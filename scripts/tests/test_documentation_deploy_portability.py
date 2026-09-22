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

from scripts.tests._git_bash import bash_executable, bash_path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]


class DocumentationDeployPortabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.suite = Path(self.temp.name) / "SBM-SUITE"
        self.context = self.suite / "context"
        scripts = self.context / "scripts"
        qa_output = self.context / "QA" / "output"
        documentation = self.context / "documentation"
        for directory in (
            scripts,
            qa_output,
            documentation / "input",
            documentation / "output",
        ):
            directory.mkdir(parents=True, exist_ok=True)

        shutil.copy2(
            CONTEXT_ROOT / "scripts" / "documentation-deploy.sh",
            scripts / "documentation-deploy.sh",
        )
        (self.context / ".env.dev").write_text(
            "DOPPLER_PROJECT=sbm-suite-context\n"
            "AI_ASSISTANT_URL=https://assistant.test\n"
            "SBM_SUITE_ROOT=..\n",
            encoding="utf-8",
        )
        (documentation / "FORMAT_CONTEXT.md").write_text("fixture\n", encoding="utf-8")
        (documentation / "SYS_PROMPT.md").write_text("fixture\n", encoding="utf-8")
        (qa_output / "finalization-gate.json").write_text(
            json.dumps(
                {
                    "branch": "FEATURE-standardizes-suite-governance",
                    "status": "passed",
                    "mode": "full-suite-with-sonar",
                    "objectives": ["OBJ-CTX-002", "OBJ-CTX-003"],
                    "state_sha256": "a" * 64,
                }
            ),
            encoding="utf-8",
        )

        self._write_python_stub(
            "objective-git-state.py",
            "import json, sys\n"
            "from pathlib import Path\n"
            "Path(__file__).resolve().parents[1].joinpath('objective-args.json').write_text(json.dumps(sys.argv[1:]))\n",
        )
        self._write_python_stub(
            "workflow-state.py",
            "import json, sys\n"
            "from pathlib import Path\n"
            "Path(__file__).resolve().parents[1].joinpath('workflow-args.json').write_text(json.dumps(sys.argv[1:]))\n",
        )
        self._write_python_stub(
            "documentation_reconciliation.py",
            "import json, sys\n"
            "from pathlib import Path\n"
            "output = Path(sys.argv[sys.argv.index('--output') + 1])\n"
            "output.write_text(json.dumps({'synchronized': True, 'summary': 'ok'}))\n",
        )
        (scripts / "suite-repositories.py").write_text("# fixture\n", encoding="utf-8")
        self._write_shell_stub(
            "objective-branches.sh",
            "root=$(cd \"$(dirname \"${BASH_SOURCE[0]}\")/..\" && pwd)\n"
            "printf '%s\\n' \"$@\" > \"${root}/branch-args.txt\"\n",
        )
        self._write_shell_stub(
            "project-tree.sh",
            "root=$(cd \"$(dirname \"${BASH_SOURCE[0]}\")/..\" && pwd)\n"
            "printf 'SBM-SUITE/context\\n' > \"${root}/project-tree.txt\"\n",
        )

        self.bin = self.suite / "bin"
        self.bin.mkdir()
        python3 = self.bin / "python3"
        python3.write_text(
            "#!/usr/bin/env bash\n"
            f"exec {shlex.quote(bash_path(sys.executable))} \"$@\"\n",
            encoding="utf-8",
            newline="\n",
        )
        python3.chmod(0o755)

    def _write_python_stub(self, name: str, body: str) -> None:
        path = self.context / "scripts" / name
        path.write_text(body, encoding="utf-8", newline="\n")

    def _write_shell_stub(self, name: str, body: str) -> None:
        path = self.context / "scripts" / name
        path.write_text("#!/usr/bin/env bash\nset -euo pipefail\n" + body, encoding="utf-8", newline="\n")
        path.chmod(0o755)

    def test_native_windows_python_control_values_have_no_carriage_return(self) -> None:
        script = self.context / "scripts" / "documentation-deploy.sh"
        command = [bash_executable(), bash_path(script)]
        if os.name == "nt":
            command = [
                bash_executable(),
                "-c",
                'export PATH="$1${PATH:+:$PATH}"; exec bash "$2"',
                "documentation-deploy-test",
                bash_path(self.bin),
                bash_path(script),
            ]
        result = subprocess.run(
            command,
            env=os.environ.copy(),
            capture_output=True,
            timeout=20,
        )

        self.assertEqual(
            result.returncode,
            0,
            result.stderr.decode("utf-8", errors="replace"),
        )
        branch_args = (self.context / "branch-args.txt").read_text().splitlines()
        objective_args = json.loads((self.context / "objective-args.json").read_text())
        workflow_args = json.loads((self.context / "workflow-args.json").read_text())
        control_values = branch_args + objective_args + workflow_args
        self.assertFalse(any("\r" in value for value in control_values), control_values)
        self.assertEqual(branch_args, ["verify", "FEATURE-standardizes-suite-governance"])
        self.assertEqual(objective_args[-2:], ["OBJ-CTX-002", "OBJ-CTX-003"])
        self.assertEqual(workflow_args[workflow_args.index("--expect") + 1], "a" * 64)


if __name__ == "__main__":
    unittest.main()
