"""Smoke tests for UI Research CLI."""

import sys
import json
import unittest
import subprocess
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "ui_research.py"


def _run(args, timeout=30):
    """Run the CLI script with given args."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


class TestHelp(unittest.TestCase):
    """Tests for --help flag."""
    
    def test_help_exits_zero(self):
        rc, stdout, stderr = _run(["--help"])
        self.assertEqual(rc, 0, f"--help failed: {stderr}")
    
    def test_help_shows_usage(self):
        rc, stdout, stderr = _run(["--help"])
        self.assertIn("usage:", stdout)
        self.assertIn("concept", stdout)
    
    def test_help_shows_examples(self):
        rc, stdout, stderr = _run(["--help"])
        self.assertIn("Examples:", stdout)
        self.assertIn("--diagnose", stdout)


class TestDiagnose(unittest.TestCase):
    """Tests for --diagnose flag."""
    
    def test_diagnose_exits_zero(self):
        rc, stdout, stderr = _run(["--diagnose"])
        self.assertEqual(rc, 0, f"--diagnose failed: {stderr}")
    
    def test_diagnose_returns_valid_json(self):
        rc, stdout, stderr = _run(["--diagnose"])
        data = json.loads(stdout)
        self.assertIsInstance(data, dict)
    
    def test_diagnose_has_tier(self):
        rc, stdout, stderr = _run(["--diagnose"])
        data = json.loads(stdout)
        self.assertIn("detectedTier", data)
        self.assertIn(data["detectedTier"], [0, 1, 2, 3])
    
    def test_diagnose_has_playwright_status(self):
        rc, stdout, stderr = _run(["--diagnose"])
        data = json.loads(stdout)
        self.assertIn("playwrightAvailable", data)
        self.assertIsInstance(data["playwrightAvailable"], bool)
    
    def test_diagnose_has_research_dir(self):
        rc, stdout, stderr = _run(["--diagnose"])
        data = json.loads(stdout)
        self.assertIn("researchDir", data)


class TestHistory(unittest.TestCase):
    """Tests for --history flag."""
    
    def test_history_exits_zero(self):
        rc, stdout, stderr = _run(["--history"])
        self.assertEqual(rc, 0, f"--history failed: {stderr}")
    
    def test_history_shows_message(self):
        rc, stdout, stderr = _run(["--history"])
        # Either shows history or "no history" message
        self.assertTrue(
            "History" in stdout or "history" in stdout,
            f"Expected history message, got: {stdout}"
        )


class TestMock(unittest.TestCase):
    """Tests for --mock flag."""
    
    def test_mock_requires_concept(self):
        rc, stdout, stderr = _run(["--mock"])
        self.assertNotEqual(rc, 0)
        self.assertIn("concept is required", stderr)
    
    def test_mock_runs_with_concept(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.html"
            rc, stdout, stderr = _run([
                "--mock", "test concept",
                "--output", str(output_path),
                "--no-open"
            ])
            self.assertEqual(rc, 0, f"Mock failed: {stderr}\n{stdout}")
    
    def test_mock_creates_gallery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.html"
            rc, stdout, stderr = _run([
                "--mock", "kanban board",
                "--output", str(output_path),
                "--no-open"
            ])
            self.assertTrue(output_path.exists(), f"Gallery not created: {stderr}")
            
            # Verify HTML content
            content = output_path.read_text()
            self.assertIn("kanban board", content.lower())
            self.assertIn("<!DOCTYPE html>", content)
    
    def test_mock_outputs_research_id(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.html"
            rc, stdout, stderr = _run([
                "--mock", "test",
                "--output", str(output_path),
                "--no-open"
            ])
            self.assertIn("Research ID:", stdout)


class TestNoArgs(unittest.TestCase):
    """Tests for running without arguments."""
    
    def test_no_args_shows_help(self):
        rc, stdout, stderr = _run([])
        self.assertNotEqual(rc, 0)
        self.assertIn("usage:", stdout)
    
    def test_no_args_shows_error(self):
        rc, stdout, stderr = _run([])
        self.assertIn("concept is required", stderr)


class TestInvalidArgs(unittest.TestCase):
    """Tests for invalid arguments."""
    
    def test_invalid_tier(self):
        rc, stdout, stderr = _run(["--tier", "5", "test"])
        self.assertNotEqual(rc, 0)
    
    def test_invalid_open_id(self):
        rc, stdout, stderr = _run(["--open", "nonexistent-id-xyz"])
        self.assertNotEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
