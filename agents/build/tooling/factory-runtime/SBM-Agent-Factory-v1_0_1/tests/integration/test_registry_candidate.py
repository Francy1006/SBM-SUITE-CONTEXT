from pathlib import Path
import sys
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_1' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.registry import make_candidate,write_candidate
import yaml
def test_registry_candidate_generated_not_registry(tmp_path):
 z=tmp_path/'A.zip'; z.write_bytes(b'x')
 cfg={'factory_id':'SBM-Agent-Factory','factory_version':'1.0.1','template_id':'SBM-Agent-Template','canonical_template_sha256':'f8f3901d23720d34e617a48f7a26956c34afe8fba73fc807eaaa6736323dd663'}
 c=make_candidate({'agent_id':'A','agent_name':'A','description':'d','agent_version':'1.0.0','spec_version':'1.0.0','standard_version':'2.0.0','template_version':'2.0.1'},z,'abc',cfg)
 p=tmp_path/'candidate.yaml'; write_candidate(p,c); written=yaml.safe_load(p.read_text())
 assert p.is_file() and not (tmp_path/'context/agents').exists()
 assert written['factory_version']=='1.0.1' and written['template_version']=='2.0.1'
 assert written['template_sha256']==cfg['canonical_template_sha256'] and written['package_sha256']=='abc'
