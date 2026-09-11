from pathlib import Path
import sys
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_1' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.clone import computed_delta,validate_delta
def test_clone_computed_delta_real_contracts():
 p={'AGENT_DEFINITION':{'x':1},'PERMISSIONS':{'allowed_actions':['a']}}; t={'AGENT_DEFINITION':{'x':2},'PERMISSIONS':{'allowed_actions':['a']}}
 d=computed_delta(p,t); assert set(d)=={'AGENT_DEFINITION'}
 validate_delta(d,{'component_references':{'AGENT_DEFINITION':{'artifact_id':'D','artifact_version':'1'}}},t)
