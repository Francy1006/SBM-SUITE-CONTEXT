from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_SOURCE = CONTEXT_ROOT / "scripts" / "objective-branches.sh"


def _run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class BranchEnvironment:
    repositories = ("context", "dp/DP-API", "sbm/SBM-API")

    def __init__(self, root: Path):
        self.root = root
        self.suite_root = root / "SBM-SUITE"
        self.context_root = self.suite_root / "context"
        self.script = self.context_root / "scripts" / "objective-branches.sh"
        self.remotes = root / "remotes"
        self.remotes.mkdir(parents=True)

        self._write_project_context(self.repositories)
        self.script.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SCRIPT_SOURCE, self.script)
        self.script.chmod(0o755)

        for repository in self.repositories:
            self._initialize_repository(repository)

    def _write_project_context(self, repositories: tuple[str, ...]) -> None:
        rows = []
        for index, repository in enumerate(repositories, start=1):
            main_context = f"{repository}/context/PROJECT_CONTEXT.md"
            if repository == "context":
                main_context = "context/PROJECT_CONTEXT.md"
            rows.append(
                f"| P{index} | purpose | active | pending | `FEATURE-old` | "
                f"`{main_context}` | N/A | N/A |"
            )
        content = (
            "# PROJECT_CONTEXT.md\n\n"
            "## 6. Project objective summaries\n\n"
            "| Project | Purpose | Active objective | Pending objectives | Branch | "
            "Main context | QA context | Documentation |\n"
            "|---|---|---|---|---|---|---|---|\n"
            + "\n".join(rows)
            + "\n\n## 7. Boundary\n"
        )
        path = self.context_root / "PROJECT_CONTEXT.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _initialize_repository(self, relative_path: str) -> None:
        repository = self.suite_root / relative_path
        repository.mkdir(parents=True, exist_ok=True)
        remote = self.remotes / (relative_path.replace("/", "-") + ".git")
        _run("git", "init", "--bare", str(remote), cwd=self.root)
        _run("git", "init", "-b", "main", cwd=repository)
        _run("git", "config", "user.email", "tests@example.com", cwd=repository)
        _run("git", "config", "user.name", "Branch Tests", cwd=repository)
        marker = repository / ".branch-test-marker"
        marker.write_text(relative_path + "\n", encoding="utf-8")
        _run("git", "add", ".", cwd=repository)
        _run("git", "commit", "-m", "initial", cwd=repository)
        _run("git", "remote", "add", "origin", str(remote), cwd=repository)
        _run("git", "push", "-u", "origin", "main", cwd=repository)

    def repository(self, relative_path: str) -> Path:
        return self.suite_root / relative_path

    def branch(self, relative_path: str) -> str:
        return _run(
            "git", "branch", "--show-current", cwd=self.repository(relative_path)
        ).stdout.strip()

    def execute(self, mode: str, branch: str) -> subprocess.CompletedProcess[str]:
        return _run(
            str(self.script),
            mode,
            branch,
            cwd=self.context_root,
            check=False,
        )


class ObjectiveBranchesTests(unittest.TestCase):
    def test_multiple_clean_repositories_support_new_local_and_remote_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = BranchEnvironment(Path(directory))
            branch = "FEATURE-cross-repository"
            extra_repository = "sbm/EXTRA"
            env._initialize_repository(extra_repository)

            _run("git", "branch", branch, "main", cwd=env.repository("context"))
            remote = env.remotes / "dp-DP-API.git"
            _run(
                "git",
                "--git-dir",
                str(remote),
                "branch",
                branch,
                "main",
                cwd=env.root,
            )

            result = env.execute("prepare", branch)

            self.assertEqual(result.returncode, 0, result.stderr)
            for repository in (*env.repositories, extra_repository):
                with self.subTest(repository=repository):
                    self.assertEqual(env.branch(repository), branch)
            tracking = _run(
                "git",
                "rev-parse",
                "--abbrev-ref",
                "--symbolic-full-name",
                "@{upstream}",
                cwd=env.repository("dp/DP-API"),
            ).stdout.strip()
            self.assertEqual(tracking, f"origin/{branch}")
            self.assertEqual(
                _run(
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    "main",
                    branch,
                    cwd=env.repository("sbm/SBM-API"),
                    check=False,
                ).returncode,
                0,
            )

    def test_dirty_repository_aborts_before_any_branch_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = BranchEnvironment(Path(directory))
            (env.repository("sbm/SBM-API") / "dirty.txt").write_text(
                "dirty\n", encoding="utf-8"
            )

            result = env.execute("prepare", "FEATURE-must-abort")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("sbm/SBM-API: working tree", result.stderr)
            self.assertIn("no se modificó ninguna branch", result.stderr)
            self.assertEqual(
                [env.branch(repository) for repository in env.repositories],
                ["main", "main", "main"],
            )

    def test_missing_or_invalid_registered_repository_aborts_globally(self) -> None:
        for invalid_kind in ("missing", "not-git"):
            with self.subTest(invalid_kind=invalid_kind):
                with tempfile.TemporaryDirectory() as directory:
                    env = BranchEnvironment(Path(directory))
                    registered = (*env.repositories, "sbm/BROKEN")
                    env._write_project_context(registered)
                    _run("git", "add", "PROJECT_CONTEXT.md", cwd=env.context_root)
                    _run(
                        "git",
                        "commit",
                        "-m",
                        "register broken repository",
                        cwd=env.context_root,
                    )
                    _run("git", "push", "origin", "main", cwd=env.context_root)
                    if invalid_kind == "not-git":
                        (env.suite_root / "sbm/BROKEN").mkdir(parents=True)

                    result = env.execute("prepare", "FEATURE-must-abort")

                    self.assertNotEqual(result.returncode, 0)
                    expected = (
                        "directorio inexistente"
                        if invalid_kind == "missing"
                        else "no es un repositorio Git válido"
                    )
                    self.assertIn(f"sbm/BROKEN: {expected}", result.stderr)
                    self.assertEqual(
                        [env.branch(repository) for repository in env.repositories],
                        ["main", "main", "main"],
                    )

    def test_verify_reports_any_repository_on_the_wrong_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = BranchEnvironment(Path(directory))
            branch = "FEATURE-verify-all"
            self.assertEqual(env.execute("prepare", branch).returncode, 0)
            _run("git", "checkout", "main", cwd=env.repository("dp/DP-API"))

            result = env.execute("verify", branch)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("dp/DP-API: branch actual 'main'", result.stderr)

    def test_scripts_and_agent_contract_embed_no_machine_absolute_paths(self) -> None:
        content = SCRIPT_SOURCE.read_text(encoding="utf-8") + (
            CONTEXT_ROOT / "INIT_CONTEXT.md"
        ).read_text(encoding="utf-8")
        self.assertNotRegex(content, r"/(?:Users|home)/[^\s]+")
        self.assertNotRegex(content, r"[A-Za-z]:\\")

    def test_progress_contract_separates_prepare_and_register_commands(self) -> None:
        contract = (CONTEXT_ROOT / "INIT_CONTEXT.md").read_text(encoding="utf-8")
        progress = contract.split(
            "17. For `implementation-progress`", maxsplit=1
        )[1].split(
            "18. Exclusively for `implementation-closure`", maxsplit=1
        )[0]
        bash_blocks = re.findall(r"```bash\n(.*?)```", progress, flags=re.DOTALL)

        self.assertIn("BASH 1 — PREPARAR BRANCHES TRANSVERSALES", progress)
        self.assertIn("BASH 2 — REGISTRAR PROGRESO", progress)
        self.assertEqual(len(bash_blocks), 2)
        self.assertIn("objective-branches.sh prepare", bash_blocks[0])
        self.assertNotIn("context-deploy.sh", bash_blocks[0])
        self.assertIn("objective-branches.sh verify", bash_blocks[1])
        self.assertIn("context-deploy.sh", bash_blocks[1])
        for forbidden in ("checkout", "pull", "fetch", "checkout -b", "switch"):
            self.assertNotIn(forbidden, bash_blocks[1])
        self.assertIn(
            "output/context-deploy-package.zip",
            progress.split("```bash", maxsplit=2)[-1],
        )

    def test_activation_reconciliation_auto_handoffs_to_progress_without_menu(self) -> None:
        contract = (CONTEXT_ROOT / "INIT_CONTEXT.md").read_text(encoding="utf-8")

        self.assertIn("#### Automatic activation-to-implementation handoff", contract)
        handoff = contract.split(
            "#### Automatic activation-to-implementation handoff", maxsplit=1
        )[1].split(
            "#### Optional transversal Git finalization for progress and closure",
            maxsplit=1,
        )[0]

        bash_blocks = re.findall(r"```bash\n(.*?)```", handoff, flags=re.DOTALL)
        self.assertEqual(len(bash_blocks), 2)
        self.assertIn("objective-branches.sh prepare", bash_blocks[0])
        self.assertNotIn("context-deploy.sh", bash_blocks[0])
        self.assertIn("objective-branches.sh verify", bash_blocks[1])
        self.assertIn("implementation-progress", bash_blocks[1])
        self.assertIn("<activated-objective-id>", bash_blocks[1])
        self.assertIn("<frozen-registry_project_name>", bash_blocks[1])
        for forbidden in ("checkout", "pull", "fetch", "checkout -b", "switch"):
            self.assertNotIn(forbidden, bash_blocks[1])

        self.assertIn(
            "never ask the user to select `Registrar progreso` after a successful activation",
            handoff,
        )
        self.assertIn(
            "If this Documentation run continues `objective-activation`, immediately render",
            contract,
        )



if __name__ == "__main__":
    unittest.main()
