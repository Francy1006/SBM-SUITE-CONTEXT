from .errors import invalid

def validate_relationships(r):
    for rel in r.get('relationships',[]):
        if not all(rel.get(k) for k in ['actor','relationship_type','direction','purpose']): invalid('RELATIONSHIP_INVALID','Relationship incomplete')
    return True
