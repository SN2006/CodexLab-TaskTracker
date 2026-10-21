import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from app import store
from app.service import complete_task, get_task, list_tasks


class TaskCompletionTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "tasks.json"
        self.tasks = [
            {"id": 1, "title": "First", "description": "", "status": "open", "completed_at": None},
            {"id": 2, "title": "Second", "description": "", "status": "open", "completed_at": None},
        ]
        self.path.write_text(json.dumps(self.tasks), encoding="utf-8")
        patcher = patch.object(store, "DATA_FILE", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_completion_persists_on_fresh_read(self):
        before = datetime.now(timezone.utc)
        completed = complete_task(1)
        after = datetime.now(timezone.utc)

        self.assertEqual(completed["status"], "done")
        timestamp = datetime.fromisoformat(completed["completed_at"])
        self.assertLessEqual(before, timestamp)
        self.assertLessEqual(timestamp, after)
        self.assertEqual(get_task(1), completed)
        self.assertEqual(json.loads(self.path.read_text()), [completed, self.tasks[1]])
        self.assertEqual(list_tasks(status="done"), [completed])
        self.assertEqual(list_tasks(status="open"), [self.tasks[1]])

    def test_missing_task_does_not_modify_storage(self):
        before = self.path.read_bytes()
        self.assertIsNone(complete_task(999))
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
