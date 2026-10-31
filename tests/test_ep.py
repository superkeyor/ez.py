import ast
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
source = ast.parse((ROOT / "ez/ez.py").read_text())
FUNCTIONS = {"_ep_exe", "_ep_load", "ep"}
GLOBALS = {"_EP_FILE", "_EP_CACHE", "_EP_ERROR", "_PYSECRETS_ERROR"}
nodes = [node for node in source.body
         if (isinstance(node, ast.FunctionDef) and node.name in FUNCTIONS)
         or (isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in GLOBALS)]

# stands in for "ep run ez -- CMD": sets two secrets, then runs CMD; FAKE_EP_FAIL=1 makes it fail
FAKE_EP = """#!/bin/sh
echo "$*" >> "$FAKE_EP_LOG"
if [ -n "$FAKE_EP_FAIL" ]; then echo "no client key" >&2; exit 1; fi
if [ "$2" = "--print" ]; then echo "EMAIL=fa**"; exit 0; fi
shift 3
EMAIL=fake@example.test GSHEET_KEY='{"k": 1}' exec "$@"
"""


class EpTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="ez-ep-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.log = self.root / "calls.log"
        fake = self.root / "ep"
        fake.write_text(FAKE_EP)
        fake.chmod(0o755)
        patcher = patch.dict(os.environ, {"PATH": f"{self.root}{os.pathsep}{os.environ['PATH']}",
                                          "FAKE_EP_LOG": str(self.log)})
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in ("EMAIL", "GSHEET_KEY", "FAKE_EP_FAIL"):
            os.environ.pop(name, None)
        self.namespace = {
            "os": os, "sys": sys, "shutil": shutil, "subprocess": subprocess,
            "expanduser": os.path.expanduser, "isfile": os.path.isfile,
            "__name__": "ez.ez", "_pysecrets": None,
        }
        exec(compile(ast.Module(body=nodes, type_ignores=[]), "ez/ez.py", "exec"), self.namespace)
        self.ep = self.namespace["ep"]

    def calls(self):
        return self.log.read_text().splitlines() if self.log.exists() else []

    def test_pysecrets_comes_first_and_ep_is_not_run(self):
        self.namespace["_pysecrets"] = types.SimpleNamespace(EMAIL="old@example.test")
        os.environ["EMAIL"] = "env@example.test"
        self.assertEqual(self.ep("EMAIL"), "old@example.test")
        self.assertEqual(self.calls(), [])

    def test_ep_answers_when_pysecrets_lacks_the_name(self):
        self.namespace["_pysecrets"] = types.SimpleNamespace(OTHER="x")
        self.assertEqual(self.ep("EMAIL"), "fake@example.test")
        self.assertNotIn("EMAIL", os.environ)

    def test_ep_beats_the_environment(self):
        os.environ["EMAIL"] = "env@example.test"
        self.assertEqual(self.ep("EMAIL"), "fake@example.test")

    def test_environment_is_the_last_fallback(self):
        os.environ["FAKE_EP_FAIL"] = "1"
        os.environ["EMAIL"] = "env@example.test"
        self.assertEqual(self.ep("EMAIL"), "env@example.test")

    def test_ep_run_happens_once_per_process(self):
        self.ep("EMAIL")
        self.ep("GSHEET_KEY")
        self.ep("EMAIL")
        self.assertEqual(len(self.calls()), 1)
        self.assertTrue(self.calls()[0].startswith("run ez -- "))

    def test_json_text_comes_back_as_a_dict(self):
        self.assertEqual(self.ep("GSHEET_KEY"), {"k": 1})

    def test_missing_secret_names_the_name_and_the_ep_error(self):
        os.environ["FAKE_EP_FAIL"] = "1"
        with self.assertRaisesRegex(KeyError, "O365ID is not set.*no client key"):
            self.ep("O365ID")

    def test_text_that_only_starts_with_a_brace_stays_a_string(self):
        self.namespace["_pysecrets"] = types.SimpleNamespace(PASSWORD="{abc123", KEY='{"a": 1}')
        self.assertEqual(self.ep("PASSWORD"), "{abc123")
        self.assertEqual(self.ep("KEY"), {"a": 1})

    def test_a_broken_pysecrets_is_named_in_the_error(self):
        os.environ["FAKE_EP_FAIL"] = "1"
        self.namespace["_PYSECRETS_ERROR"] = "SyntaxError: invalid syntax"
        with self.assertRaisesRegex(KeyError, "O365ID is not set.*SyntaxError"):
            self.ep("O365ID")

    def test_ep_not_found_is_reported(self):
        self.namespace["_ep_exe"] = lambda: None
        with self.assertRaisesRegex(KeyError, "ep was not found"):
            self.ep("EMAIL")

    def test_no_name_asks_ep_to_print_hidden_values(self):
        self.assertIsNone(self.ep())
        self.assertEqual(self.calls(), ["run --print ez"])


if __name__ == "__main__":
    unittest.main()
