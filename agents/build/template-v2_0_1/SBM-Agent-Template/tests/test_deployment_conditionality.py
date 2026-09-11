from pathlib import Path
import yaml, hashlib, zipfile, tempfile, copy, importlib.machinery, importlib.util
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding="utf-8"))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file())
def load_validator():
    loader=importlib.machinery.SourceFileLoader("sbm_validate",str(ROOT/"scripts/validate")); spec=importlib.util.spec_from_loader(loader.name,loader); mod=importlib.util.module_from_spec(spec); loader.exec_module(mod); return mod
def test_qa_template_08_deployment_absent():
    v=load_validator(); f=y('fixtures/deployment_absent/fixture.yaml'); assert f['deployment'] is None and f['generated_deployment_present'] is False; v.cross(f,'absent')
def test_qa_template_09_deployment_present():
    v=load_validator(); f=y('fixtures/deployment_present/fixture.yaml'); assert f['generated_deployment_present'] is True
    Draft202012Validator(y('schemas/DEPLOYMENT_PROFILE.schema.yaml')).validate(f['deployment']); v.cross(f,'present')
    bad=copy.deepcopy(f); bad['runtime_profile']['runtime_reference']['target']='OPENAI_API'
    try: v.cross(bad,'bad'); assert False
    except ValueError as e: assert 'runtime/deployment mismatch' in str(e)
