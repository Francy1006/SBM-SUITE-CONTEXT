from pathlib import Path
import sys,yaml,shutil
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_2' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.qa import write_fixture_bundle,canonical_template_path,run_agent_qa,render_fixture_agent
from sbm_agent_factory.package import package_workspace
from sbm_agent_factory.manifest import write_manifest
from sbm_agent_factory.checksum import write_checksums
from sbm_agent_factory.errors import FactoryError
from sbm_agent_factory.template_engine import TemplateEngine
CFG=yaml.safe_load((ROOT/'config/FACTORY_CONFIG.yaml').read_text()); TEMPLATE=canonical_template_path()
def refresh(root):
 write_manifest(root); write_checksums(root); write_manifest(root); write_checksums(root)
def contract(): return TemplateEngine().resolve(CFG['template_id'],CFG['template_version'],TEMPLATE,CFG['canonical_template_sha256'])
def package_fails(root,out):
 c=contract()
 try:
  try: package_workspace(root,out,arc_root='MutationBase',template_contract=c); assert False
  except FactoryError as e: assert not out.exists(); return e
 finally: c.close()
def test_mutation_and_real_qa_failures_block_package(tmp_path):
 b=write_fixture_bundle(tmp_path/'i',TEMPLATE,agent_id='MutationBase'); base=render_fixture_agent(b,TEMPLATE,tmp_path/'base',CFG); assert run_agent_qa(base)['qa_result']=='PASS'
 a=tmp_path/'spec_mut'; shutil.copytree(base,a); d=yaml.safe_load((a/'AGENT_DEFINITION.yaml').read_text()); d['agent_id']='DifferentAgent'; (a/'AGENT_DEFINITION.yaml').write_text(yaml.safe_dump(d,sort_keys=False)); refresh(a); package_fails(a,tmp_path/'spec.zip')
 qroot=tmp_path/'qa_mut'; shutil.copytree(base,qroot); (qroot/'tests/test_instance_validation.py').write_text('def test_forced_failure():\n    assert False, "physical agent QA failure"\n'); refresh(qroot); e=package_fails(qroot,tmp_path/'qa.zip'); assert e.details['agent_validate_exit_code']==0 and e.details['agent_test_exit_code']!=0 and e.details['qa_result']!='PASS'
 vroot=tmp_path/'val_mut'; shutil.copytree(base,vroot); d=yaml.safe_load((vroot/'AGENT_DEFINITION.yaml').read_text()); d['agent_id']=12345; (vroot/'AGENT_DEFINITION.yaml').write_text(yaml.safe_dump(d,sort_keys=False)); refresh(vroot); v=run_agent_qa(vroot); assert v['agent_validate_exit_code']!=0 and v['qa_result']!='PASS'
