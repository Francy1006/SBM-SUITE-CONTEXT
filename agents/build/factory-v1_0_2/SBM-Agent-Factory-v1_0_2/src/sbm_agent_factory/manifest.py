from pathlib import Path
import yaml
from .checksum import sha256_file

def physical_files(root): return sorted(p.relative_to(root).as_posix() for p in Path(root).rglob('*') if p.is_file())
def build_manifest(root, identity=None):
    root=Path(root); files=[]
    for rel in physical_files(root):
        h=None if rel in ('MANIFEST.yaml','CHECKSUMS.sha256') else sha256_file(root/rel)
        files.append({'path':rel,'purpose':'package artifact','required':True,'sha256':h})
    if (root/'AGENT_SPEC.yaml').is_file():
        s=yaml.safe_load((root/'AGENT_SPEC.yaml').read_text(encoding='utf-8')); d={'agent_id':s['agent_id'],'agent_version':s['agent_version'],'standard_version':s['standard_version'],'template_version':s['template_version'],'files':files}
    else: d={'factory_id':'SBM-Agent-Factory','factory_version':'1.0.2','files':files}
    if identity: d.update(identity)
    return d

def write_manifest(root):
    root=Path(root); d=build_manifest(root); (root/'MANIFEST.yaml').write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True),encoding='utf-8',newline='\n'); return d
