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

from sbm_agent_factory.create import create_agent
def test_materialization_wrong_spec_blocked(tmp_path):
    b=write_fixture_bundle(tmp_path/'i',TEMPLATE,agent_id='A'); m=yaml.safe_load(b['materialization_approval'].read_text()); m['artifact_id']='SPEC-OTHER'; b['materialization_approval'].write_text(yaml.safe_dump(m,sort_keys=False))
    try: create_agent(*args(b),TEMPLATE,tmp_path/'o',CFG); assert False
    except FactoryError as e: assert e.code=='APPROVAL_MISMATCH' and e.status=='BLOCKED'
