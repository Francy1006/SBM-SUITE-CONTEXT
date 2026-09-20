from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from .checksum import sha256_file
FIXED_DT=(1980,1,1,0,0,0)

def build_zip(source_root, destination, arc_root=None, compresslevel=6):
    source_root=Path(source_root); destination=Path(destination)
    arc_root=arc_root or source_root.name
    files=sorted(p for p in source_root.rglob('*') if p.is_file())
    with ZipFile(destination,'w',compression=ZIP_DEFLATED,compresslevel=compresslevel) as z:
        for p in files:
            rel=p.relative_to(source_root).as_posix(); arc=f"{arc_root}/{rel}"
            info=ZipInfo(arc,FIXED_DT); info.compress_type=ZIP_DEFLATED; info.create_system=3
            mode=0o755 if rel.startswith('scripts/') or rel in () else 0o644
            info.external_attr=(mode & 0xFFFF)<<16
            info.flag_bits|=0x800
            z.writestr(info,p.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=compresslevel)
    return sha256_file(destination)

def rebuild_from_extracted(extracted_root,destination,arc_root=None,compresslevel=6):
    return build_zip(extracted_root,destination,arc_root=arc_root,compresslevel=compresslevel)
