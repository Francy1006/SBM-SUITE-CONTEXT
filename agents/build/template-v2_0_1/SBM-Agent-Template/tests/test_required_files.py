from pathlib import Path
import json, yaml, hashlib, zipfile, tempfile, shutil, subprocess, sys, os
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding='utf-8'))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file())

def test_qa_template_06_required_files():
    t=y('TEMPLATE.yaml'); assert set(physical())==set(t['required_files']) and len(t['required_files'])==67
def test_qa_template_07_no_extra_files():
    assert set(physical())==set(y('TEMPLATE.yaml')['required_files'])
