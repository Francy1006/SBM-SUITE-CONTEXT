from pathlib import Path
import yaml, hashlib, zipfile, tempfile, copy, importlib.machinery, importlib.util
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding="utf-8"))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file())
def load_validator():
    loader=importlib.machinery.SourceFileLoader("sbm_validate",str(ROOT/"scripts/validate")); spec=importlib.util.spec_from_loader(loader.name,loader); mod=importlib.util.module_from_spec(spec); loader.exec_module(mod); return mod
SCHEMAS={'proposal':'AGENT_PROPOSAL','spec':'AGENT_SPEC','definition':'AGENT_DEFINITION','agent_context':'AGENT_CONTEXT','context_contract':'CONTEXT_CONTRACT','runtime_profile':'RUNTIME_PROFILE','permissions':'PERMISSIONS','hierarchy':'HIERARCHY','relationships':'RELATIONSHIPS','lineage':'CLONE_LINEAGE','approval':'APPROVAL_RECORD','deployment':'DEPLOYMENT_PROFILE'}
def test_qa_template_04_fixtures_valid():
    for p in sorted((ROOT/'fixtures').glob('*/fixture.yaml')):
        f=y(p.relative_to(ROOT).as_posix()); assert isinstance(f,dict) and 'case' in f and 'spec' in f
        for key,sn in SCHEMAS.items():
            if f.get(key) is not None: Draft202012Validator(y(f'schemas/{sn}.schema.yaml')).validate(f[key])
def test_qa_template_05_instance_validation_adversarial():
    f=y('fixtures/new/fixture.yaml'); bad=copy.deepcopy(f['proposal']); del bad['review_status']
    assert list(Draft202012Validator(y('schemas/AGENT_PROPOSAL.schema.yaml')).iter_errors(bad))
    bad2=copy.deepcopy(f['runtime_profile']); bad2['llm_invocation_policy']='LLM_ALWAYS'
    assert list(Draft202012Validator(y('schemas/RUNTIME_PROFILE.schema.yaml')).iter_errors(bad2))
