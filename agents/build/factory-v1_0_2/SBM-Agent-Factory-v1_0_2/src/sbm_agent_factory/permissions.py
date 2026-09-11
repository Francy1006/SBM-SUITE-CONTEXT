from .errors import blocked

def validate_permissions(definition,permissions):
    a=set(permissions.get('allowed_actions',[])); d=set(permissions.get('denied_actions',[]))
    if a & d: blocked('PERMISSION_CONFLICT','Allowed and denied actions overlap',details={'overlap':sorted(a&d)})
    authority=set(definition.get('authority',[]))
    if not a.issubset(authority): blocked('PERMISSION_CONFLICT','Allowed actions exceed authority',details={'excess':sorted(a-authority)})
    return True
