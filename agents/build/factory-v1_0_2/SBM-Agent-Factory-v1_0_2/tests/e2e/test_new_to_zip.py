from pathlib import Path
import sys,os,yaml,subprocess
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_2' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.qa import write_fixture_bundle,canonical_template_path
from sbm_agent_factory.create import create_agent
from sbm_agent_factory.validate import validate_agent_workspace
CFG=yaml.safe_load((ROOT/'config/FACTORY_CONFIG.yaml').read_text()); TEMPLATE=canonical_template_path()
def args(b): return [b['proposal'],b['proposal_approval'],b['spec'],b['spec_approval'],b['materialization_approval']]
def test_new_to_zip(tmp_path):
 b=write_fixture_bundle(tmp_path/'inputs',TEMPLATE,agent_id='RealNew',agent_version='1.0.0')
 r=create_agent(*args(b),TEMPLATE,tmp_path/'build'/'RealNew',CFG)
 ev=yaml.safe_load(r['evidence'].read_text())
 assert ev['agent_validate_exit_code']==0 and ev['agent_test_exit_code']==0 and ev['qa_result']=='PASS'
 assert r['zip'].is_file() and validate_agent_workspace(r['workspace'])
 assert (r['workspace']/'AGENT_DEFINITION.yaml').is_file() and (r['workspace']/'tests/test_instance_validation.py').is_file()
