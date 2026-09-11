from pathlib import Path
import hashlib

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def file_hashes(root, exclude=("CHECKSUMS.sha256",)):
    root=Path(root)
    return {p.relative_to(root).as_posix():sha256_file(p) for p in sorted(root.rglob('*')) if p.is_file() and p.relative_to(root).as_posix() not in exclude}

def write_checksums(root):
    root=Path(root); hashes=file_hashes(root)
    text=''.join(f"{h}  {p}\n" for p,h in sorted(hashes.items()))
    (root/'CHECKSUMS.sha256').write_text(text,encoding='utf-8',newline='\n')
    return hashes

def read_checksums(path):
    out={}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        h,p=line.split('  ',1); out[p]=h
    return out
