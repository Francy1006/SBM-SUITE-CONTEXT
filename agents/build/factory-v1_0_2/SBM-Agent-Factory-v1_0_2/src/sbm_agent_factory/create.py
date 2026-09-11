from __future__ import annotations
from pathlib import Path
import json,yaml
from .approvals import validate_gate
from .template_engine import TemplateEngine
from .errors import invalid, blocked
from .lineage import validate_lineage
from .validate import validate_agent_workspace
from .manifest import write_manifest
from .checksum import write_checksums
from .package import package_workspace
from .registry import make_candidate,write_candidate
from .documentation import generate_docs
from .qa import run_agent_qa

COMPONENT_PATHS={'AGENT_DEFINITION':'AGENT_DEFINITION.yaml','AGENT_CONTEXT':'AGENT_CONTEXT.yaml','CONTEXT_CONTRACT':'config/CONTEXT_CONTRACT.yaml','RUNTIME_PROFILE':'config/RUNTIME_PROFILE.yaml','CLONE_LINEAGE':'config/CLONE_LINEAGE.yaml','PERMISSIONS':'config/PERMISSIONS.yaml','HIERARCHY':'config/HIERARCHY.yaml','RELATIONSHIPS':'config/RELATIONSHIPS.yaml','DEPLOYMENT_PROFILE':'deployment/DEPLOYMENT_PROFILE.yaml'}

def _load(path): return yaml.safe_load(Path(path).read_text(encoding='utf-8'))
def _find_component(bundle_root,name):
    rel=COMPONENT_PATHS[name]; candidates=[Path(bundle_root)/rel,Path(bundle_root)/Path(rel).name]
    for p in candidates:
        if p.is_file(): return _load(p)
    invalid('INSTANCE_INVALID',f'Missing approved target component {name}',path=rel)

def load_target_components(spec_path,spec):
    root=Path(spec_path).parent; out={}
    for name in ['AGENT_DEFINITION','AGENT_CONTEXT','CONTEXT_CONTRACT','RUNTIME_PROFILE','CLONE_LINEAGE','PERMISSIONS','HIERARCHY','RELATIONSHIPS']:
        out[name]=_find_component(root,name)
    if spec.get('deployment_reference') is not None: out['DEPLOYMENT_PROFILE']=_find_component(root,'DEPLOYMENT_PROFILE')
    return out

def _write_integrity(root):
    # seed placeholders so both are inventoried, then converge deterministically
    root=Path(root); (root/'MANIFEST.yaml').write_text('files: []\n',encoding='utf-8'); (root/'CHECKSUMS.sha256').write_text('',encoding='utf-8')
    write_manifest(root); write_checksums(root); write_manifest(root); write_checksums(root)

def _artifact_name(spec): return f"{spec['agent_id']}-v{str(spec['agent_version']).replace('.','_')}.zip"

def materialize(proposal_path,proposal_approval_path,spec_path,spec_approval_path,materialization_approval_path,template_path,output_dir,config,mode='NEW',parent=None):
    proposal,spec,approvals=validate_gate(proposal_path,proposal_approval_path,spec_path,spec_approval_path,materialization_approval_path)
    engine=TemplateEngine(); contract=engine.resolve(config['template_id'],config['template_version'],template_path,config['canonical_template_sha256'])
    try:
        comps=load_target_components(spec_path,spec)
        engine.validate_inputs(contract,proposal,spec,approvals,comps)
        if mode=='NEW' and spec.get('creation_mode')!='NEW': invalid('LINEAGE_INVALID','create only accepts NEW including STANDARD_UPGRADE')
        if mode=='CLONE' and spec.get('creation_mode')!='CLONE': invalid('LINEAGE_INVALID','clone requires CLONE')
        validate_lineage(spec,comps['CLONE_LINEAGE'])
        out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
        if any(out.iterdir()): invalid('EXTRA_FILE','Output workspace must be empty',path=str(out))
        engine.render(contract,{'proposal':proposal,'spec':spec,'components':comps,'approvals':approvals},out)
        engine.verify_output(out,contract)
        # docs required by pipeline but only README is canonical package content in Template; registry/version docs stay derived outside agent package
        _write_integrity(out)
        validate_agent_workspace(out,template_contract=contract,verify_integrity=True)
        qa=run_agent_qa(out)
        if qa['agent_validate_exit_code'] != 0 or qa['agent_test_exit_code'] != 0:
            blocked('INSTANCE_INVALID','Generated agent QA failed; package not generated',details=qa)
        # package command revalidates current state and reruns current agent QA atomically
        dist=out.parent/'dist'; dist.mkdir(parents=True,exist_ok=True); zip_path=dist/_artifact_name(spec)
        sha=package_workspace(out,zip_path,validated_snapshot=None,arc_root=spec['agent_id'],compresslevel=config['zip_compresslevel'],template_contract=contract)
        candidate=make_candidate({**spec,'agent_name':proposal.get('agent_name'),'description':proposal.get('agent_description')},zip_path,sha,config)
        cand_path=out.parent/'REGISTRY_CANDIDATE.yaml'; write_candidate(cand_path,candidate)
        evidence={'execution_id':f"{spec['agent_id']}-{spec['agent_version']}",'factory_id':config['factory_id'],'factory_version':config['factory_version'],'command':'clone' if mode=='CLONE' else 'create','status':'SUCCEEDED','input_references':[str(proposal_path),str(spec_path)],'proposal_reference':spec['proposal_reference'],'spec_reference':{'spec_id':spec['spec_id'],'spec_version':spec['spec_version']},'approval_references':[approvals[k]['approval_id'] for k in ('proposal','spec','materialization')],'template_id':config['template_id'],'template_version':config['template_version'],'template_sha256':config['canonical_template_sha256'],'validation_result':qa['validation_result'],'qa_result':qa['qa_result'],'agent_validate_exit_code':qa['agent_validate_exit_code'],'agent_test_exit_code':qa['agent_test_exit_code'],'package_path':str(zip_path),'package_sha256':sha,'registry_candidate_path':str(cand_path),'started_at':'1980-01-01T00:00:00Z','completed_at':'1980-01-01T00:00:00Z','errors':[]}
        ev_path=out.parent/'EXECUTION_EVIDENCE.yaml'; ev_path.write_text(yaml.safe_dump(evidence,sort_keys=False),encoding='utf-8',newline='\n')
        return {'workspace':out,'zip':zip_path,'sha256':sha,'registry_candidate':cand_path,'evidence':ev_path,'contract':contract}
    finally:
        contract.close()

def create_agent(proposal,proposal_approval,spec,spec_approval,materialization_approval,template,output_dir,config):
    return materialize(proposal,proposal_approval,spec,spec_approval,materialization_approval,template,output_dir,config,mode='NEW')
