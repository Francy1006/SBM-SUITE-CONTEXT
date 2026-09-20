from pathlib import Path
import yaml, hashlib, zipfile, tempfile, copy, importlib.machinery, importlib.util
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding="utf-8"))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file())
def load_validator():
    loader=importlib.machinery.SourceFileLoader("sbm_validate",str(ROOT/"scripts/validate")); spec=importlib.util.spec_from_loader(loader.name,loader); mod=importlib.util.module_from_spec(spec); loader.exec_module(mod); return mod
def test_qa_template_23_standard_upgrade_valid():
    v=load_validator(); f=y('fixtures/standard_upgrade/fixture.yaml'); Draft202012Validator(y('schemas/AGENT_SPEC.schema.yaml')).validate(f['spec']); v.cross(f,'upgrade')
def test_qa_template_24_standard_upgrade_invalid_clone_semantics():
    v=load_validator(); f=y('fixtures/standard_upgrade/fixture.yaml'); bad=copy.deepcopy(f); bad['spec']['creation_mode']='CLONE'; bad['lineage']['is_clone']=True
    try: v.cross(bad,'bad'); assert False
    except ValueError: pass
def test_qa_template_25_historical_immutability():
    f=y('fixtures/standard_upgrade/fixture.yaml'); m=f['spec']['migration_reference']; assert m['source_agent_id']==f['spec']['agent_id']; assert m['source_agent_version']!=f['spec']['agent_version']; assert m['source_standard_version']!=f['spec']['standard_version']; assert f['spec']['parent_reference'] is None and f['lineage']['is_clone'] is False
def test_qa_template_26_upgrade_traceability():
    f=y('fixtures/standard_upgrade/fixture.yaml'); m=f['spec']['migration_reference']; assert m=={'source_agent_id':'FixtureAgent','source_agent_version':'1.0.0','source_standard_version':'1.0.0','migration_type':'STANDARD_UPGRADE'}
