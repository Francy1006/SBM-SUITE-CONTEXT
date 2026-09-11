import yaml
from pathlib import Path
from .errors import blocked

def load_yaml(p): return yaml.safe_load(Path(p).read_text(encoding='utf-8'))
def validate_approval(path, approval_type, artifact_id, artifact_version):
    a=load_yaml(path)
    ok=(a.get('approval_type')==approval_type and a.get('artifact_id')==artifact_id and str(a.get('artifact_version'))==str(artifact_version) and a.get('approval_status')=='APPROVED' and a.get('approved_by')=='sbm-admin')
    if not ok: blocked('APPROVAL_MISMATCH','Approval does not match artifact',path=str(path),details={'expected_artifact_id':artifact_id,'expected_artifact_version':artifact_version})
    return a

def validate_gate(proposal,proposal_approval,spec,spec_approval,materialization_approval):
    p=load_yaml(proposal); s=load_yaml(spec)
    if p.get('review_status')!='APPROVED': blocked('PROPOSAL_NOT_APPROVED','Proposal is not APPROVED',path=str(proposal))
    pa=validate_approval(proposal_approval,'AGENT_PROPOSAL',p['proposal_id'],p['proposal_version'])
    sa=validate_approval(spec_approval,'AGENT_SPEC',s['spec_id'],s['spec_version'])
    ma=validate_approval(materialization_approval,'MATERIALIZATION',s['spec_id'],s['spec_version'])
    return p,s,{'proposal':pa,'spec':sa,'materialization':ma}
