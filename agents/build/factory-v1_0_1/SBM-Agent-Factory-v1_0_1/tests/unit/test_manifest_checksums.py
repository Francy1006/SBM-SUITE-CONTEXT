from pathlib import Path
import sys
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_1' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.manifest import write_manifest
from sbm_agent_factory.checksum import write_checksums
from sbm_agent_factory.validate import validate_manifest_checksums
def test_manifest_checksums_agent(tmp_path):
 (tmp_path/'a.txt').write_text('a'); (tmp_path/'MANIFEST.yaml').write_text('files: []\n'); (tmp_path/'CHECKSUMS.sha256').write_text(''); write_manifest(tmp_path); write_checksums(tmp_path); write_manifest(tmp_path); write_checksums(tmp_path); assert validate_manifest_checksums(tmp_path)
