from pathlib import Path
import sys, os, yaml, shutil
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_1' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.qa import write_fixture_bundle, canonical_template_path
from sbm_agent_factory.checksum import sha256_file
from sbm_agent_factory.errors import FactoryError
CFG=yaml.safe_load((ROOT/'config/FACTORY_CONFIG.yaml').read_text())
TEMPLATE=canonical_template_path()

def args(b):
    return [b['proposal'],b['proposal_approval'],b['spec'],b['spec_approval'],b['materialization_approval']]

from sbm_agent_factory.lineage import validate_lineage
def test_new_lineage():
    assert validate_lineage({'creation_mode':'NEW','migration_reference':None,'parent_reference':None},{'is_clone':False,'parent_agent_id':None,'parent_agent_version':None,'parent_spec_id':None,'parent_spec_version':None})
def test_upgrade_invariants():
    assert validate_lineage({'creation_mode':'NEW','agent_id':'A','agent_version':'2','standard_version':'2','parent_reference':None,'migration_reference':{'migration_type':'STANDARD_UPGRADE','source_agent_id':'A','source_agent_version':'1','source_standard_version':'1'}},{'is_clone':False,'parent_agent_id':None,'parent_agent_version':None,'parent_spec_id':None,'parent_spec_version':None})
