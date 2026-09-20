from pathlib import Path
import sys,yaml
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_1' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.qa import write_fixture_bundle,canonical_template_path
from sbm_agent_factory.create import create_agent
CFG=yaml.safe_load((ROOT/'config/FACTORY_CONFIG.yaml').read_text()); TEMPLATE=canonical_template_path()
def args(b): return [b['proposal'],b['proposal_approval'],b['spec'],b['spec_approval'],b['materialization_approval']]
def test_upgrade_to_zip(tmp_path):
 mig={'source_agent_id':'UpgradeAgent','source_agent_version':'1.0.0','source_standard_version':'1.0.0','migration_type':'STANDARD_UPGRADE'}
 b=write_fixture_bundle(tmp_path/'i',TEMPLATE,agent_id='UpgradeAgent',agent_version='2.0.0',migration=mig)
 r=create_agent(*args(b),TEMPLATE,tmp_path/'build'/'UpgradeAgent',CFG); ev=yaml.safe_load(r['evidence'].read_text())
 s=yaml.safe_load((r['workspace']/'AGENT_SPEC.yaml').read_text()); l=yaml.safe_load((r['workspace']/'config/CLONE_LINEAGE.yaml').read_text())
 assert s['creation_mode']=='NEW' and s['parent_reference'] is None and l['is_clone'] is False
 assert ev['agent_validate_exit_code']==0 and ev['agent_test_exit_code']==0 and r['zip'].is_file()
