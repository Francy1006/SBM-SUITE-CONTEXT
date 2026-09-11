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
from sbm_agent_factory.reproducibility import rebuild_from_extracted
from zipfile import ZipFile
def test_rebuild_same_sha(tmp_path):
    b=write_fixture_bundle(tmp_path/'inputs',TEMPLATE,agent_id='Rebuild',agent_version='1.0.0'); r=create_agent(*args(b),TEMPLATE,tmp_path/'build'/'Rebuild',CFG)
    ex=tmp_path/'ex'; ZipFile(r['zip']).extractall(ex); rebuilt=tmp_path/'rebuilt.zip'; sha=rebuild_from_extracted(ex/'Rebuild',rebuilt,arc_root='Rebuild',compresslevel=6)
    assert sha==r['sha256']==sha256_file(r['zip'])
