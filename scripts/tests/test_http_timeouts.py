from __future__ import annotations

import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]


class HttpTimeoutContractTests(unittest.TestCase):
    def test_context_deploy_allows_long_synchronous_export(self) -> None:
        content = (
            CONTEXT_ROOT / "scripts/context-deploy.sh"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'AI_ASSISTANT_MAX_TIME_SECONDS="${AI_ASSISTANT_MAX_TIME_SECONDS:-1800}"',
            content,
        )
        self.assertIn('if [[ "${CURL_STATUS}" -eq 28 ]]', content)
        self.assertIn("El backend puede continuar procesando", content)

    def test_documentation_deploy_allows_long_synchronous_export(self) -> None:
        content = (
            CONTEXT_ROOT / "scripts/documentation-deploy.sh"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'AI_ASSISTANT_MAX_TIME_SECONDS="${AI_ASSISTANT_MAX_TIME_SECONDS:-1800}"',
            content,
        )
        self.assertIn('if [[ "${CURL_STATUS}" -eq 28 ]]', content)
        self.assertIn("El backend puede continuar procesando", content)

    def test_all_http_orchestration_scripts_have_bounded_timeouts(self) -> None:
        for relative in (
            "scripts/context-deploy.sh",
            "scripts/context-upgrade.sh",
            "scripts/documentation-deploy.sh",
            "scripts/documentation-upgrade.sh",
        ):
            with self.subTest(script=relative):
                content = (CONTEXT_ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("AI_ASSISTANT_CONNECT_TIMEOUT_SECONDS", content)
                self.assertIn("AI_ASSISTANT_MAX_TIME_SECONDS", content)
                self.assertIn("--connect-timeout", content)
                self.assertIn("--max-time", content)
                self.assertIn("^https?://", content)


if __name__ == "__main__":
    unittest.main()
