from pathlib import Path
import yaml, hashlib, zipfile, tempfile, copy, importlib.machinery, importlib.util
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding="utf-8"))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file())
def load_validator():
    loader=importlib.machinery.SourceFileLoader("sbm_validate",str(ROOT/"scripts/validate")); spec=importlib.util.spec_from_loader(loader.name,loader); mod=importlib.util.module_from_spec(spec); loader.exec_module(mod); return mod
def test_qa_template_19_hierarchy():
    s=y('schemas/HIERARCHY.schema.yaml'); h=y('fixtures/new/fixture.yaml')['hierarchy']; Draft202012Validator(s).validate(h)
    assert h['reports_to']=='sbm-admin' and h['can_instruct']==[]
    bad=copy.deepcopy(h); bad['inferred_by_name']=True; assert list(Draft202012Validator(s).iter_errors(bad))
