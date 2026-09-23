from __future__ import annotations

import hashlib
import os
import re
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

HELPER = Path(__file__).resolve().parents[2] / "scripts" / "sonar-scanner-common.sh"


class SonarScannerArchitectureTests(unittest.TestCase):
    def _run_helper(self, docker_script: str, shell_code: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_bin = Path(tmpdir) / "bin"
            fake_bin.mkdir(parents=True, exist_ok=True)
            docker_path = fake_bin / "docker"
            docker_path.write_text(docker_script, encoding="utf-8")
            docker_path.chmod(0o755)

            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
            command = ["bash", "-c", f"source {shlex.quote(str(HELPER))}; {shell_code}"]
            return subprocess.run(command, check=False, text=True, capture_output=True, env=env)

    def test_amd64_detection_uses_native_linux_amd64(self):
        script = """#!/usr/bin/env bash
if [[ "$1" == "version" ]]; then
  echo "amd64"
  exit 0
fi
if [[ "$1" == "info" ]]; then
  echo "amd64"
  exit 0
fi
"""
        result = self._run_helper(script, 'echo "$(sbm_sonar_detect_arch)"; echo "$(sbm_sonar_platform)"')
        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout.strip().splitlines()
        self.assertEqual(output[0], "amd64")
        self.assertEqual(output[1], "linux/amd64")

    def test_arm64_detection_uses_native_linux_arm64_without_qemu(self):
        script = """#!/usr/bin/env bash
if [[ "$1" == "version" ]]; then
  echo "arm64"
  exit 0
fi
if [[ "$1" == "info" ]]; then
  echo "arm64"
  exit 0
fi
"""
        result = self._run_helper(script, 'echo "$(sbm_sonar_detect_arch)"; echo "$(sbm_sonar_platform)"')
        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout.strip().splitlines()
        self.assertEqual(output[0], "arm64")
        self.assertEqual(output[1], "linux/arm64")
        self.assertNotIn("qemu-x86_64", "\n".join(output))

    def test_cache_dir_is_arch_specific(self):
        script = """#!/usr/bin/env bash
if [[ "$1" == "version" ]]; then
  echo "arm64"
  exit 0
fi
if [[ "$1" == "info" ]]; then
  echo "arm64"
  exit 0
fi
"""
        result = self._run_helper(script, 'echo "$(sbm_sonar_cache_dir /tmp/project)"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("/tmp/project/.sonar/cache/arm64", result.stdout.strip())

    def test_timeout_cleans_the_container(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_bin = Path(tmpdir) / "bin"
            fake_bin.mkdir(parents=True, exist_ok=True)
            log_file = Path(tmpdir) / "docker.log"
            docker_path = fake_bin / "docker"
            docker_path.write_text(
                "#!/usr/bin/env bash\n"
                "if [[ \"$1\" == \"version\" ]]; then\n"
                "  echo \"arm64\"\n"
                "  exit 0\n"
                "fi\n"
                "if [[ \"$1\" == \"rm\" ]]; then\n"
                "  echo \"rm:$2 $3\" >> \"${FAKE_DOCKER_LOG}\"\n"
                "  exit 0\n"
                "fi\n"
                "if [[ \"$1\" == \"run\" ]]; then\n"
                "  echo \"run:start\" >> \"${FAKE_DOCKER_LOG}\"\n"
                "  exec sleep 30\n"
                "  exit 0\n"
                "fi\n"
                "exit 0\n",
                encoding="utf-8",
            )
            docker_path.chmod(0o755)

            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
            env["FAKE_DOCKER_LOG"] = str(log_file)
            command = [
                "bash",
                "-c",
                f"source {shlex.quote(str(HELPER))}; SONAR_SCANNER_TIMEOUT_SECONDS=1; sbm_sonar_run docker run --rm --name sbm-sonar-arm64-tests --platform linux/arm64 busybox true",
            ]
            result = subprocess.run(command, check=False, text=True, capture_output=True, env=env)
            self.assertEqual(result.returncode, 124, result.stderr)
            self.assertIn("rm:-f sbm-sonar-arm64-tests", log_file.read_text(encoding="utf-8"))


    def test_image_lifecycle(self):
        expected_hash = hashlib.sha256((HELPER.parents[1] / "docker/sonar-scanner/Dockerfile").read_bytes()).hexdigest()
        for arch in ("amd64", "arm64"):
            for state in ("existing", "missing", "stale", "unlabelled", "wrong", "wrong_after_build", "bad_hash_after_build", "build_failure"):
                with self.subTest(arch=arch, state=state), tempfile.TemporaryDirectory() as tmp:
                    state_file = shlex.quote(str(Path(tmp) / "built"))
                    script = f"""#!/usr/bin/env bash
case "$1" in
  version) echo {arch} ;;
  image)
    if [[ "{state}" != existing && "{state}" != wrong && "{state}" != stale && "{state}" != unlabelled && ! -f {state_file} ]]; then exit 1; fi
    if [[ "$3" == --format ]]; then
      if [[ "$4" == *Architecture* ]]; then
        if [[ "{state}" == wrong* ]]; then echo linux/invalid; else echo linux/{arch}; fi
      elif [[ "{state}" == bad_hash_after_build ]]; then echo invalid
      elif [[ -f {state_file} || "{state}" == existing || "{state}" == wrong ]]; then cat {state_file} 2>/dev/null || echo {expected_hash}
      elif [[ "{state}" == stale ]]; then echo outdated
      else echo '<no value>'
      fi
    fi ;;
  build)
    echo "BUILD:$*" >&2
    [[ "{state}" != build_failure ]] || exit 9
    while [[ "$#" -gt 0 ]]; do
      if [[ "$1" == --label ]]; then
        printf '%s' "${{2#*=}}" > {state_file}
        exit 0
      fi
      shift
    done
    exit 98 ;;
  *) exit 99 ;;
esac
"""
                    result = self._run_helper(
                        script,
                        'set -e; sbm_sonar_ensure_image; sbm_sonar_ensure_image; '
                        'sbm_sonar_image; sbm_sonar_cache_dir /tmp/project',
                    )
                    if state in ("wrong", "wrong_after_build", "bad_hash_after_build", "build_failure"):
                        self.assertNotEqual(result.returncode, 0)
                        if state == "bad_hash_after_build":
                            self.assertIn("Huella del Dockerfile incorrecta", result.stderr)
                        if state.startswith("wrong"):
                            self.assertIn("Arquitectura incorrecta", result.stderr)
                    else:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(result.stdout.splitlines(), [
                            f"sbm-sonar-scanner:{arch}", f"/tmp/project/.sonar/cache/{arch}",
                        ])
                    expected_builds = int(state not in ("existing", "wrong"))
                    self.assertEqual(result.stderr.count("BUILD:"), expected_builds)
                    if expected_builds:
                        self.assertIn(f"--label com.sbm.sonar-scanner.dockerfile-sha256={expected_hash}", result.stderr)
                        self.assertIn(f"--platform linux/{arch} -t sbm-sonar-scanner:{arch}", result.stderr)
                        self.assertIn(str(HELPER.parents[1] / "docker/sonar-scanner/Dockerfile"), result.stderr)

    def test_seven_consumers_use_central_helper_and_validate_before_run(self):
        suite = HELPER.parents[2]
        repos = ("DP/DP-API", "KS/KS-STORE", "SBM/sbm-ai-assistant",
                 "SBM/SBM-API", "SBM/SBM-DB", "SBM/SBM-MANAGER", "SBM/SBM-UTIL")
        for repo in repos:
            with self.subTest(repo=repo):
                script = suite / repo / "scripts/sonar-scan.sh"
                source = script.read_text()
                helper_lines = [line.strip() for line in source.splitlines() if "sonar-scanner-common.sh" in line]
                self.assertEqual(helper_lines, ['source "${SUITE_ROOT}/context/scripts/sonar-scanner-common.sh"'])
                self.assertNotIn('${SUITE_ROOT}/scripts/sonar-scanner-common.sh', source)
                self.assertNotIn("sonarsource/sonar-scanner-cli", source)
                self.assertIn('"${SONAR_CACHE_DIR}:/opt/sonar-scanner/.sonar/cache"', source)
                self.assertIn('sbm_sonar_ensure_image\nsbm_sonar_run "${docker_args[@]}"', source)
                result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_root_compatibility_wrapper_does_not_exist(self):
        wrapper = HELPER.parents[2] / "scripts/sonar-scanner-common.sh"
        self.assertFalse(os.path.lexists(wrapper), f"Wrapper residual prohibido: {wrapper}")


    def test_cache_home_and_manager_working_directory(self):
        dockerfile = HELPER.parents[1] / "docker/sonar-scanner/Dockerfile"
        self.assertIn("ENV SONAR_USER_HOME=/opt/sonar-scanner/.sonar", dockerfile.read_text())
        manager = HELPER.parents[2] / "SBM/SBM-MANAGER/scripts/sonar-scan.sh"
        source = manager.read_text()
        self.assertIn('"${PROJECT_ROOT}:/usr/src:ro"', source)
        self.assertIn('"-Dsonar.working.directory=/tmp/.scannerwork"', source)
        self.assertNotIn("mkdir -p .scannerwork", source)

    def test_dockerfile_hash_changes_with_contents(self):
        with tempfile.TemporaryDirectory(prefix="sonar hash ") as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            docker_dir = root / "docker/sonar-scanner"
            docker_dir.mkdir(parents=True)
            for content in (b"FROM debian:12-slim\n", b"FROM debian:12-slim\nENV TEST=1\n"):
                (docker_dir / "Dockerfile").write_bytes(content)
                result = self._run_helper(
                    "#!/usr/bin/env bash\nexit 99\n",
                    f"SBM_SONAR_HELPER_DIR={shlex.quote(str(root / 'scripts'))}; sbm_sonar_dockerfile_hash",
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), hashlib.sha256(content).hexdigest())

    def test_dockerfile_installs_compatible_node_and_npm_on_path(self):
        source = (HELPER.parents[1] / "docker/sonar-scanner/Dockerfile").read_text()
        version = re.search(r"^ARG NODE_VERSION=(\d+)\.(\d+)\.(\d+)$", source, re.MULTILINE)
        self.assertIsNotNone(version)
        parts = tuple(map(int, version.groups()))
        self.assertEqual(parts[0], 22)
        self.assertGreaterEqual(parts, (22, 11, 0))
        self.assertIn('https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-${NODE_ARCH}.tar.xz', source)
        self.assertIn('xz-utils', source)
        self.assertIn('tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1', source)
        self.assertIn('&& node --version', source)
        self.assertIn('&& npm --version', source)
        self.assertIn('ENV PATH="/opt/sonar-scanner/bin:/usr/local/bin:${PATH}"', source)
        self.assertIn('ARG SONAR_SCANNER_VERSION=8.1.0.6389', source)

    def test_dockerfile_selects_native_node_architecture(self):
        source = (HELPER.parents[1] / "docker/sonar-scanner/Dockerfile").read_text()
        selection = re.search(r'RUN (case .*?esac)', source, re.DOTALL).group(1)
        for arch, expected in (("amd64", "linux-x64"), ("arm64", "linux-arm64"), ("unsupported", None)):
            with self.subTest(arch=arch):
                result = subprocess.run(
                    ["bash", "-c", selection + '; printf "%s" "$NODE_ARCH"'],
                    env={**os.environ, "TARGETARCH": arch}, capture_output=True, text=True,
                )
                if expected is None:
                    self.assertNotEqual(result.returncode, 0)
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, expected)

    def test_run_preserves_exit_status(self):
        for status in (0, 7):
            result = self._run_helper("#!/usr/bin/env bash\nexit 99\n",
                                      f"sbm_sonar_run bash -c 'exit {status}'")
            self.assertEqual(result.returncode, status, result.stderr)


if __name__ == "__main__":
    unittest.main()
