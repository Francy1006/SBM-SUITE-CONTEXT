#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


QA_WORKFLOW_PATH = "scripts/qa-check.sh"
FULL_QA_WORKFLOW_PATH = "QA/qa-full.sh"
TRANSVERSAL_RESULTS_PATH = "QA/output/qa-all-without-sonar-results.md"
TRANSVERSAL_QUEUE_PATH = "QA/output/qa-all-without-sonar-queue.tsv"
FULL_TRANSVERSAL_RESULTS_PATH = "QA/output/qa-all-with-sonar-results.md"
FULL_TRANSVERSAL_QUEUE_PATH = "QA/output/qa-all-with-sonar-queue.tsv"
CONTEXT_QA_RESULTS_PATH = "QA/output/context-qa-results.md"
LIFECYCLE_PHASES = {
    "planning-activation",
    "objective-activation",
    "objective-registration",
    "objective-completion",
    "objective-deletion",
    "objective-update",
    "implementation-progress",
    "implementation-closure",
}


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
        r"^\s*(?:>\s*)?(?:[-*]\s*)?(?:\*\*)?Overall status:(?:\*\*)?\s*"
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


def _read_evidence(root: Path, relative_path: str) -> str | None:
    path = root / relative_path
    if path.is_symlink():
        raise QAContractError(f"QA evidence must not be a symlink: {relative_path}")
    if not path.exists():
        return None
    if not path.is_file():
        raise QAContractError(f"QA evidence is not a file: {relative_path}")
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise QAContractError(
            f"QA evidence is not readable UTF-8: {relative_path}"
        ) from exc
    if not content.strip():
        raise QAContractError(f"QA evidence is empty: {relative_path}")
    return content


def _transversal_queue_status(queue: str, expected_mode: str = "without-sonar") -> str:
    reader = csv.DictReader(io.StringIO(queue), delimiter="\t")
    expected_fields = {"project", "repository", "mode", "status", "exit_code"}
    if reader.fieldnames is None or set(reader.fieldnames) != expected_fields:
        raise QAContractError("transversal QA queue has an invalid header")

    rows = list(reader)
    if not rows:
        raise QAContractError("transversal QA queue has no project results")

    passed = True
    for row in rows:
        if not row["project"].strip() or not row["repository"].strip():
            raise QAContractError("transversal QA queue has an incomplete project row")
        if row["mode"] != expected_mode:
            raise QAContractError("transversal QA queue has an unexpected mode")
        try:
            exit_code = int(row["exit_code"])
        except ValueError as exc:
            raise QAContractError(
                "transversal QA queue has an invalid exit code"
            ) from exc
        acceptable = row["status"] == "passed" and exit_code == 0
        if expected_mode == "with-sonar":
            acceptable = acceptable or (
                row["status"] == "skipped" and exit_code == 3
            )
        if not acceptable:
            passed = False
    return "passed" if passed else "failed"


def evaluate_full_qa(project_name: str, context_root: Path) -> tuple[QADecision, str]:
    """Require successful Context plus all-project Sonar evidence for any lifecycle batch."""
    resolved_root = context_root.resolve(strict=True)
    context_evidence = _read_evidence(resolved_root, CONTEXT_QA_RESULTS_PATH)
    summary = _read_evidence(resolved_root, FULL_TRANSVERSAL_RESULTS_PATH)
    queue = _read_evidence(resolved_root, FULL_TRANSVERSAL_QUEUE_PATH)
    if context_evidence is None or summary is None or queue is None:
        raise QAContractError(
            "full-suite QA evidence requires context QA plus with-Sonar summary and queue"
        )
    context_status = _executed_status(context_evidence)
    summary_status = _transversal_summary_status(summary, allow_not_applicable=True)
    queue_status = _transversal_queue_status(queue, "with-sonar")
    status = "passed" if context_status == summary_status == queue_status == "passed" else "failed"
    evidence = "\n".join(
        (
            "# QA Results",
            "",
            f"Overall status: {status}",
            "",
            f"## {CONTEXT_QA_RESULTS_PATH}",
            "",
            context_evidence.rstrip(),
            "",
            f"## {FULL_TRANSVERSAL_RESULTS_PATH}",
            "",
            summary.rstrip(),
            "",
            f"## {FULL_TRANSVERSAL_QUEUE_PATH}",
            "",
            "```tsv",
            queue.rstrip(),
            "```",
            "",
        )
    )
    decision = QADecision(
        status=status,
        applicable=True,
        workflow_path=FULL_QA_WORKFLOW_PATH,
        evidence_file="qa-results.md",
        evidence_sha256=_sha256(evidence),
        reason="full Context and transversal with-Sonar QA evidence verified",
    )
    if status != "passed":
        raise QAContractError("lifecycle batch is blocked by failed full-suite QA")
    return decision, evidence


def _transversal_summary_status(summary: str, *, allow_not_applicable: bool = False) -> str:
    statuses = re.findall(
        r"^\|\s*[^|]+\|\s*`[^`]+`\s*\|\s*([^|]+?)\s*\|",
        summary,
        flags=re.MULTILINE,
    )
    statuses = [status.strip().casefold() for status in statuses]
    if not statuses:
        raise QAContractError("transversal QA summary has no project results")
    allowed = {"passed"}
    if allow_not_applicable:
        allowed.add("not-applicable")
    return "passed" if all(status in allowed for status in statuses) else "failed"


def evaluate_progress_qa(
    project_name: str, project_root: Path
) -> tuple[QADecision, str] | None:
    """Resolve optional QA evidence for an implementation-progress export."""
    if project_name != "sbm-suite-context":
        return None

    resolved_root = project_root.resolve(strict=True)
    summary = _read_evidence(resolved_root, TRANSVERSAL_RESULTS_PATH)
    queue = _read_evidence(resolved_root, TRANSVERSAL_QUEUE_PATH)
    context_evidence = _read_evidence(resolved_root, CONTEXT_QA_RESULTS_PATH)

    if summary is None and queue is None:
        if context_evidence is None:
            return None
        status = _executed_status(context_evidence)
        evidence = context_evidence
        workflow_path = QA_WORKFLOW_PATH
        reason = "Context QA executed with canonical evidence"
    else:
        if summary is None or queue is None:
            raise QAContractError(
                "transversal QA evidence requires both results and queue files"
            )
        summary_status = _transversal_summary_status(summary)
        queue_status = _transversal_queue_status(queue)
        status = (
            "passed"
            if summary_status == queue_status == "passed"
            else "failed"
        )
        sections = [
            "# QA Results",
            "",
            f"Overall status: {status}",
            "",
            f"## {TRANSVERSAL_RESULTS_PATH}",
            "",
            summary.rstrip(),
            "",
            f"## {TRANSVERSAL_QUEUE_PATH}",
            "",
            "```tsv",
            queue.rstrip(),
            "```",
        ]
        if context_evidence is not None:
            context_status = _executed_status(context_evidence)
            if context_status != "passed":
                status = "failed"
                sections[2] = "Overall status: failed"
            sections.extend(
                [
                    "",
                    f"## {CONTEXT_QA_RESULTS_PATH}",
                    "",
                    context_evidence.rstrip(),
                ]
            )
        evidence = "\n".join(sections) + "\n"
        workflow_path = QA_WORKFLOW_PATH
        reason = "transversal QA executed with verified summary and queue evidence"

    decision = QADecision(
        status=status,
        applicable=True,
        workflow_path=workflow_path,
        evidence_file="qa-results.md",
        evidence_sha256=_sha256(evidence),
        reason=reason,
    )
    return decision, evidence


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
    if project_name == "sbm-suite-context":
        transversal = evaluate_progress_qa(project_name, project_root)
        if transversal is not None:
            decision, evidence = transversal
            if decision.status == "failed":
                raise QAContractError("implementation-closure is blocked by failed QA")
            return decision, evidence

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
    if decision.evidence_file != "qa-results.md":
        raise QAContractError("export has an unsupported QA evidence path")
    if decision.evidence_sha256 != _sha256(evidence):
        raise QAContractError("export QA evidence hash does not match")
    with ZipFile(context_package) as archive:
        try:
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise QAContractError("context package manifest is invalid") from exc
    if manifest.get("project_name") != project_name:
        raise QAContractError("context package project_name does not match QA decision")
    phase = manifest.get("lifecycle_phase")
    if decision.workflow_path == FULL_QA_WORKFLOW_PATH:
        if phase not in LIFECYCLE_PHASES:
            raise QAContractError("full QA export has an unsupported lifecycle phase")
        if decision.status != "passed" or not decision.applicable:
            raise QAContractError("full QA export has no authorizing QA status")
    elif phase == "implementation-closure":
        if decision.status not in {"passed", "not-applicable"}:
            raise QAContractError("closure export has no authorizing QA status")
        if decision.applicable != (decision.status == "passed"):
            raise QAContractError("closure export has inconsistent QA applicability")
        if decision.workflow_path != QA_WORKFLOW_PATH:
            raise QAContractError("closure export has an unsupported QA workflow path")
    elif phase == "implementation-progress":
        if decision.status not in {"passed", "failed"} or not decision.applicable:
            raise QAContractError("progress export has inconsistent QA status")
        if decision.workflow_path != QA_WORKFLOW_PATH:
            raise QAContractError("progress export has an unsupported QA workflow path")
    else:
        raise QAContractError("QA export normalization applies only to implementation")
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

    progress = subparsers.add_parser("evaluate-progress")
    progress.add_argument("--project-name", required=True)
    progress.add_argument("--project-root", required=True)
    progress.add_argument("--output", required=True)

    full = subparsers.add_parser("evaluate-full")
    full.add_argument("--project-name", required=True)
    full.add_argument("--project-root", required=True)
    full.add_argument("--output", required=True)

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
        elif arguments.command == "evaluate-progress":
            result = evaluate_progress_qa(
                arguments.project_name, Path(arguments.project_root)
            )
            payload: dict[str, Any] = {
                "project_name": arguments.project_name,
                "qa": None,
                "qa_results": "",
            }
            if result is not None:
                decision, evidence = result
                payload["qa"] = decision.manifest()
                payload["qa_results"] = evidence
            Path(arguments.output).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        elif arguments.command == "evaluate-full":
            decision, evidence = evaluate_full_qa(
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
