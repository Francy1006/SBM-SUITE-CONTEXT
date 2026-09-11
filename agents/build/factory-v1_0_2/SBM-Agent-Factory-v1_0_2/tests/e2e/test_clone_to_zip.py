from pathlib import Path
import sys,yaml
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_2' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.qa import write_fixture_bundle,canonical_template_path,render_fixture_agent
from sbm_agent_factory.create import create_agent
from sbm_agent_factory.clone import clone_agent
CFG=yaml.safe_load((ROOT/'config/FACTORY_CONFIG.yaml').read_text()); TEMPLATE=canonical_template_path()
def args(b): return [b['proposal'],b['proposal_approval'],b['spec'],b['spec_approval'],b['materialization_approval']]
def test_clone_to_zip(tmp_path):
 pb=write_fixture_bundle(tmp_path/'parent_inputs',TEMPLATE,agent_id='Parent',agent_version='1.0.0'); parent=render_fixture_agent(pb,TEMPLATE,tmp_path/'parent',CFG); from sbm_agent_factory.validate import validate_agent_workspace; assert validate_agent_workspace(parent)
 ps=yaml.safe_load(pb['spec'].read_text()); tb=write_fixture_bundle(tmp_path/'target_inputs',TEMPLATE,mode='CLONE',agent_id='Child',agent_version='1.0.0',parent_spec=ps)
 r=clone_agent(*args(tb),parent,TEMPLATE,tmp_path/'child',CFG); ev=yaml.safe_load(r['evidence'].read_text())
 assert ev['agent_validate_exit_code']==0 and ev['agent_test_exit_code']==0 and r['zip'].is_file()
