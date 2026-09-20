from pathlib import Path
import sys, os, yaml, shutil
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_2' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.qa import write_fixture_bundle, canonical_template_path
from sbm_agent_factory.checksum import sha256_file
from sbm_agent_factory.errors import FactoryError
CFG=yaml.safe_load((ROOT/'config/FACTORY_CONFIG.yaml').read_text())
TEMPLATE=canonical_template_path()

def args(b):
    return [b['proposal'],b['proposal_approval'],b['spec'],b['spec_approval'],b['materialization_approval']]

from sbm_agent_factory.relationships import validate_relationships
def test_relationship_invalid():
    try: validate_relationships({'relationships':[{'actor':'A'}]}); assert False
    except FactoryError as e: assert e.code=='RELATIONSHIP_INVALID'
