from pathlib import Path
import sys, yaml, shutil, pytest
ROOT=Path(__file__).resolve()
while ROOT.name!='SBM-Agent-Factory-v1_0_2' and ROOT.parent!=ROOT: ROOT=ROOT.parent
SRC=ROOT/'src'
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from sbm_agent_factory.qa import write_fixture_bundle, canonical_template_path, render_fixture_agent, run_agent_qa
from sbm_agent_factory.errors import FactoryError
from sbm_agent_factory.template_engine import TemplateEngine
from sbm_agent_factory.package import package_workspace
from sbm_agent_factory.manifest import write_manifest
from sbm_agent_factory.checksum import write_checksums
CFG=yaml.safe_load((ROOT/'config/FACTORY_CONFIG.yaml').read_text())
TEMPLATE=canonical_template_path()

def contract():
    return TemplateEngine().resolve(CFG['template_id'],CFG['template_version'],TEMPLATE,CFG['canonical_template_sha256'])

def refresh(root):
    write_manifest(root); write_checksums(root); write_manifest(root); write_checksums(root)

@pytest.fixture(scope="module")
def validated_base(tmp_path_factory):
    base=tmp_path_factory.mktemp("template-required-base")
    b=write_fixture_bundle(base/"inputs",TEMPLATE,agent_id="RequiredGate")
    agent=render_fixture_agent(b,TEMPLATE,base/"agent",CFG)
    assert run_agent_qa(agent)["qa_result"]=="PASS"
    return agent

def copy_agent(validated_base,tmp_path):
    dst=tmp_path/"agent"
    shutil.copytree(validated_base,dst)
    return dst

def package_fails(root,out):
    c=contract()
    try:
        try:
            package_workspace(root,out,arc_root=root.name,compresslevel=CFG['zip_compresslevel'],template_contract=c)
            assert False, 'package unexpectedly succeeded'
        except FactoryError as e:
            assert e.status in {'INVALID','BLOCKED'}
            assert not out.exists()
            return e
    finally:
        c.close()

def test_extra_after_validate_rejected(tmp_path,validated_base):
    workspace=copy_agent(validated_base,tmp_path)
    (workspace/'EXTRA.txt').write_text('x',encoding='utf-8')
    refresh(workspace)
    e=package_fails(workspace,tmp_path/'extra.zip')
    assert e.code=='EXTRA_FILE'

def _missing_required_case(tmp_path,validated_base,rel):
    workspace=copy_agent(validated_base,tmp_path)
    target=workspace/rel
    assert target.is_file()
    target.unlink()
    refresh(workspace)
    e=package_fails(workspace,tmp_path/'missing.zip')
    assert e.code in {'INSTANCE_INVALID','EXTRA_FILE'}
    assert 'Template-required' in e.message or 'missing' in e.message.lower()

def test_missing_readme_with_valid_integrity_blocks_package(tmp_path,validated_base):
    _missing_required_case(tmp_path,validated_base,'README.md')

def test_missing_init_with_valid_integrity_blocks_package(tmp_path,validated_base):
    _missing_required_case(tmp_path,validated_base,'INIT.md')

def test_missing_qa_matrix_with_valid_integrity_blocks_package(tmp_path,validated_base):
    _missing_required_case(tmp_path,validated_base,'qa/TEST_MATRIX.md')

def test_missing_schema_with_valid_integrity_blocks_package(tmp_path,validated_base):
    _missing_required_case(tmp_path,validated_base,'schemas/AGENT_SPEC.schema.yaml')

def test_missing_test_with_valid_integrity_blocks_package(tmp_path,validated_base):
    _missing_required_case(tmp_path,validated_base,'tests/test_instance_validation.py')

def test_package_requires_non_null_template_contract(tmp_path,validated_base):
    workspace=copy_agent(validated_base,tmp_path)
    out=tmp_path/'none.zip'
    try:
        package_workspace(workspace,out,arc_root='NoTemplateGate',template_contract=None)
        assert False
    except FactoryError as e:
        assert e.status=='BLOCKED' and e.code=='TEMPLATE_SHA_MISMATCH' and not out.exists()
