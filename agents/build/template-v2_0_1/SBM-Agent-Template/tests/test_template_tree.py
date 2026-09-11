from pathlib import Path
import json, yaml, hashlib, zipfile, tempfile, shutil, subprocess, sys, os
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding='utf-8'))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file())

def test_qa_template_01_tree_exact():
    t=y('TEMPLATE.yaml'); assert len(physical())==67; assert physical()==sorted(t['required_files'])
