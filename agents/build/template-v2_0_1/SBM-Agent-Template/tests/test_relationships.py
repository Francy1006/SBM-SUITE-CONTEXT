from pathlib import Path
import yaml, hashlib, zipfile, tempfile, copy, importlib.machinery, importlib.util
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding="utf-8"))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file())
def load_validator():
    loader=importlib.machinery.SourceFileLoader("sbm_validate",str(ROOT/"scripts/validate")); spec=importlib.util.spec_from_loader(loader.name,loader); mod=importlib.util.module_from_spec(spec); loader.exec_module(mod); return mod
def test_qa_template_20_relationships():
    s=y('schemas/RELATIONSHIPS.schema.yaml'); r=y('fixtures/new/fixture.yaml')['relationships']; Draft202012Validator(s).validate(r)
    rel=r['relationships'][0]; assert set(rel)=={'actor','relationship_type','direction','purpose'}
    bad=copy.deepcopy(r); del bad['relationships'][0]['purpose']; assert list(Draft202012Validator(s).iter_errors(bad))
