from pathlib import Path
import sys,yaml
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_1' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.qa import write_fixture_bundle,canonical_template_path
from sbm_agent_factory.approvals import validate_gate
from sbm_agent_factory.create import load_target_components
from sbm_agent_factory.template_engine import TemplateEngine
from sbm_agent_factory.checksum import sha256_file
TEMPLATE=canonical_template_path()
def test_create_render_full_agent(tmp_path):
 b=write_fixture_bundle(tmp_path/'i',TEMPLATE,agent_id='CreateFull'); p,s,a=validate_gate(b['proposal'],b['proposal_approval'],b['spec'],b['spec_approval'],b['materialization_approval']); c=TemplateEngine().resolve('SBM-Agent-Template','2.0.1',TEMPLATE,sha256_file(TEMPLATE))
 try:
  out=tmp_path/'agent'; comps=load_target_components(b['spec'],s); TemplateEngine().render(c,{'proposal':p,'spec':s,'components':comps,'approvals':a},out); TemplateEngine().verify_output(out,c)
  assert (out/'scripts/validate').is_file() and (out/'scripts/test').is_file()
 finally: c.close()
