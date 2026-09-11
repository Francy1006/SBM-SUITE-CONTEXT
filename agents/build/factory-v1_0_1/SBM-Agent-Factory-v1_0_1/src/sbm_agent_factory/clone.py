from pathlib import Path
import yaml
from .create import materialize,load_target_components,COMPONENT_PATHS
from .validate import validate_agent_workspace
from .errors import blocked,invalid

def _load(p): return yaml.safe_load(Path(p).read_text(encoding='utf-8'))
def resolved_contracts(root):
    root=Path(root); out={}
    for name,rel in COMPONENT_PATHS.items():
        p=root/rel
        if p.is_file(): out[name]=_load(p)
    return out

def computed_delta(parent_contracts,target_contracts):
    names=['AGENT_DEFINITION','AGENT_CONTEXT','CONTEXT_CONTRACT','RUNTIME_PROFILE','PERMISSIONS','HIERARCHY','RELATIONSHIPS','DEPLOYMENT_PROFILE']
    return {k:{'parent':parent_contracts.get(k),'target':target_contracts.get(k)} for k in names if parent_contracts.get(k)!=target_contracts.get(k)}

def validate_delta(delta,target_spec,target_contracts):
    refs=target_spec.get('component_references') or {}
    bad=[]
    for name,item in delta.items():
        if name not in refs or item['target'] is None: bad.append(name)
    if bad: blocked('UNAPPROVED_DELTA','Computed delta contains change outside approved target component references',details={'components':sorted(bad)})
    return True

def clone_agent(proposal,proposal_approval,spec,spec_approval,materialization_approval,parent,template,output_dir,config):
    parent=Path(parent)
    if not (parent/'AGENT_SPEC.yaml').is_file(): invalid('LINEAGE_INVALID','Exact parent AGENT_SPEC missing',path=str(parent))
    parent_spec=_load(parent/'AGENT_SPEC.yaml'); target_spec=_load(spec)
    pref=target_spec.get('parent_reference') or {}
    expected={'agent_id':parent_spec.get('agent_id'),'agent_version':parent_spec.get('agent_version'),'spec_id':parent_spec.get('spec_id'),'spec_version':parent_spec.get('spec_version')}
    if pref != expected: blocked('UNAPPROVED_DELTA','Target parent_reference does not match exact parent')
    pc=resolved_contracts(parent); tc=load_target_components(spec,target_spec); delta=computed_delta(pc,tc); validate_delta(delta,target_spec,tc)
    result=materialize(proposal,proposal_approval,spec,spec_approval,materialization_approval,template,output_dir,config,mode='CLONE',parent=parent)
    rendered=resolved_contracts(result['workspace']); post_delta=computed_delta(pc,rendered)
    if set(post_delta)!=set(delta):
        try: result['zip'].unlink(missing_ok=True)
        except Exception: pass
        blocked('UNAPPROVED_DELTA','Rendered target differs from approved resolved target contracts')
    return result
