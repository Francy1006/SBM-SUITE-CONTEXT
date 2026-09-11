from pathlib import Path
import hashlib,json,yaml
from jsonschema import Draft202012Validator
from .errors import invalid, blocked
from .checksum import sha256_file, read_checksums
from .permissions import validate_permissions
from .hierarchy import validate_hierarchy
from .relationships import validate_relationships
from .lineage import validate_lineage
from .context import validate_context
from .runtime import validate_runtime
PROHIBITED=['__pycache__','.pytest_cache','.DS_Store','Thumbs.db','node_modules','.git','build','dist','context','.sbm','coverage']

def load_struct(path):
    p=Path(path)
    if not p.is_file(): invalid('INSTANCE_INVALID','Required artifact missing',path=str(p))
    txt=p.read_text(encoding='utf-8'); return json.loads(txt) if p.suffix=='.json' else yaml.safe_load(txt)

def validate_schema(instance,schema,path=''):
    errs=sorted(Draft202012Validator(schema).iter_errors(instance),key=lambda e:list(e.path))
    if errs: invalid('INSTANCE_INVALID',errs[0].message,path=path)

def validate_factory_config(root):
    root=Path(root); inst=load_struct(root/'config/FACTORY_CONFIG.yaml'); sch=load_struct(root/'schemas/FACTORY_CONFIG.schema.yaml'); validate_schema(inst,sch,'config/FACTORY_CONFIG.yaml'); return inst

def clean_files(root):
    for p in Path(root).rglob('*'):
        rel=p.relative_to(root).as_posix(); parts=rel.split('/')
        if any(x in parts for x in PROHIBITED) or p.suffix in ('.pyc','.pyo') or p.name.endswith(('.tmp','.temp','.log')): invalid('PROHIBITED_ARTIFACT','Prohibited artifact',path=rel)
    return True

def validate_manifest_checksums(root):
    root=Path(root); man=load_struct(root/'MANIFEST.yaml'); mf={x['path']:x for x in man['files']}; phys=sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file())
    if set(mf)!=set(phys): invalid('EXTRA_FILE','Manifest/physical mismatch',details={'physical':len(phys),'manifest':len(mf)})
    sums=read_checksums(root/'CHECKSUMS.sha256'); expected=set(phys)-{'CHECKSUMS.sha256'}
    if set(sums)!=expected: invalid('INSTANCE_INVALID','Checksum coverage mismatch')
    for rel,h in sums.items():
        if sha256_file(root/rel)!=h: invalid('INSTANCE_INVALID','Checksum mismatch',path=rel)
        mh=mf[rel].get('sha256')
        if rel=='MANIFEST.yaml':
            if mh is not None: invalid('INSTANCE_INVALID','MANIFEST self hash must be null')
        elif mh != h: invalid('INSTANCE_INVALID','Manifest hash mismatch',path=rel)
    if mf['CHECKSUMS.sha256'].get('sha256') is not None: invalid('INSTANCE_INVALID','CHECKSUMS self hash must be null')
    return True

def _component_map(root):
    paths={'AGENT_DEFINITION':'AGENT_DEFINITION.yaml','AGENT_CONTEXT':'AGENT_CONTEXT.yaml','CONTEXT_CONTRACT':'config/CONTEXT_CONTRACT.yaml','RUNTIME_PROFILE':'config/RUNTIME_PROFILE.yaml','CLONE_LINEAGE':'config/CLONE_LINEAGE.yaml','PERMISSIONS':'config/PERMISSIONS.yaml','HIERARCHY':'config/HIERARCHY.yaml','RELATIONSHIPS':'config/RELATIONSHIPS.yaml'}
    if (Path(root)/'deployment/DEPLOYMENT_PROFILE.yaml').is_file(): paths['DEPLOYMENT_PROFILE']='deployment/DEPLOYMENT_PROFILE.yaml'
    return {k:load_struct(Path(root)/v) for k,v in paths.items()}

def _artifact_identity(name,obj):
    maps={'AGENT_DEFINITION':('agent_definition_id','agent_definition_version'),'AGENT_CONTEXT':('agent_id','context_version'),'CONTEXT_CONTRACT':('context_contract_id','context_contract_version'),'RUNTIME_PROFILE':('runtime_profile_id','runtime_profile_version'),'CLONE_LINEAGE':('clone_lineage_id','agent_version'),'PERMISSIONS':('permissions_id','permissions_version'),'HIERARCHY':('agent_id','hierarchy_version'),'RELATIONSHIPS':('relationships_id','relationships_version'),'DEPLOYMENT_PROFILE':('deployment_profile_id','deployment_profile_version')}
    a,v=maps[name]; return str(obj.get(a)),str(obj.get(v))

def validate_agent_workspace(root,template_contract=None,verify_integrity=True):
    root=Path(root); clean_files(root)
    required=['AGENT_PROPOSAL.yaml','AGENT_SPEC.yaml','AGENT_DEFINITION.yaml','AGENT_CONTEXT.yaml','approvals/PROPOSAL_APPROVAL.yaml','approvals/SPEC_APPROVAL.yaml','approvals/MATERIALIZATION_APPROVAL.yaml','config/CONTEXT_CONTRACT.yaml','config/RUNTIME_PROFILE.yaml','config/CLONE_LINEAGE.yaml','config/PERMISSIONS.yaml','config/HIERARCHY.yaml','config/RELATIONSHIPS.yaml']
    for rel in required:
        if not (root/rel).is_file(): invalid('INSTANCE_INVALID','Agent artifact missing',path=rel)
    proposal=load_struct(root/'AGENT_PROPOSAL.yaml'); spec=load_struct(root/'AGENT_SPEC.yaml'); comps=_component_map(root)
    approvals={'proposal':load_struct(root/'approvals/PROPOSAL_APPROVAL.yaml'),'spec':load_struct(root/'approvals/SPEC_APPROVAL.yaml'),'materialization':load_struct(root/'approvals/MATERIALIZATION_APPROVAL.yaml')}
    if template_contract or (root/'schemas').is_dir():
        schema_names={'AGENT_PROPOSAL':'AGENT_PROPOSAL.schema.yaml','AGENT_SPEC':'AGENT_SPEC.schema.yaml','AGENT_DEFINITION':'AGENT_DEFINITION.schema.yaml','AGENT_CONTEXT':'AGENT_CONTEXT.schema.yaml','APPROVAL_RECORD':'APPROVAL_RECORD.schema.yaml','CONTEXT_CONTRACT':'CONTEXT_CONTRACT.schema.yaml','RUNTIME_PROFILE':'RUNTIME_PROFILE.schema.yaml','CLONE_LINEAGE':'CLONE_LINEAGE.schema.yaml','PERMISSIONS':'PERMISSIONS.schema.yaml','HIERARCHY':'HIERARCHY.schema.yaml','RELATIONSHIPS':'RELATIONSHIPS.schema.yaml','DEPLOYMENT_PROFILE':'DEPLOYMENT_PROFILE.schema.yaml'}
        def sch(n): return load_struct((template_contract.root if template_contract else root)/'schemas'/schema_names[n])
        validate_schema(proposal,sch('AGENT_PROPOSAL'),'AGENT_PROPOSAL.yaml'); validate_schema(spec,sch('AGENT_SPEC'),'AGENT_SPEC.yaml')
        for n,o in comps.items(): validate_schema(o,sch(n),n)
        for n,o in approvals.items(): validate_schema(o,sch('APPROVAL_RECORD'),f'approvals/{n}')
    aid=spec['agent_id']; av=str(spec['agent_version'])
    if proposal.get('proposal_id')!=(spec.get('proposal_reference') or {}).get('proposal_id') or str(proposal.get('proposal_version'))!=str((spec.get('proposal_reference') or {}).get('proposal_version')): invalid('CROSS_REFERENCE_MISMATCH','proposal_reference mismatch')
    for n,o in comps.items():
        if o.get('agent_id') not in (None,aid): invalid('CROSS_REFERENCE_MISMATCH',f'{n} agent_id mismatch')
    refs=spec.get('component_references') or {}
    for n,o in comps.items():
        if n not in refs: invalid('CROSS_REFERENCE_MISMATCH',f'Missing component reference {n}')
        oid,over=_artifact_identity(n,o); ref=refs[n]
        if str(ref.get('artifact_id'))!=oid or str(ref.get('artifact_version'))!=over: invalid('CROSS_REFERENCE_MISMATCH',f'{n} reference/version mismatch')
    if approvals['proposal'].get('artifact_id')!=proposal['proposal_id'] or str(approvals['proposal'].get('artifact_version'))!=str(proposal['proposal_version']): blocked('APPROVAL_MISMATCH','Proposal approval mismatch')
    if approvals['spec'].get('artifact_id')!=spec['spec_id'] or str(approvals['spec'].get('artifact_version'))!=str(spec['spec_version']): blocked('APPROVAL_MISMATCH','Spec approval mismatch')
    ar=spec.get('approval_reference') or {}
    if ar.get('approval_id')!=approvals['spec'].get('approval_id') or str(ar.get('artifact_version'))!=str(approvals['spec'].get('artifact_version')): blocked('APPROVAL_MISMATCH','approval_reference mismatch')
    if approvals['materialization'].get('artifact_id')!=spec['spec_id'] or str(approvals['materialization'].get('artifact_version'))!=str(spec['spec_version']): blocked('APPROVAL_MISMATCH','Materialization approval must target exact spec')
    validate_permissions(comps['AGENT_DEFINITION'],comps['PERMISSIONS']); validate_hierarchy(comps['HIERARCHY']); validate_relationships(comps['RELATIONSHIPS'])
    if not validate_context(comps['AGENT_CONTEXT'],comps['CONTEXT_CONTRACT']): invalid('CROSS_REFERENCE_MISMATCH','Context contracts incompatible')
    if not validate_runtime(comps['RUNTIME_PROFILE']): invalid('INSTANCE_INVALID','Runtime invalid')
    validate_lineage(spec,comps['CLONE_LINEAGE'])
    if template_contract is not None:
        from .template_engine import TemplateEngine
        TemplateEngine().verify_output(root,template_contract,include_integrity=verify_integrity)
    dep=spec.get('deployment_reference')
    if bool(dep) != ('DEPLOYMENT_PROFILE' in comps): invalid('CROSS_REFERENCE_MISMATCH','Deployment reference/profile mismatch')
    if dep:
        did,dver=_artifact_identity('DEPLOYMENT_PROFILE',comps['DEPLOYMENT_PROFILE'])
        if str(dep.get('artifact_id'))!=did or str(dep.get('artifact_version'))!=dver: invalid('CROSS_REFERENCE_MISMATCH','deployment_reference mismatch')
    if verify_integrity and (root/'MANIFEST.yaml').is_file() and (root/'CHECKSUMS.sha256').is_file(): validate_manifest_checksums(root)
    return sha256_tree(root)

def validate_factory_package(root):
    root=Path(root); validate_factory_config(root); clean_files(root); validate_manifest_checksums(root); return sha256_tree(root)

def validate_workspace(root,template_contract=None):
    root=Path(root)
    return validate_factory_package(root) if (root/'config/FACTORY_CONFIG.yaml').is_file() else validate_agent_workspace(root,template_contract=template_contract)

def sha256_tree(root):
    h=hashlib.sha256()
    for p in sorted(Path(root).rglob('*')):
        if p.is_file(): h.update(p.relative_to(root).as_posix().encode()); h.update(b'\0'); h.update(p.read_bytes()); h.update(b'\0')
    return h.hexdigest()
