from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
STUB = r'''#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
root = Path(os.environ['TEST_CONTEXT'])
url = next(a for a in args if a.startswith(('http://', 'https://')))
with (root / 'calls.jsonl').open('a') as stream:
    stream.write(json.dumps(args) + '\n')
output = Path(args[args.index('--output') + 1])
status = '200'
if url.endswith('/contexts/contract'):
    payload = {'canonical_projects': {'sbm-suite-context': {}}}
    if os.environ.get('BAD_REGISTRY'):
        payload = {'canonical_projects': {}}
elif url.endswith('/documentation/upgrade'):
    target = root / 'documentation/pages/guide.md'
    backup = root / 'backup/test/guide.md'
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(target.read_text())
    target.write_text('# Updated\n')
    if not os.environ.get('KEEP_ZIP'):
        (root / 'documentation/input/documentation-upgrade.zip').unlink()
    payload = {'workflow': 'documentation-upgrade', 'project_name': 'sbm-suite-context',
               'updated_files': ['documentation/pages/guide.md'],
               'backup_directory': 'context/backup/test', 'input_cleaned': True}
    if os.environ.get('BAD_UPGRADE'):
        payload['workflow'] = 'wrong'
else:
    assert url.endswith('/api/notion/documentation/sync'), url
    assert not list((root / 'documentation/input').iterdir()), 'cleanup must precede sync'
    assert [p.name for p in (root / 'documentation/output').iterdir()] == ['documentation-upgrade-response.json']
    assert (root / 'documentation/pages/guide.md').read_text() == '# Updated\n'
    assert (root / 'backup/test/guide.md').exists()
    code = int(os.environ.get('SYNC_CURL_CODE', '0'))
    if code:
        sys.exit(code)
    output.write_text(os.environ['SYNC_BODY'])
    print(os.environ.get('SYNC_HTTP', '200'), end='')
    sys.exit(0)
output.write_text(json.dumps(payload))
print(status, end='')
'''


class DocumentationUpgradeNotionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        suite = Path(self.temp.name)
        self.root = suite / 'context'
        scripts = self.root / 'scripts'
        scripts.mkdir(parents=True)
        for name in ('documentation-upgrade.sh', 'resolve-upgrade-input.py',
                     'validate_documentation_upgrade.py', 'cleanup-exchange.sh'):
            shutil.copy2(CONTEXT_ROOT / 'scripts' / name, scripts / name)
        self.bin = suite / 'bin'
        self.bin.mkdir()
        curl = self.bin / 'curl'
        curl.write_text(STUB)
        curl.chmod(0o755)
        (self.root / 'documentation/pages').mkdir(parents=True)
        (self.root / 'documentation/pages/guide.md').write_text('# Original\n')
        (self.root / 'documentation/input').mkdir()
        (self.root / 'documentation/output').mkdir()
        (self.root / 'documentation/output/stale.zip').write_text('old')
        self.make_zip()
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(('SBM_', 'AI_ASSISTANT_', 'SYNC_', 'BAD_'))}
        self.env.update(PATH=f'{self.bin}:{os.environ["PATH"]}',
                        TEST_CONTEXT=str(self.root), AI_ASSISTANT_URL='https://assistant.test',
                        SYNC_BODY=json.dumps(self.payload()))
        self.env_file = self.root / '.env.dev'
        self.env_file.write_text('SBM_UTIL_BASE_URL="https://util.test/"\nSBM_SERVICE_TOKEN="test-secret"\n')

    @staticmethod
    def payload(**changes):
        return dict(project='SBM-SUITE', discovered=3, created=1, updated=1, unchanged=1) | changes

    def make_zip(self):
        with ZipFile(self.root / 'documentation/input/documentation-upgrade.zip', 'w') as archive:
            archive.writestr('manifest.json', json.dumps({
                'project_name': 'sbm-suite-context', 'workflow': 'documentation-upgrade',
                'updated_files': ['documentation/pages/guide.md']}))
            archive.writestr('documentation/pages/guide.md', '# Updated\n')

    def run_script(self, **env):
        result = subprocess.run(['bash', str(self.root / 'scripts/documentation-upgrade.sh')],
                                env=self.env | env, text=True, capture_output=True, timeout=15)
        self.assertNotIn('test-secret', result.stdout + result.stderr)
        return result

    def calls(self):
        path = self.root / 'calls.jsonl'
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def assert_sync_failed(self, result):
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('Documentación actualizada correctamente.', result.stdout)
        self.assertIn('ERROR:', result.stderr)
        self.assertEqual((self.root / 'documentation/pages/guide.md').read_text(), '# Updated\n')
        call = self.calls()[-1]
        self.assertFalse(Path(call[call.index('--output') + 1]).exists())
        self.assertTrue((self.root / 'documentation/.notion-sync-pending').exists())
        self.assertFalse((self.root / 'documentation/input/documentation-upgrade.zip').exists())

    def test_success_request_and_cleanup(self):
        result = self.run_script(SBM_UTIL_CONNECT_TIMEOUT_SECONDS='7', SBM_UTIL_MAX_TIME_SECONDS='240')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('discovered=3/created=1/updated=1/unchanged=1', result.stdout)
        self.assertTrue(result.stdout.endswith('Documentación actualizada correctamente.\n'))
        call = self.calls()[-1]
        self.assertIn('https://util.test/api/notion/documentation/sync', call)
        self.assertIn('X-SBM-Service-Token: test-secret', call)
        self.assertIn('Content-Type: application/json', call)
        self.assertEqual(call[call.index('--request') + 1], 'POST')
        self.assertEqual(call[call.index('--connect-timeout') + 1], '7')
        self.assertEqual(call[call.index('--max-time') + 1], '240')
        self.assertEqual(json.loads(call[call.index('--data-binary') + 1]),
                         {'project': 'SBM-SUITE', 'documentationPath': 'sbm-suite'})
        self.assertFalse((self.root / 'documentation/.notion-sync-pending').exists())
        self.assertFalse(Path(call[call.index('--output') + 1]).exists())

    def test_valid_counters_and_2xx(self):
        for counts in ((3, 0, 0), (0, 3, 0), (0, 0, 3), (0, 0, 0)):
            with self.subTest(counts=counts):
                self.make_zip()
                created, updated, unchanged = counts
                result = self.run_script(SYNC_HTTP='201', SYNC_BODY=json.dumps(self.payload(
                    discovered=sum(counts), created=created, updated=updated, unchanged=unchanged)))
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_transport_and_http_failures_allow_retry_without_zip(self):
        for settings in ({'SYNC_CURL_CODE': '7'}, {'SYNC_CURL_CODE': '28'},
                         {'SYNC_HTTP': '401'}, {'SYNC_HTTP': '403'}, {'SYNC_HTTP': '500'},
                         {'SYNC_HTTP': '302'}):
            with self.subTest(settings=settings):
                self.make_zip()
                result = self.run_script(**settings)
                self.assert_sync_failed(result)
                self.assertIn(next(iter(settings.values())), result.stderr)
                before = len(self.calls())
                retry = self.run_script(SYNC_BODY=json.dumps(self.payload(created=0, updated=0, unchanged=3)))
                self.assertEqual(retry.returncode, 0, retry.stderr)
                self.assertEqual(len(self.calls()), before + 1)
                self.assertIn('unchanged=3', retry.stdout)

    def test_invalid_response_contracts(self):
        payloads = ['not JSON test-secret', '[]', 'null', '{}',
                    json.dumps(self.payload(project='wrong')),
                    json.dumps(self.payload(discovered=4))]
        for field in ('discovered', 'created', 'updated', 'unchanged'):
            missing = self.payload()
            del missing[field]
            payloads.append(json.dumps(missing))
            for value in (-1, True, 1.0, '1', None):
                payloads.append(json.dumps(self.payload(**{field: value})))
        for body in payloads:
            with self.subTest(body=body):
                self.make_zip()
                self.assert_sync_failed(self.run_script(SYNC_BODY=body))

    def test_configuration_validation_before_upgrade(self):
        for settings in ({'SBM_UTIL_BASE_URL': 'ftp://invalid'},
                         {'SBM_UTIL_CONNECT_TIMEOUT_SECONDS': '0'},
                         {'SBM_UTIL_MAX_TIME_SECONDS': '-1'},
                         {'SBM_UTIL_MAX_TIME_SECONDS': '1.5'}):
            with self.subTest(settings=settings):
                self.assertNotEqual(self.run_script(**settings).returncode, 0)
                self.assertEqual(self.calls(), [])
        for content in ('SBM_SERVICE_TOKEN=test-secret\n', 'SBM_UTIL_BASE_URL=https://util.test\n'):
            self.env_file.write_text(content)
            self.assertNotEqual(self.run_script().returncode, 0)
            self.assertEqual(self.calls(), [])

    def test_process_environment_overrides_context(self):
        result = self.run_script(SBM_UTIL_BASE_URL='https://override.test', SBM_SERVICE_TOKEN='override-token')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('https://override.test/api/notion/documentation/sync', self.calls()[-1])
        self.assertIn('X-SBM-Service-Token: override-token', self.calls()[-1])

    def test_assistant_fallback_does_not_change_util_configuration(self):
        del self.env['AI_ASSISTANT_URL']
        fallback = self.root.parent / 'SBM/sbm-ai-assistant/.env.dev'
        fallback.parent.mkdir(parents=True)
        fallback.write_text('AI_ASSISTANT_URL=https://fallback.test\n'
                            'SBM_UTIL_BASE_URL=https://wrong.test\nSBM_SERVICE_TOKEN=wrong\n')
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('https://fallback.test/contexts/contract', self.calls()[0])
        self.assertIn('https://util.test/api/notion/documentation/sync', self.calls()[-1])
        self.assertIn('X-SBM-Service-Token: test-secret', self.calls()[-1])

    def test_local_failures_do_not_sync(self):
        for settings in ({'BAD_REGISTRY': '1'}, {'BAD_UPGRADE': '1'}, {'KEEP_ZIP': '1'}):
            with self.subTest(settings=settings):
                self.make_zip()
                result = self.run_script(**settings)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(any(any('/api/notion/' in arg for arg in call) for call in self.calls()))
                self.assertFalse((self.root / 'documentation/.notion-sync-pending').exists())

    def test_invalid_zip_does_not_contact_backends(self):
        (self.root / 'documentation/input/documentation-upgrade.zip').write_bytes(b'invalid')
        self.assertNotEqual(self.run_script().returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_new_invalid_upgrade_preserves_previous_retry(self):
        self.assert_sync_failed(self.run_script(SYNC_HTTP='500'))
        for settings in ({'BAD_REGISTRY': '1'}, {'BAD_UPGRADE': '1'}, {'KEEP_ZIP': '1'}):
            with self.subTest(settings=settings):
                self.make_zip()
                before = len(self.calls())
                result = self.run_script(**settings)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue((self.root / 'documentation/.notion-sync-pending').exists())
                self.assertNotIn('Documentación actualizada correctamente.', result.stdout)
                self.assertFalse(any(any('/api/notion/' in arg for arg in call)
                                     for call in self.calls()[before:]))

    def test_pending_with_new_upgrade_and_successful_sync_removes_marker(self):
        self.assert_sync_failed(self.run_script(SYNC_HTTP='500'))
        self.make_zip()
        before = len(self.calls())
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls()[before:]
        self.assertEqual(len(calls), 3)
        for call, endpoint in zip(calls, ('/contexts/contract', '/documentation/upgrade',
                                         '/api/notion/documentation/sync')):
            self.assertTrue(any(arg.endswith(endpoint) for arg in call))
        self.assertFalse((self.root / 'documentation/.notion-sync-pending').exists())
        self.assertIn('Documentación actualizada correctamente.', result.stdout)

    def test_pending_with_new_upgrade_and_failed_sync_preserves_marker(self):
        self.assert_sync_failed(self.run_script(SYNC_HTTP='500'))
        for settings in ({'SYNC_CURL_CODE': '7'}, {'SYNC_CURL_CODE': '28'},
                         {'SYNC_HTTP': '500'}, {'SYNC_BODY': 'invalid'},
                         {'SYNC_BODY': json.dumps(self.payload(discovered=4))}):
            with self.subTest(settings=settings):
                self.make_zip()
                before = len(self.calls())
                self.assert_sync_failed(self.run_script(**settings))
                calls = self.calls()[before:]
                self.assertEqual(len(calls), 3)
                for call, endpoint in zip(calls, ('/contexts/contract', '/documentation/upgrade',
                                                 '/api/notion/documentation/sync')):
                    self.assertTrue(any(arg.endswith(endpoint) for arg in call))

    def test_repeated_upgrade_publishes_same_identity(self):
        self.assertEqual(self.run_script().returncode, 0)
        first = self.calls()[-1]
        self.make_zip()
        result = self.run_script(SYNC_BODY=json.dumps(self.payload(created=0, updated=0, unchanged=3)))
        self.assertEqual(result.returncode, 0, result.stderr)
        second = self.calls()[-1]
        self.assertEqual(first[first.index('--data-binary') + 1], second[second.index('--data-binary') + 1])
        self.assertIn('unchanged=3', result.stdout)


if __name__ == '__main__':
    unittest.main()
