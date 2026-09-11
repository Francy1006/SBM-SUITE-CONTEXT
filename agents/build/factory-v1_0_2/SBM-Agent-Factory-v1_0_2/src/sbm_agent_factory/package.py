from pathlib import Path
from .errors import blocked, invalid
from .validate import sha256_tree, clean_files, validate_agent_workspace
from .manifest import write_manifest
from .checksum import write_checksums
from .reproducibility import build_zip
from .qa import run_agent_qa

def package_workspace(workspace,destination,validated_snapshot=None,arc_root=None,compresslevel=6,template_contract=None):
    workspace=Path(workspace); destination=Path(destination)
    if template_contract is None:
        destination.unlink(missing_ok=True)
        blocked('TEMPLATE_SHA_MISMATCH','Final package requires an explicitly resolved canonical Template contract')
    if validated_snapshot is not None and sha256_tree(workspace)!=validated_snapshot: invalid('EXTRA_FILE','Workspace mutated after validation')
    clean_files(workspace)
    # existing integrity is a TOCTOU snapshot: any post-validate mutation must be rejected before regeneration
    if (workspace/'MANIFEST.yaml').is_file() and (workspace/'CHECKSUMS.sha256').is_file():
        validate_agent_workspace(workspace,template_contract=template_contract,verify_integrity=True)
    else:
        validate_agent_workspace(workspace,template_contract=template_contract,verify_integrity=False)
    qa=run_agent_qa(workspace)
    if qa['agent_validate_exit_code'] != 0 or qa['agent_test_exit_code'] != 0:
        destination.unlink(missing_ok=True)
        blocked('INSTANCE_INVALID','Current agent QA failed; package not generated',details=qa)
    write_manifest(workspace); write_checksums(workspace); write_manifest(workspace); write_checksums(workspace)
    validate_agent_workspace(workspace,template_contract=template_contract,verify_integrity=True)
    from .template_engine import TemplateEngine
    TemplateEngine().verify_output(workspace,template_contract,include_integrity=True)
    snapshot=sha256_tree(workspace)
    sha=build_zip(workspace,destination,arc_root=arc_root,compresslevel=compresslevel)
    if sha256_tree(workspace)!=snapshot: destination.unlink(missing_ok=True); blocked('REPRODUCIBILITY_MISMATCH','Workspace changed during package')
    return sha
