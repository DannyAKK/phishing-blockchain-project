"""Tests for preparation without premature assessment results."""

import contextlib
import io
import unittest
from unittest.mock import patch

import main
from assessment import prepare_assessment


class AssessmentTests(unittest.TestCase):
    def test_preparation_preserves_input_and_normalises_hostname(self):
        assessment = prepare_assessment("  https://Example.com/Login?Ref=Test  ")
        self.assertEqual(assessment.submitted_input, "https://Example.com/Login?Ref=Test")
        self.assertEqual(assessment.input_type, "HTTPS URL")
        self.assertEqual(assessment.hostname, "example.com")

    def test_bare_domain_remains_bare(self):
        assessment = prepare_assessment("Example.com")
        self.assertEqual(assessment.submitted_input, "Example.com")
        self.assertEqual(assessment.input_type, "Domain")
        self.assertEqual(assessment.hostname, "example.com")

    def test_unperformed_results_are_unset(self):
        assessment = prepare_assessment("example.com")
        self.assertIsNone(assessment.reason_codes)
        self.assertIsNone(assessment.score)
        self.assertIsNone(assessment.verdict)
        self.assertIsNone(assessment.registry_status)

    def test_invalid_input_does_not_produce_assessment(self):
        for supplied in ("", "example..com", "ftp://example.com", "\texample.com"):
            with self.subTest(supplied=supplied):
                with self.assertRaises(ValueError):
                    prepare_assessment(supplied)

    def test_cli_does_not_display_unperformed_results(self):
        output = io.StringIO()
        with patch("builtins.input", return_value="example.com"):
            with contextlib.redirect_stdout(output):
                main.main()
        displayed = output.getvalue()
        self.assertIn("Hostname: example.com", displayed)
        self.assertIn("Phishing assessment is not implemented yet.", displayed)
        for label in ("Score:", "Verdict:", "Registry status:", "None"):
            self.assertNotIn(label, displayed)


if __name__ == "__main__":
    unittest.main()
