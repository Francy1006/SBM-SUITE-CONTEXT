from pathlib import Path
import json, yaml, hashlib, zipfile, tempfile, shutil, subprocess, sys, os
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding='utf-8'))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file())

def test_qa_template_13_prohibited_artifacts():
    bad={'__pycache__','.pytest_cache','node_modules','.git','build','dist','context','.sbm','coverage','.DS_Store','Thumbs.db'}
    for rel in physical(): assert not any(x in bad for x in Path(rel).parts)
