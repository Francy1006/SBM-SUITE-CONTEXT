from pathlib import Path
import json, yaml, hashlib, zipfile, tempfile, shutil, subprocess, sys, os
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding='utf-8'))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file())

def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
def test_qa_template_10_manifest_consistency():
    m=y('MANIFEST.yaml'); assert len(m['files'])==67; assert sorted(x['path'] for x in m['files'])==physical(); d={x['path']:x for x in m['files']}; assert d['MANIFEST.yaml']['sha256'] is None and d['CHECKSUMS.sha256']['sha256'] is None
def test_qa_template_11_checksum_consistency():
    lines=(ROOT/'CHECKSUMS.sha256').read_text().splitlines(); c=dict(line.split('  ',1)[::-1] for line in []) if False else {rel:h for h,rel in (line.split('  ',1) for line in lines if line)}; assert len(c)==66; assert 'CHECKSUMS.sha256' not in c; assert sorted(c)==[x for x in physical() if x!='CHECKSUMS.sha256']; assert all(c[r]==sha(r) for r in c)
