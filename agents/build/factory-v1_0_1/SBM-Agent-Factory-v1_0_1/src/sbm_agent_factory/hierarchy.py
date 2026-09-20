from .errors import invalid

def validate_hierarchy(h):
    required=['agent_id','hierarchy_version','reports_to','can_request_from','can_instruct','requires_approval_from','escalation_target']
    if any(k not in h for k in required): invalid('HIERARCHY_INVALID','Hierarchy incomplete')
    if h['agent_id'] in (h.get('can_instruct') or []): invalid('HIERARCHY_INVALID','Agent cannot instruct itself')
    return True
