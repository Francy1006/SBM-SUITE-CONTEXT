from pathlib import Path
import yaml, hashlib, zipfile, tempfile, copy, importlib.machinery, importlib.util
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding="utf-8"))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file())
def load_validator():
    loader=importlib.machinery.SourceFileLoader("sbm_validate",str(ROOT/"scripts/validate")); spec=importlib.util.spec_from_loader(loader.name,loader); mod=importlib.util.module_from_spec(spec); loader.exec_module(mod); return mod
def test_qa_template_15_spec_component_mismatch():
    v=load_validator(); f=y('fixtures/new/fixture.yaml'); v.cross(f,'good')
    bad=copy.deepcopy(f); bad['spec']['component_references']['PERMISSIONS']['artifact_version']='9.9.9'
    try: v.cross(bad,'bad'); assert False, 'cross-reference mismatch accepted'
    except ValueError as e: assert 'PERMISSIONS reference mismatch' in str(e)
    bad2=copy.deepcopy(f); bad2['spec']['proposal_reference']['proposal_version']='9.9.9'
    try: v.cross(bad2,'bad2'); assert False
    except ValueError as e: assert 'proposal_reference mismatch' in str(e)
