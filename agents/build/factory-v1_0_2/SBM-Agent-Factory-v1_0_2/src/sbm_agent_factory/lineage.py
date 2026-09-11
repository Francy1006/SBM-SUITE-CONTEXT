from .errors import invalid

def validate_lineage(spec,lineage):
    mode=spec.get('creation_mode'); mig=spec.get('migration_reference'); parent=spec.get('parent_reference')
    parent_keys=['parent_agent_id','parent_agent_version','parent_spec_id','parent_spec_version']
    if mode=='CLONE':
        if mig is not None: invalid('LINEAGE_INVALID','CLONE cannot be STANDARD_UPGRADE')
        if not isinstance(parent,dict) or not lineage.get('is_clone') or not all(lineage.get(k) for k in parent_keys): invalid('LINEAGE_INVALID','CLONE requires exact parent lineage')
        expected=[parent.get('agent_id'),parent.get('agent_version'),parent.get('spec_id'),parent.get('spec_version')]
        if [lineage.get(k) for k in parent_keys] != expected: invalid('LINEAGE_INVALID','CLONE lineage does not match parent_reference')
    elif mode=='NEW':
        if parent is not None or lineage.get('is_clone') or any(lineage.get(k) is not None for k in parent_keys): invalid('LINEAGE_INVALID','NEW must not have parent lineage')
        if mig is not None:
            if mig.get('migration_type')!='STANDARD_UPGRADE' or mig.get('source_agent_id')!=spec.get('agent_id') or str(mig.get('source_agent_version'))==str(spec.get('agent_version')) or str(mig.get('source_standard_version'))==str(spec.get('standard_version')):
                invalid('STANDARD_UPGRADE_INVALID','Invalid STANDARD_UPGRADE invariants')
    else: invalid('LINEAGE_INVALID','Unsupported creation_mode')
    return True
