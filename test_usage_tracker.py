from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path

import requests

from usage_tracker import (
    _parse_total,
    github_counter,
    local_counter,
    read_total,
    record_visit,
)


class FakeResponse:
    def __init__(self, code: int, data: dict | None = None, text: str = ""):
        self.status_code = code
        self.data = data or {}
        self.text = text
    def json(self):
        return self.data
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"error code {self.status_code}", response=self)


class FakeGitHub:
    def __init__(self):
        self.total = None
        self.sha = "v0"
        self.conflict_once = False
        self.writes = 0
        self.malformed = False
    def get(self, url, headers=None, params=None, timeout=None):
        if self.total is None:
            return FakeResponse(404)
        data = {"total_uses": self.total} if not self.malformed else {"junk": 0}
        return FakeResponse(200, {
            "type": "file", "sha": self.sha,
            "content": base64.b64encode(json.dumps(data).encode()).decode(),
        })
    def put(self, url, headers=None, json=None, timeout=None):
        if self.conflict_once:
            self.conflict_once = False
            self.total = (self.total or 0) + 1
            self.sha = f"v{self.total}"
            return FakeResponse(409)
        if self.total is not None and json.get("sha") != self.sha:
            return FakeResponse(409)
        if self.total is None and "sha" in json:
            return FakeResponse(409)
        obj = __import__("json").loads(base64.b64decode(json["content"]).decode())
        self.total = obj["total_uses"]
        self.sha = f"v{self.total}"
        self.writes += 1
        return FakeResponse(200 if "sha" in json else 201)


class CounterTests(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "GITHUB_COUNTER_TOKEN": "fake-token",
            "GITHUB_COUNTER_REPO": "test-owner/counter-data",
            "GITHUB_COUNTER_BRANCH": "main",
            "GITHUB_COUNTER_PATH": "visits.json",
            "GITHUB_COUNTER_INITIAL_TOTAL": "0",
        }

    def test_create_read_and_update(self):
        client = FakeGitHub()
        self.assertEqual(github_counter(self.settings, client=client).total, 1)
        self.assertEqual(github_counter(self.settings, client=client).total, 2)
        self.assertEqual(github_counter(self.settings, increment=False, client=client).total, 2)
        self.assertEqual(client.writes, 2)

    def test_retry_on_concurrent_visitor(self):
        client = FakeGitHub()
        client.total = 5
        client.sha = "v5"
        client.conflict_once = True
        result = github_counter(self.settings, client=client)
        self.assertEqual(result.total, 7)  # simulated concurrent visitor + our arrival
        self.assertEqual(client.total, 7)
        self.assertEqual(client.writes, 1)

    def test_previous_visits_migrated(self):
        client = FakeGitHub()
        settings = dict(self.settings, GITHUB_COUNTER_INITIAL_TOTAL="249")
        self.assertEqual(github_counter(settings, client=client).total, 250)

    def test_refuse_malformed_existing_file(self):
        client = FakeGitHub()
        client.total = 12
        client.malformed = True
        result = github_counter(self.settings, client=client)
        self.assertIsNone(result.total)
        self.assertEqual(client.writes, 0)

    def test_unconfigured_doesnt_pretend_to_have_count(self):
        self.assertIsNone(record_visit({}).total)
        self.assertIsNone(read_total({}).total)

    def test_local_counter_file_development(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "usage.json"
            self.assertEqual(local_counter(path=path).total, 1)
            self.assertEqual(local_counter(path=path).total, 2)
            self.assertEqual(local_counter(increment=False, path=path).total, 2)
            path.write_text('{"not_the_count": true}', encoding="utf-8")
            self.assertIsNone(local_counter(path=path).total)

    def test_nonnegative_schema(self):
        with self.assertRaises(ValueError):
            _parse_total({"total_uses": -1})
        with self.assertRaises(ValueError):
            _parse_total({"total_uses": "100"})


if __name__ == "__main__":
    unittest.main()
