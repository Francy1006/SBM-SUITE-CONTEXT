from pathlib import Path
import json, yaml, hashlib, zipfile, tempfile, shutil, subprocess, sys, os
ROOT=Path(__file__).resolve().parents[1]
def y(rel): return yaml.safe_load((ROOT/rel).read_text(encoding='utf-8'))
def physical(): return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file())

from jsonschema import Draft202012Validator
def test_qa_template_02_template_schema():
    Draft202012Validator(y('schemas/TEMPLATE.schema.yaml')).validate(y('TEMPLATE.yaml'))
def test_qa_template_03_schemas_valid():
    for p in sorted((ROOT/'schemas').glob('*.yaml')): Draft202012Validator.check_schema(y(p.relative_to(ROOT).as_posix()))
