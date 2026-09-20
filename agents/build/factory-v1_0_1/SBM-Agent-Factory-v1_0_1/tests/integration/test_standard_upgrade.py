from pathlib import Path
import sys
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_1' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.lineage import validate_lineage
def test_standard_upgrade_via_create_invariants():
 s={'creation_mode':'NEW','agent_id':'U','agent_version':'2.0.0','standard_version':'2.0.0','parent_reference':None,'migration_reference':{'source_agent_id':'U','source_agent_version':'1.0.0','source_standard_version':'1.0.0','migration_type':'STANDARD_UPGRADE'}}
 l={'is_clone':False,'parent_agent_id':None,'parent_agent_version':None,'parent_spec_id':None,'parent_spec_version':None}
 assert validate_lineage(s,l)
