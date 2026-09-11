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

from sbm_agent_factory.template_engine import TemplateEngine
def test_reject_known_noncanonical_hash():
    try: TemplateEngine().resolve('SBM-Agent-Template','2.0.1',TEMPLATE,'ffeff9850e983d07137dd0bef0b21966aa61bdb8d3e6d228285e4f0170bc7513'); assert False
    except FactoryError as e: assert e.code=='TEMPLATE_SHA_MISMATCH' and e.status=='BLOCKED'
def test_accept_canonical_hash():
    c=TemplateEngine().resolve('SBM-Agent-Template','2.0.1',TEMPLATE,'f8f3901d23720d34e617a48f7a26956c34afe8fba73fc807eaaa6736323dd663'); assert c.metadata['template_version']=='2.0.1'; c.close()


def test_package_cli_requires_template_argument(tmp_path):
    from sbm_agent_factory.cli import main
    try:
        main(['package','--root',str(tmp_path/'agent'),'--output',str(tmp_path/'x.zip')])
        assert False
    except SystemExit as e:
        assert e.code==2 and not (tmp_path/'x.zip').exists()

def test_package_cli_rejects_noncanonical_template_bytes(tmp_path):
    from sbm_agent_factory.cli import main
    bad=tmp_path/'bad-template.zip'; bad.write_bytes(TEMPLATE.read_bytes()+b'X')
    rc=main(['package','--root',str(tmp_path/'agent'),'--template',str(bad),'--output',str(tmp_path/'x.zip')])
    assert rc==3 and not (tmp_path/'x.zip').exists()
