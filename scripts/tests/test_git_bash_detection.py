from __future__ import annotations

import unittest
from unittest import mock

from scripts.tests import _git_bash


class GitBashDetectionTests(unittest.TestCase):
    def test_posix_ignores_git_for_windows_environment(self):
        for git_bash in ("", r"E:\Programs Files\Git\bin\bash.exe"):
            with (
                self.subTest(git_bash=git_bash),
                mock.patch.object(_git_bash, "_is_windows", return_value=False),
                mock.patch.object(_git_bash.shutil, "which", return_value="/bin/bash") as which,
                mock.patch.object(_git_bash, "_exists") as windows_exists,
                mock.patch.object(_git_bash, "_windows_python_shim") as windows_shim,
                mock.patch.dict(_git_bash.os.environ, {
                    "PATH": "/usr/bin:/bin:/opt/native tools/bin",
                    "GIT_BASH": git_bash,
                    "ProgramFiles": r"E:\Programs Files",
                }, clear=True),
            ):
                before = dict(_git_bash.os.environ)
                command = _git_bash.bash_command("script.sh", "argument")
                self.assertEqual(command, ["/bin/bash", _git_bash.bash_path("script.sh"), "argument"])
                which.assert_called_once_with("bash")
                windows_exists.assert_not_called()
                windows_shim.assert_not_called()
                self.assertEqual(dict(_git_bash.os.environ), before)

    @staticmethod
    def _which(mapping):
        return lambda executable: mapping.get(executable)

    def test_derives_custom_installation_from_git_executable(self):
        files = {r"E:\Programs Files\Git\bin\bash.exe".casefold()}
        which = self._which({"git.exe": r"E:\Programs Files\Git\cmd\git.exe"})
        with (
            mock.patch.object(_git_bash, "_is_windows", return_value=True),
            mock.patch.object(_git_bash.shutil, "which", side_effect=which),
            mock.patch.object(
                _git_bash,
                "_exists",
                side_effect=lambda path: str(path).casefold() in files,
            ),
            mock.patch.dict(_git_bash.os.environ, {}, clear=True),
        ):
            self.assertEqual(
                _git_bash.bash_executable(),
                r"E:\Programs Files\Git\bin\bash.exe",
            )

    def test_msystem_prefers_path_bash(self):
        bash = r"E:\Portable Git\usr\bin\bash.exe"
        which = self._which({"bash.exe": bash, "git.exe": r"Z:\Elsewhere\git.exe"})
        with (
            mock.patch.object(_git_bash, "_is_windows", return_value=True),
            mock.patch.object(_git_bash.shutil, "which", side_effect=which),
            mock.patch.object(_git_bash, "_exists", return_value=True),
            mock.patch.dict(_git_bash.os.environ, {"MSYSTEM": "MINGW64"}, clear=True),
        ):
            self.assertEqual(_git_bash.bash_executable(), bash)

    def test_rejects_system32_bash_and_uses_git_for_windows(self):
        git_bash = r"E:\Programs Files\Git\bin\bash.exe"
        files = {
            r"C:\Windows\System32\bash.exe".casefold(),
            git_bash.casefold(),
        }
        which = self._which({
            "bash.exe": r"C:\Windows\System32\bash.exe",
            "bash": r"C:\Windows\System32\bash.exe",
            "git.exe": r"E:\Programs Files\Git\cmd\git.exe",
        })
        with (
            mock.patch.object(_git_bash, "_is_windows", return_value=True),
            mock.patch.object(_git_bash.shutil, "which", side_effect=which),
            mock.patch.object(
                _git_bash,
                "_exists",
                side_effect=lambda path: str(path).casefold() in files,
            ),
            mock.patch.dict(_git_bash.os.environ, {"MSYSTEM": "MINGW64"}, clear=True),
        ):
            self.assertEqual(_git_bash.bash_executable(), git_bash)

    def test_converts_windows_script_path_for_git_bash_command(self):
        with (
            mock.patch.object(_git_bash, "_is_windows", return_value=True),
            mock.patch.object(
                _git_bash.Path,
                "resolve",
                return_value=_git_bash.Path("E:/Programs Files/context/script.sh"),
            ),
            mock.patch.object(
                _git_bash, "bash_executable", return_value=r"E:\Git\bin\bash.exe"
            ),
            mock.patch.object(
                _git_bash, "_windows_python_shim", return_value="/e/python-lf"
            ),
        ):
            self.assertEqual(
                _git_bash.bash_command("script.sh", "argument"),
                [
                    r"E:\Git\bin\bash.exe",
                    "-c",
                    'export PATH="$1${PATH:+:$PATH}"; exec bash "$2" "${@:3}"',
                    "context-test",
                    "/e/python-lf",
                    "/e/Programs Files/context/script.sh",
                    "argument",
                ],
            )

        with (
            mock.patch.object(_git_bash, "_is_windows", return_value=False),
            mock.patch.object(_git_bash, "bash_executable", return_value="/bin/bash"),
            mock.patch.object(
                _git_bash.Path,
                "resolve",
                return_value=_git_bash.Path("/tmp/context/script.sh"),
            ),
        ):
            self.assertEqual(
                _git_bash.bash_command("script.sh", "argument"),
                ["/bin/bash", "/tmp/context/script.sh", "argument"],
            )


if __name__ == "__main__":
    unittest.main()
