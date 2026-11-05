import copy
import importlib.util
import json
from html.parser import HTMLParser
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "skills/recoup-internal-consulting-weekly-project-review"
spec = importlib.util.spec_from_file_location("weekly_review", SKILL / "scripts/render_review.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class WeeklyProjectReviewTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SKILL / "fixtures/example.json").read_text())

    def test_only_audience_fields_are_published(self):
        self.data["projects"][0]["evidence"] = ["PRIVATE_SOURCE_778"]
        self.data["projects"][0]["internal_notes"] = ["PRIVATE_NOTE_991"]
        result = review.render_html(self.data)
        self.assertNotIn("PRIVATE_SOURCE_778", result)
        self.assertNotIn("PRIVATE_NOTE_991", result)
        self.assertIn("The new search returns account names and cities.", result)

    def test_content_cannot_escape_into_active_html(self):
        self.data["title"] = '</title><script>alert("title")</script>'
        self.data["projects"][0]["progress"] = ['<img src=x onerror="alert(1)">']
        result = review.render_html(self.data)
        self.assertNotIn('<img src=x', result)
        self.assertNotIn('</title><script>alert', result)
        self.assertIn('&lt;img src=x', result)

    def test_ambiguous_or_unsafe_navigation_is_rejected(self):
        second = copy.deepcopy(self.data["projects"][0])
        self.data["projects"].append(second)
        with self.assertRaises(ValueError):
            review.validate(self.data)
        self.data["projects"].pop()
        self.data["projects"][0]["id"] = 'x" onclick="alert(1)'
        with self.assertRaises(ValueError):
            review.validate(self.data)

    def test_blocker_and_slowdown_are_distinct(self):
        review.validate(self.data)
        result = review.render_html(self.data)
        self.assertIn('class="tag slowdown"', result)
        self.assertIn('class="tag blocker"', result)
        self.data["projects"][0]["issues"][0]["kind"] = "almost-done"
        with self.assertRaises(ValueError):
            review.validate(self.data)

    def test_secondary_updates_keep_separate_bullets_and_private_notes_out(self):
        secondary = self.data["other_projects"][0]
        secondary["progress"] = ["First verified change", "Second verified change"]
        secondary["next_week"] = ["Review the sample", "Confirm the result"]
        secondary["internal_notes"] = ["PRIVATE_SECONDARY_NOTE"]
        result = review.render_html(self.data)
        self.assertIn("<li>First verified change</li>", result)
        self.assertIn("<li>Second verified change</li>", result)
        self.assertIn("<li>Review the sample</li>", result)
        self.assertIn("<li>Confirm the result</li>", result)
        self.assertNotIn("PRIVATE_SECONDARY_NOTE", result)

    def test_progress_is_not_capped_and_continuing_work_is_separate(self):
        project = self.data["projects"][0]
        project["progress"] = [f"Verified change {i}" for i in range(6)]
        project["continuing"] = ["Design work can continue"]
        result = review.render_html(self.data)
        for item in project["progress"]:
            self.assertIn(f"<li>{item}</li>", result)
        self.assertIn("<h4>Can continue now</h4>", result)
        self.assertIn("<li>Design work can continue</li>", result)

    def test_projects_and_sections_start_closed_without_duplicate_views(self):
        class Disclosures(HTMLParser):
            def __init__(self):
                super().__init__()
                self.details = []

            def handle_starttag(self, tag, attrs):
                if tag == "details":
                    self.details.append(dict(attrs))

        parser = Disclosures()
        parser.feed(review.render_html(self.data))
        projects = [x for x in parser.details if x.get("class") == "project"]
        sections = [x for x in parser.details if x.get("class") == "review-section"]
        expected = len(self.data["projects"]) + len(self.data["other_projects"])
        self.assertEqual(len(projects), expected)
        self.assertEqual(len({x["data-project"] for x in projects}), expected)
        self.assertEqual([x["data-section"] for x in sections],
                         ["progress", "blockers", "focus"] * expected)
        self.assertTrue(all("open" not in x for x in parser.details))


if __name__ == "__main__":
    unittest.main()
