from pathlib import Path
import yaml, hashlib, zipfile, tempfile, copy, importlib.machinery, importlib.util
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding="utf-8"))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file())
def load_validator():
    loader=importlib.machinery.SourceFileLoader("sbm_validate",str(ROOT/"scripts/validate")); spec=importlib.util.spec_from_loader(loader.name,loader); mod=importlib.util.module_from_spec(spec); loader.exec_module(mod); return mod
def test_qa_template_21_context_contract():
    f=y('fixtures/new/fixture.yaml'); s=y('schemas/CONTEXT_CONTRACT.schema.yaml'); Draft202012Validator(s).validate(f['context_contract'])
    assert 'specific_objectives' not in f['context_contract']; assert f['context_contract']['context_zip_required'] is True
    bad=copy.deepcopy(f['context_contract']); bad['specific_objectives']=['wrong domain']; assert list(Draft202012Validator(s).iter_errors(bad))

def test_qa_template_21_init_uses_context_contract_startup_lifecycle():
    init=(ROOT/'templates/agent/INIT.template.md').read_text(encoding='utf-8')
    assert 'CONTEXT_CONTRACT.context_zip_required' in init
    assert 'CONTEXT_CONTRACT.context_required' not in init
    assert 'LOADING_AGENT -> WAITING_FOR_CONTEXT -> ACTIVE' in init
    assert '`BLOCKED`' in init
    assert 'No functional work is permitted before a complete, valid, and compatible `context.zip` is loaded and validated.' in init
