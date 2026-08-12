#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


QA_WORKFLOW_PATH = "scripts/qa-check.sh"
class QAContractError(ValueError):
    pass


@dataclass(frozen=True)
class QADecision:
    status: str
    applicable: bool
    workflow_path: str
    evidence_file: str
    evidence_sha256: str
    reason: str

    def manifest(self) -> dict[str, Any]:
        return asdict(self)

    def evidence(self, project_name: str) -> str:
        if self.status == "not-applicable":
            return (
                "# QA Results\n\n"
                "QA status: not-applicable\n"
                "QA applicable: false\n"
                f"QA workflow: {self.workflow_path}\n"
                f"Project: {project_name}\n"
                f"Reason: {self.reason}\n"
            )
        raise QAContractError("executed QA evidence must be preserved verbatim")


def qa_results_path(project_name: str, project_root: Path) -> Path:
    if project_name == "sbm-suite-context":
        return project_root / "qa-results.md"
    return project_root / "context" / "qa-results.md"


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _executed_status(evidence: str) -> str:
    match = re.search(
        r"^\s*(?:>\s*)?(?:\*\*)?Overall status:(?:\*\*)?\s*"
        r"(?:\*\*)?(passed|success|failed|failure)(?:\*\*)?\s*$",
        evidence,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if match is None:
        raise QAContractError(
            "QA workflow is applicable but qa-results.md has no canonical "
            "Overall status"
        )
    return "passed" if match.group(1).casefold() in {"passed", "success"} else "failed"


def evaluate_qa(project_name: str, project_root: Path) -> tuple[QADecision, str]:
    resolved_root = project_root.resolve(strict=True)
    workflow = resolved_root / QA_WORKFLOW_PATH
    if not workflow.is_file():
        reason = (
            "no applicable QA workflow is currently defined for "
            f"{project_name}: {QA_WORKFLOW_PATH} does not exist"
        )
        evidence = (
            "# QA Results\n\n"
            "QA status: not-applicable\n"
            "QA applicable: false\n"
            f"QA workflow: {QA_WORKFLOW_PATH}\n"
            f"Project: {project_name}\n"
            f"Reason: {reason}\n"
        )
        decision = QADecision(
            status="not-applicable",
            applicable=False,
            workflow_path=QA_WORKFLOW_PATH,
            evidence_file="qa-results.md",
            evidence_sha256=_sha256(evidence),
            reason=reason,
        )
        return decision, evidence

    evidence_path = qa_results_path(project_name, resolved_root)
    if evidence_path.is_symlink() or not evidence_path.is_file():
        raise QAContractError(
            "QA workflow is applicable but executed qa-results.md evidence is missing"
        )
    try:
        evidence = evidence_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise QAContractError("qa-results.md is not readable UTF-8") from exc
    if not evidence.strip():
        raise QAContractError(
            "QA workflow is applicable but executed qa-results.md evidence is empty"
        )

    status = _executed_status(evidence)
    decision = QADecision(
        status=status,
        applicable=True,
        workflow_path=QA_WORKFLOW_PATH,
        evidence_file="qa-results.md",
        evidence_sha256=_sha256(evidence),
        reason="applicable QA workflow executed with canonical evidence",
    )
    return decision, evidence


def require_closure_qa(project_name: str, project_root: Path) -> tuple[QADecision, str]:
    decision, evidence = evaluate_qa(project_name, project_root)
    if decision.status == "failed":
        raise QAContractError("implementation-closure is blocked by failed QA")
    return decision, evidence


def validate_closure_manifest_qa(
    raw_qa: Any,
    project_name: str,
    project_root: Path,
) -> QADecision:
    if not isinstance(raw_qa, dict):
        raise QAContractError("implementation-closure manifest.qa must be an object")
    expected, _ = require_closure_qa(project_name, project_root)
    if raw_qa != expected.manifest():
        raise QAContractError(
            "manifest.qa does not match the structurally verified project QA state"
        )
    return expected


def _rewrite_zip_entries(zip_path: Path, replacements: dict[str, bytes]) -> None:
    if zip_path.is_symlink() or not zip_path.is_file():
        raise QAContractError(f"required export package does not exist: {zip_path}")
    with tempfile.NamedTemporaryFile(
        dir=zip_path.parent,
        prefix=f".{zip_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        replaced: set[str] = set()
        with ZipFile(zip_path) as source, ZipFile(
            temporary_path, "w", compression=ZIP_DEFLATED
        ) as target:
            for member in source.infolist():
                content = replacements.get(member.filename)
                if content is None:
                    content = source.read(member.filename)
                else:
                    replaced.add(member.filename)
                target.writestr(member, content)
        missing = sorted(set(replacements) - replaced)
        if missing:
            raise QAContractError(
                "export package is missing required QA entries: " + ", ".join(missing)
            )
        os.replace(temporary_path, zip_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def normalize_context_export(
    context_package: Path,
    upload_package: Path,
    project_name: str,
    decision: QADecision,
    evidence: str,
) -> None:
    if decision.status not in {"passed", "not-applicable"}:
        raise QAContractError("closure export has no authorizing QA status")
    if decision.applicable != (decision.status == "passed"):
        raise QAContractError("closure export has inconsistent QA applicability")
    if decision.workflow_path != QA_WORKFLOW_PATH:
        raise QAContractError("closure export has an unsupported QA workflow path")
    if decision.evidence_file != "qa-results.md":
        raise QAContractError("closure export has an unsupported QA evidence path")
    if decision.evidence_sha256 != _sha256(evidence):
        raise QAContractError("closure export QA evidence hash does not match")
    with ZipFile(context_package) as archive:
        try:
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise QAContractError("context package manifest is invalid") from exc
    if manifest.get("project_name") != project_name:
        raise QAContractError("context package project_name does not match QA decision")
    if manifest.get("lifecycle_phase") != "implementation-closure":
        raise QAContractError("QA export normalization applies only to closure")
    manifest["qa"] = decision.manifest()
    rendered_manifest = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    _rewrite_zip_entries(
        context_package,
        {
            "manifest.json": rendered_manifest,
            "qa-results.md": evidence.encode("utf-8"),
        },
    )
    _rewrite_zip_entries(
        upload_package,
        {"context-package.zip": context_package.read_bytes()},
    )


def _decision_file(path: Path) -> tuple[str, QADecision, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return (
        payload["project_name"],
        QADecision(**payload["qa"]),
        payload["qa_results"],
    )


def _main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    evaluate = subparsers.add_parser("evaluate-closure")
    evaluate.add_argument("--project-name", required=True)
    evaluate.add_argument("--project-root", required=True)
    evaluate.add_argument("--output", required=True)

    normalize = subparsers.add_parser("normalize-export")
    normalize.add_argument("--decision", required=True)
    normalize.add_argument("--context-package", required=True)
    normalize.add_argument("--upload-package", required=True)

    arguments = parser.parse_args()
    try:
        if arguments.command == "evaluate-closure":
            decision, evidence = require_closure_qa(
                arguments.project_name, Path(arguments.project_root)
            )
            Path(arguments.output).write_text(
                json.dumps(
                    {
                        "project_name": arguments.project_name,
                        "qa": decision.manifest(),
                        "qa_results": evidence,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        else:
            project_name, decision, evidence = _decision_file(
                Path(arguments.decision)
            )
            normalize_context_export(
                Path(arguments.context_package),
                Path(arguments.upload_package),
                project_name,
                decision,
                evidence,
            )
    except (OSError, QAContractError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
