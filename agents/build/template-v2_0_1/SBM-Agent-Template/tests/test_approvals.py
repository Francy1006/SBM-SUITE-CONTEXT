from pathlib import Path
import yaml, hashlib, zipfile, tempfile, copy, importlib.machinery, importlib.util
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding="utf-8"))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file())
def load_validator():
    loader=importlib.machinery.SourceFileLoader("sbm_validate",str(ROOT/"scripts/validate")); spec=importlib.util.spec_from_loader(loader.name,loader); mod=importlib.util.module_from_spec(spec); loader.exec_module(mod); return mod
def test_qa_template_14_approval_mismatch():
    s=y('schemas/APPROVAL_RECORD.schema.yaml'); good=y('fixtures/new/fixture.yaml')['approval']; Draft202012Validator(s).validate(good)
    bad=copy.deepcopy(good); bad['approved_by']='Yeoman'; assert list(Draft202012Validator(s).iter_errors(bad))
    bad2=copy.deepcopy(good); bad2['approval_type']='OTHER'; assert list(Draft202012Validator(s).iter_errors(bad2))
