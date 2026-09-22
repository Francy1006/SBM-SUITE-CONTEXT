from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.tests._git_bash import bash_executable as _bash_executable

CONTEXT_ROOT = Path(__file__).resolve().parents[2]
QA_PROJECT_SOURCE = CONTEXT_ROOT / "QA" / "qa-project.sh"
QA_ALL_SOURCE = CONTEXT_ROOT / "QA" / "qa-all.sh"
QA_CONTEXT_SOURCE = CONTEXT_ROOT / "QA" / "qa-context.sh"
QA_FULL_SOURCE = CONTEXT_ROOT / "QA" / "qa-full.sh"
REPOSITORY_SOURCE = CONTEXT_ROOT / "scripts" / "suite-repositories.py"


def _bash_path(path: Path) -> str:
    resolved = path.resolve().as_posix()
    if os.name == "nt" and len(resolved) >= 3 and resolved[1:3] == ":/":
        return f"/{resolved[0].lower()}/{resolved[3:]}"
    return resolved


def _run(*args: str, cwd: Path, check: bool = True, env=None):
    command = list(args)
    if os.name == "nt" and command[0].endswith(".sh"):
        script = Path(command[0]).resolve()
        try:
            script_arg = "./" + script.relative_to(cwd.resolve()).as_posix()
        except ValueError:
            script_arg = _bash_path(script)
        command = [_bash_executable(), script_arg, *command[1:]]
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )


class QAEnvironment:
    def __init__(self, root: Path, *, context_venv_layout: str = "bin"):
        self.root = root
        self.suite = root / "SBM-SUITE"
        self.context = self.suite / "context"
        self.context.mkdir(parents=True)
        (self.context / "scripts").mkdir()
        (self.context / "scripts/tests").mkdir()
        (self.context / "QA").mkdir()
        self._install_context_python(context_venv_layout)
        shutil.copy2(REPOSITORY_SOURCE, self.context / "scripts" / REPOSITORY_SOURCE.name)
        shutil.copy2(QA_PROJECT_SOURCE, self.context / "QA" / QA_PROJECT_SOURCE.name)
        shutil.copy2(QA_ALL_SOURCE, self.context / "QA" / QA_ALL_SOURCE.name)
        shutil.copy2(QA_CONTEXT_SOURCE, self.context / "QA" / QA_CONTEXT_SOURCE.name)
        shutil.copy2(QA_FULL_SOURCE, self.context / "QA" / QA_FULL_SOURCE.name)
        for path in [
            self.context / "scripts" / REPOSITORY_SOURCE.name,
            self.context / "QA" / QA_PROJECT_SOURCE.name,
            self.context / "QA" / QA_ALL_SOURCE.name,
            self.context / "QA" / QA_CONTEXT_SOURCE.name,
            self.context / "QA" / QA_FULL_SOURCE.name,
        ]:
            path.chmod(0o755)

        (self.context / "scripts/suite-repositories.json").write_text(
            json.dumps(
                [
                    "context",
                    "DP/DP-API",
                    "SBM/SBM-API",
                    "SBM/SBM-DB",
                    "SBM/SBM-MANAGER",
                ]
            ),
            encoding="utf-8",
        )

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

    def _install_context_python(self, layout: str) -> None:
        if layout == "Scripts":
            executable = self.context / ".venv/Scripts/python.exe"
        elif layout == "bin":
            executable = self.context / ".venv/bin/python3"
        else:
            raise ValueError(f"layout no soportado: {layout}")
        executable.parent.mkdir(parents=True)
        real_python = shlex.quote(_bash_path(Path(sys.executable)))
        log = shlex.quote(_bash_path(self.context / "context-python.log"))
        executable.write_text(
            "#!/usr/bin/env bash\n"
            f"printf '%s\\n' \"$*\" >> {log}\n"
            f"exec {real_python} \"$@\"\n",
            encoding="utf-8",
        )
        executable.chmod(0o755)

    def context_python_log(self) -> str:
        return (self.context / "context-python.log").read_text(encoding="utf-8")

    def inherited_context_environment(self) -> dict[str, str]:
        venv = self.context / ".venv"
        venv_bin = venv / ("Scripts" if (venv / "Scripts").is_dir() else "bin")
        return os.environ | {
            "PATH": f"{venv_bin}{os.pathsep}{os.environ['PATH']}",
            "VIRTUAL_ENV": str(venv),
            "VIRTUAL_ENV_PROMPT": "(context)",
        }

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
        for layout in ("Scripts", "bin"):
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as d:
                env = QAEnvironment(Path(d), context_venv_layout=layout)
                r = _run(
                    str(env.context / "QA/qa-context.sh"),
                    cwd=env.context,
                    check=False,
                )
                self.assertEqual(r.returncode, 0, r.stderr)
                result = (
                    env.context / "QA/output/context-qa-results.md"
                ).read_text(encoding="utf-8")
                self.assertIn("Overall status: passed", result)
                self.assertIn("SonarQube: not used", result)
                python_log = env.context_python_log()
                self.assertIn("-m unittest", python_log)
                self.assertIn("-m py_compile", python_log)

    def test_full_qa_uses_context_python_without_global_fallback(self):
        source = QA_FULL_SOURCE.read_text(encoding="utf-8")
        self.assertIn('CONTEXT_PYTHON="$(context_python)"', source)
        self.assertNotRegex(source, r"(?m)^\s*python3(?:\s|$)")
        self.assertGreaterEqual(source.count('"${CONTEXT_PYTHON}"'), 4)

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


    def test_without_sonar_entrypoint_may_contain_sonar_text(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            coverage = env.suite / "SBM/SBM-MANAGER/scripts/coverage.sh"
            coverage.write_text(
                "#!/usr/bin/env bash\n"
                "set -e\n"
                "echo 'QA sin SonarQube'\n"
                "printf 'coverage:SBM-MANAGER\\n' >> qa-executions.log\n",
                encoding="utf-8",
            )
            coverage.chmod(0o755)

            r = _run(
                str(env.context / "QA/qa-project.sh"),
                "SBM-MANAGER",
                "--without-sonar",
                cwd=env.context,
                check=False,
            )

            self.assertEqual(r.returncode, 0, r.stderr)

    def test_all_isolates_child_stdin_and_processes_remaining_repositories(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            coverage = env.suite / "DP/DP-API/scripts/coverage.sh"
            coverage.write_text(
                "#!/usr/bin/env bash\n"
                "set -e\n"
                "IFS= read -r _ || true\n"
                "printf 'coverage:DP-API\\n' >> qa-executions.log\n",
                encoding="utf-8",
            )
            coverage.chmod(0o755)

            _run(
                str(env.context / "QA/qa-all.sh"),
                "--without-sonar",
                cwd=env.context,
                check=False,
            )

            summary = (
                env.context / "QA/output/qa-all-without-sonar-results.md"
            ).read_text(encoding="utf-8")

            self.assertIn("DP-API", summary)
            self.assertIn("SBM-DB", summary)


    def test_all_without_sonar_fails_when_repository_has_no_qa_entrypoint(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))

            r = _run(
                str(env.context / "QA/qa-all.sh"),
                "--without-sonar",
                cwd=env.context,
                check=False,
            )

            self.assertNotEqual(r.returncode, 0)

            summary = (
                env.context / "QA/output/qa-all-without-sonar-results.md"
            ).read_text(encoding="utf-8")

            self.assertIn("SBM-API", summary)
            self.assertIn("not-configured", summary)

    def test_context_venv_python_runs_inventory_helper_on_both_layouts(self):
        for layout in ("Scripts", "bin"):
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as d:
                env = QAEnvironment(Path(d), context_venv_layout=layout)

                project = _run(
                    str(env.context / "QA/qa-project.sh"),
                    "DP-API",
                    cwd=env.context,
                    check=False,
                )
                self.assertEqual(project.returncode, 0, project.stderr)
                self.assertIn("resolve DP-API", env.context_python_log())

                _run(
                    str(env.context / "QA/qa-all.sh"),
                    "--without-sonar",
                    cwd=env.context,
                    check=False,
                )
                self.assertTrue(
                    any(
                        line.endswith("suite-repositories.py list")
                        for line in env.context_python_log().splitlines()
                    )
                )

    def test_context_venv_is_not_inherited_by_child_qa(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            context_only = env.context / ".venv/bin/context-only"
            context_only.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            context_only.chmod(0o755)
            coverage = env.suite / "DP/DP-API/scripts/coverage.sh"
            coverage.write_text(
                "#!/usr/bin/env bash\nset -euo pipefail\n"
                "if command -v context-only >/dev/null 2>&1; then exit 19; fi\n"
                "printf '%s\\n' \"${VIRTUAL_ENV-unset}\" > child-virtual-env.txt\n"
                "printf '%s\\n' \"$PATH\" > child-path.txt\n",
                encoding="utf-8",
            )
            coverage.chmod(0o755)

            inherited = env.inherited_context_environment()
            inherited["PATH"] += r";E:\Programs Files\Git\cmd"
            result = _run(
                str(env.context / "QA/qa-project.sh"),
                "DP-API",
                cwd=env.context,
                check=False,
                env=inherited,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            child_virtual_env = (
                env.suite / "DP/DP-API/child-virtual-env.txt"
            ).read_text(encoding="utf-8").strip()
            self.assertEqual(child_virtual_env, "unset")
            child_path = (env.suite / "DP/DP-API/child-path.txt").read_text(
                encoding="utf-8"
            ).strip()
            self.assertNotRegex(child_path, r";[A-Za-z]:[\\/]")
            self.assertFalse(any(";E" in path.name for path in env.suite.rglob("*")))

    def test_repository_venv_is_selected_for_windows_and_posix_layouts(self):
        layouts = (("Scripts", "repo-python.exe"), ("bin", "repo-python"))
        for layout, command in layouts:
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as d:
                env = QAEnvironment(Path(d))
                repository = env.suite / "DP/DP-API"
                repo_command = repository / ".venv" / layout / command
                repo_command.parent.mkdir(parents=True)
                repo_command.write_text(
                    "#!/usr/bin/env bash\nprintf 'repository-python\\n'\n",
                    encoding="utf-8",
                )
                repo_command.chmod(0o755)
                coverage = repository / "scripts/coverage.sh"
                coverage.write_text(
                    "#!/usr/bin/env bash\nset -euo pipefail\n"
                    f"{command} > selected-python.txt\n"
                    "printf '%s\\n' \"${VIRTUAL_ENV-unset}\" > child-virtual-env.txt\n",
                    encoding="utf-8",
                )
                coverage.chmod(0o755)

                result = _run(
                    str(env.context / "QA/qa-project.sh"),
                    "DP-API",
                    cwd=env.context,
                    check=False,
                    env=env.inherited_context_environment(),
                )

                self.assertEqual(
                    result.returncode, 0, result.stdout + result.stderr
                )
                self.assertEqual(
                    (repository / "selected-python.txt").read_text(encoding="utf-8"),
                    "repository-python\n",
                )
                child_venv = (
                    repository / "child-virtual-env.txt"
                ).read_text(encoding="utf-8").strip()
                self.assertTrue(child_venv.endswith("/DP/DP-API/.venv"), child_venv)

    @unittest.skipUnless(os.name == "nt", "Windows python3 shim is Windows-specific")
    def test_windows_repository_python3_shim_uses_repository_python(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            repository = env.suite / "DP/DP-API"
            python = repository / ".venv/Scripts/python.exe"
            python.parent.mkdir(parents=True)
            python.write_text(
                "#!/usr/bin/env bash\n"
                "printf 'repository-python:%s\\n' \"$*\"\n",
                encoding="utf-8",
            )
            python.chmod(0o755)
            coverage = repository / "scripts/coverage.sh"
            coverage.write_text(
                "#!/usr/bin/env bash\nset -euo pipefail\n"
                "python3 sentinel > selected-python.txt\n",
                encoding="utf-8",
            )
            coverage.chmod(0o755)

            result = _run(
                str(env.context / "QA/qa-project.sh"),
                "DP-API",
                cwd=env.context,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(
                (repository / "selected-python.txt").read_text(encoding="utf-8"),
                "repository-python:sentinel\n",
            )
            self.assertFalse((python.parent / "python3").exists())

    @unittest.skipUnless(os.name == "nt", "Windows python3 shim is Windows-specific")
    def test_windows_non_python_repository_uses_context_python_for_qa_tooling(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d), context_venv_layout="Scripts")
            repository = env.suite / "DP/DP-API"
            coverage = repository / "scripts/coverage.sh"
            coverage.write_text(
                "#!/usr/bin/env bash\nset -euo pipefail\n"
                "python3 -c \"print('tooling-python')\" > tooling-python.txt\n"
                "printf '%s\\n' \"${VIRTUAL_ENV-unset}\" > child-virtual-env.txt\n",
                encoding="utf-8",
            )
            coverage.chmod(0o755)

            result = _run(
                str(env.context / "QA/qa-project.sh"),
                "DP-API",
                cwd=env.context,
                check=False,
                env=env.inherited_context_environment(),
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(
                (repository / "tooling-python.txt").read_text(encoding="utf-8"),
                "tooling-python\n",
            )
            self.assertEqual(
                (repository / "child-virtual-env.txt").read_text(encoding="utf-8").strip(),
                "unset",
            )
            self.assertIn("-c print('tooling-python')", env.context_python_log())
            self.assertFalse((repository / ".venv").exists())

    @unittest.skipUnless(os.name == "nt", "MSYS path conversion is Windows-specific")
    def test_msys_docker_shim_preserves_container_paths_and_converts_host_sources(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            repository = env.suite / "DP/DP-API"
            docker = repository / ".venv/Scripts/docker"
            docker.parent.mkdir(parents=True)
            docker.write_text(
                "#!/usr/bin/env bash\n"
                "printf 'flags:%s:%s\\n' \"${MSYS_NO_PATHCONV-}\" \"${MSYS2_ARG_CONV_EXCL-}\" >> docker-args.txt\n"
                "printf '<%s>\\n' \"$@\" >> docker-args.txt\n",
                encoding="utf-8",
            )
            docker.chmod(0o755)
            coverage = repository / "scripts/coverage.sh"
            coverage.write_text(
                "#!/usr/bin/env bash\nset -euo pipefail\n"
                "docker run -v \"$PWD:/qa-output\" -w /workspace image /app /usr/src /usr/src/app /flyway/conf/flyway.conf\n"
                "docker cp box:/tmp/coverage.xml \"$PWD/coverage.xml\"\n"
                "docker rm -f sbm-api-qa-coverage\n",
                encoding="utf-8",
            )
            coverage.chmod(0o755)

            result = _run(
                str(env.context / "QA/qa-project.sh"),
                "DP-API",
                cwd=env.context,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            log = (repository / "docker-args.txt").read_text(encoding="utf-8")
            self.assertIn("flags:1:*", log)
            self.assertRegex(log, r"<[A-Z]:/.+:/qa-output>")
            for container_path in (
                "/workspace",
                "/app",
                "/usr/src",
                "/usr/src/app",
                "/flyway/conf/flyway.conf",
            ):
                self.assertIn(f"<{container_path}>", log)
                self.assertNotIn(f"Git{container_path}", log)
            self.assertRegex(log, r"<[A-Z]:/.+/coverage\.xml>")
            self.assertEqual(
                log.splitlines()[-4:],
                ["flags::", "<rm>", "<-f>", "<sbm-api-qa-coverage>"],
            )

    def test_repository_without_venv_runs_shell_qa_without_python(self):
        with tempfile.TemporaryDirectory() as d:
            env = QAEnvironment(Path(d))
            repository = env.suite / "DP/DP-API"
            coverage = repository / "scripts/coverage.sh"
            coverage.write_text(
                "#!/usr/bin/env bash\nset -euo pipefail\n"
                "[[ ! -d .venv ]]\n"
                "printf 'shell-only\\n' > shell-only.txt\n",
                encoding="utf-8",
            )
            coverage.chmod(0o755)

            result = _run(
                str(env.context / "QA/qa-project.sh"),
                "DP-API",
                cwd=env.context,
                check=False,
                env=env.inherited_context_environment(),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                (repository / "shell-only.txt").read_text(encoding="utf-8"),
                "shell-only\n",
            )


if __name__ == "__main__":
    unittest.main()
