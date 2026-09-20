from pathlib import Path
import yaml, hashlib, zipfile, tempfile, copy, importlib.machinery, importlib.util
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding="utf-8"))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file())
def load_validator():
    loader=importlib.machinery.SourceFileLoader("sbm_validate",str(ROOT/"scripts/validate")); spec=importlib.util.spec_from_loader(loader.name,loader); mod=importlib.util.module_from_spec(spec); loader.exec_module(mod); return mod
def test_qa_template_18_permissions_authority():
    v=load_validator(); f=y('fixtures/new/fixture.yaml'); Draft202012Validator(y('schemas/PERMISSIONS.schema.yaml')).validate(f['permissions']); v.cross(f,'good')
    assert not (set(f['permissions']['allowed_actions']) & set(f['permissions']['denied_actions']))
    bad=copy.deepcopy(f); bad['permissions']['allowed_actions'].append('DELETE_ALL')
    try: v.cross(bad,'bad'); assert False
    except ValueError as e: assert 'permissions exceed' in str(e)
    bad2=copy.deepcopy(f); bad2['permissions']['denied_actions'].append('READ')
    try: v.cross(bad2,'bad2'); assert False
    except ValueError as e: assert 'intersects' in str(e)
