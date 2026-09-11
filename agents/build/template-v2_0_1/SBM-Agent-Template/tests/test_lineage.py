from pathlib import Path
import yaml, hashlib, zipfile, tempfile, copy, importlib.machinery, importlib.util
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding="utf-8"))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file())
def load_validator():
    loader=importlib.machinery.SourceFileLoader("sbm_validate",str(ROOT/"scripts/validate")); spec=importlib.util.spec_from_loader(loader.name,loader); mod=importlib.util.module_from_spec(spec); loader.exec_module(mod); return mod
def test_qa_template_16_new_lineage():
    v=load_validator(); f=y('fixtures/new/fixture.yaml'); v.cross(f,'new'); l=f['lineage']; assert f['spec']['creation_mode']=='NEW' and l['is_clone'] is False and all(l[x] is None for x in ['clone_id','parent_agent_id','parent_agent_version','parent_spec_id','parent_spec_version'])
def test_qa_template_17_clone_lineage():
    v=load_validator(); f=y('fixtures/clone/fixture.yaml'); v.cross(f,'clone'); p=f['spec']['parent_reference']; l=f['lineage']; assert l['is_clone'] is True and (l['parent_agent_id'],l['parent_agent_version'],l['parent_spec_id'],l['parent_spec_version'])==(p['agent_id'],p['agent_version'],p['spec_id'],p['spec_version'])
