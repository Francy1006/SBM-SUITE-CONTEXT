from pathlib import Path
import hashlib, os, tempfile, zipfile, shutil

ROOT=Path(__file__).resolve().parents[1]
FIXED_DT=(2020,1,1,0,0,0)
ROOT_NAME="SBM-Agent-Template"
ZIP_COMPRESSLEVEL=6

def physical(root=ROOT):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())

def makezip(src_root, dst):
    with zipfile.ZipFile(dst,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=ZIP_COMPRESSLEVEL) as z:
        for rel in physical(src_root):
            info=zipfile.ZipInfo(f"{ROOT_NAME}/{rel}",FIXED_DT)
            info.create_system=3
            info.external_attr=(0o100644)<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(src_root/rel).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=ZIP_COMPRESSLEVEL)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def test_qa_template_12_reproducibility():
    with tempfile.TemporaryDirectory(prefix="sbm-repro-") as d:
        td=Path(d)
        a=td/"generation-a.zip"
        b=td/"generation-b.zip"
        makezip(ROOT,a)
        makezip(ROOT,b)
        assert a.read_bytes()==b.read_bytes()

        delivered_env=os.environ.get("SBM_DELIVERED_ZIP")
        delivered=Path(delivered_env) if delivered_env else a
        assert delivered.is_file()
        assert sha(a)==sha(b)==sha(delivered)

        extracted=td/"extracted"
        with zipfile.ZipFile(delivered) as z:
            z.extractall(extracted)
        rebuilt=td/"rebuilt-from-extracted.zip"
        makezip(extracted/ROOT_NAME,rebuilt)
        assert sha(rebuilt)==sha(delivered)
        assert rebuilt.read_bytes()==delivered.read_bytes()
