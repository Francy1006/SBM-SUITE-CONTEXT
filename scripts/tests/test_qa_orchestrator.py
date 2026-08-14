from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

CONTEXT_ROOT = Path(__file__).resolve().parents[2]
QA_PROJECT_SOURCE = CONTEXT_ROOT / "QA" / "qa-project.sh"
QA_ALL_SOURCE = CONTEXT_ROOT / "QA" / "qa-all.sh"
QA_CONTEXT_SOURCE = CONTEXT_ROOT / "QA" / "qa-context.sh"
REPOSITORY_SOURCE = CONTEXT_ROOT / "scripts" / "suite-repositories.py"


def _run(*args: str, cwd: Path, check: bool = True):
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class QAEnvironment:
    def __init__(self, root: Path):
        self.root = root
        self.suite = root / "SBM-SUITE"
        self.context = self.suite / "context"
        self.context.mkdir(parents=True)
        (self.context / "scripts").mkdir()
        (self.context / "scripts/tests").mkdir()
        (self.context / "QA").mkdir()
        shutil.copy2(REPOSITORY_SOURCE, self.context / "scripts" / REPOSITORY_SOURCE.name)
        shutil.copy2(QA_PROJECT_SOURCE, self.context / "QA" / QA_PROJECT_SOURCE.name)
        shutil.copy2(QA_ALL_SOURCE, self.context / "QA" / QA_ALL_SOURCE.name)
        shutil.copy2(QA_CONTEXT_SOURCE, self.context / "QA" / QA_CONTEXT_SOURCE.name)
        for path in [
            self.context / "scripts" / REPOSITORY_SOURCE.name,
            self.context / "QA" / QA_PROJECT_SOURCE.name,
            self.context / "QA" / QA_ALL_SOURCE.name,
            self.context / "QA" / QA_CONTEXT_SOURCE.name,
        ]:
            path.chmod(0o755)

        self._repo("SBM/SBM-MANAGER", sonar=True, split=True)
        self._repo("DP/DP-API", sonar=False, split=True)
        self._repo("SBM/SBM-DB", sonar=True, split=False)
        self._repo("SBM/SBM-API", sonar=False, qa=False)
        self._repo("context", sonar=False, qa=False, existing=True)
        self._write_context()
        (self.context / "scripts/tests/test_dummy.py").write_text(
            "import unittest\n\n"
            "class Dummy(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n",
            encoding="utf-8",
        )

    def _repo(self, rel: str, *, sonar: bool, split: bool = False, qa: bool = True, existing: bool = False):
        repo = self.suite / rel
        repo.mkdir(parents=True, exist_ok=True)
        _run("git", "init", "-b", "main", cwd=repo)
        if qa:
            (repo / "scripts").mkdir(exist_ok=True)
            (repo / "context").mkdir(exist_ok=True)
            if split:
                coverage = repo / "scripts/coverage.sh"
                coverage.write_text(
                    "#!/usr/bin/env bash\nset -e\n"
                    "printf 'coverage:%s\\n' \"$(basename \"$(pwd)\")\" >> qa-executions.log\n",
                    encoding="utf-8",
                )
                coverage.chmod(0o755)
            marker = "# sonar-scanner\n" if sonar else ""
            qa_check = repo / "scripts/qa-check.sh"
            qa_check.write_text(
                "#!/usr/bin/env bash\nset -e\n"
                + marker
                + "printf 'full:%s\\n' \"$(basename \"$(pwd)\")\" >> qa-executions.log\n"
                + "mkdir -p context\n"
                + "printf '# QA results\\n\\nOverall status: passed\\n' > context/qa-results.md\n",
                encoding="utf-8",
            )
            qa_check.chmod(0o755)

    def _write_context(self):
        rows = [
            "| SBM-MANAGER | purpose | N/A | N/A | N/A | `sbm/SBM-MANAGER/context/PROJECT_CONTEXT.md` | N/A | N/A |",
            "| DP-API | purpose | N/A | N/A | N/A | `dp/DP-API/context/PROJECT_CONTEXT.md` | N/A | N/A |",
            "| SBM-DB | purpose | N/A | N/A | N/A | `sbm/SBM-DB/context/PROJECT_CONTEXT.md` | N/A | N/A |",
            "| SBM-API | purpose | N/A | N/A | N/A | `sbm/SBM-API/context/PROJECT_CONTEXT.md` | N/A | N/A |",
            "| SBM-SUITE | purpose | N/A | N/A | N/A | `context/PROJECT_CONTEXT.md` | N/A | N/A |",
        ]
        (self.context / "PROJECT_CONTEXT.md").write_text(
            "# PROJECT_CONTEXT.md\n\n## 6. Project objective summaries\n\n"
            "| Project | Purpose | Active objective | Pending objectives | Branch | Main context | QA context | Documentation |\n"
            "|---|---|---|---|---|---|---|---|\n"
            + "\n".join(rows)
            + "\n\n## 7. Boundary\n",
            encoding="utf-8",
        )


class QAOrchestratorTests(unittest.TestCase):
    def test_context_qa_runs_context_regressions_without_sonar(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            r = _run(str(env.context / "QA/qa-context.sh"), cwd=env.context, check=False)
            self.assertEqual(r.returncode, 0, r.stderr)
            result = (env.context / "QA/output/context-qa-results.md").read_text(encoding="utf-8")
            self.assertIn("Overall status: passed", result)
            self.assertIn("SonarQube: not used", result)

    def test_project_without_sonar_uses_split_non_sonar_entrypoint(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            r = _run(
                str(env.context / "QA/qa-project.sh"),
                "SBM-MANAGER",
                "--without-sonar",
                cwd=env.context,
                check=False,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            executions = (env.suite / "SBM/SBM-MANAGER/qa-executions.log").read_text(encoding="utf-8")
            self.assertIn("coverage:SBM-MANAGER", executions)
            self.assertNotIn("full:SBM-MANAGER", executions)
            self.assertTrue((env.context / "QA/output/SBM-SBM-MANAGER-without-sonar-qa-results.md").is_file())

    def test_project_with_sonar_requires_explicit_confirmation(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            r = _run(
                str(env.context / "QA/qa-project.sh"),
                "SBM-MANAGER",
                "--with-sonar",
                cwd=env.context,
                check=False,
            )
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("--sonarqube-ready", r.stderr)

    def test_project_with_sonar_runs_canonical_full_qa(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            r = _run(
                str(env.context / "QA/qa-project.sh"),
                "SBM-MANAGER",
                "--with-sonar",
                "--sonarqube-ready",
                cwd=env.context,
                check=False,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            executions = (env.suite / "SBM/SBM-MANAGER/qa-executions.log").read_text(encoding="utf-8")
            self.assertIn("full:SBM-MANAGER", executions)
            result = (env.context / "QA/output/SBM-SBM-MANAGER-with-sonar-qa-results.md").read_text(encoding="utf-8")
            self.assertIn("## Project evidence", result)

    def test_all_without_sonar_runs_split_project_qa_and_flags_unsplit_qa(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            r = _run(str(env.context / "QA/qa-all.sh"), "--without-sonar", cwd=env.context, check=False)
            self.assertNotEqual(r.returncode, 0)
            summary = (env.context / "QA/output/qa-all-without-sonar-results.md").read_text(encoding="utf-8")
            self.assertIn("SBM-MANAGER", summary)
            self.assertIn("DP-API", summary)
            self.assertIn("SBM-DB", summary)
            self.assertIn("not-configured", summary)
            self.assertNotIn("SBM-SUITE |", summary)

    def test_all_with_sonar_runs_sequential_queue_for_sonar_projects(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            r = _run(
                str(env.context / "QA/qa-all.sh"),
                "--with-sonar",
                "--sonarqube-ready",
                cwd=env.context,
                check=False,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            queue = (env.context / "QA/output/qa-all-with-sonar-queue.tsv").read_text(encoding="utf-8")
            self.assertIn("SBM-MANAGER", queue)
            self.assertIn("SBM-DB", queue)
            self.assertIn("passed", queue)
            self.assertTrue((env.context / "QA/output/qa-all-with-sonar-results.md").is_file())

    def test_default_project_mode_is_without_sonar(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            r = _run(str(env.context / "QA/qa-project.sh"), "SBM-MANAGER", cwd=env.context, check=False)
            self.assertEqual(r.returncode, 0, r.stderr)
            executions = (env.suite / "SBM/SBM-MANAGER/qa-executions.log").read_text(encoding="utf-8")
            self.assertIn("coverage:SBM-MANAGER", executions)
            self.assertNotIn("full:SBM-MANAGER", executions)


if __name__ == "__main__":
    unittest.main()
