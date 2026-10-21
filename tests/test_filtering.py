import unittest
from unittest.mock import patch

from app.schemas import TaskStatus
from app.service import list_tasks


class TaskFilteringTests(unittest.TestCase):
    def test_filters(self):
        tasks = [
            {"id": 1, "title": "Launch plan", "description": "Partner session", "status": "open"},
            {"id": 2, "title": "Report", "description": "LAUNCH recap", "status": "done"},
            {"id": 3, "title": "Other", "description": "", "status": "open"},
            {"id": 4, "title": "Straße", "description": "", "status": "done"},
        ]
        cases = [
            ({}, [1, 2, 3, 4]),
            ({"status": "open"}, [1, 3]),
            ({"status": TaskStatus.done}, [2, 4]),
            ({"q": "LaUnCh"}, [1, 2]),
            ({"q": "artner"}, [1]),
            ({"q": "STRASSE"}, [4]),
            ({"q": "missing"}, []),
            ({"status": "open", "q": "launch"}, [1]),
            ({"status": "done", "q": "launch"}, [2]),
            ({"status": "done", "q": "partner"}, []),
        ]
        with patch("app.service.load_tasks", return_value=tasks):
            for filters, expected in cases:
                with self.subTest(filters=filters):
                    self.assertEqual([task["id"] for task in list_tasks(**filters)], expected)

    def test_empty_storage(self):
        with patch("app.service.load_tasks", return_value=[]):
            self.assertEqual(list_tasks(status="open", q="launch"), [])


if __name__ == "__main__":
    unittest.main()
