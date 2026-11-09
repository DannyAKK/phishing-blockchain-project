"""Tests for the restricted input policy and CLI boundary."""

import contextlib
import importlib
import io
import unittest
from unittest.mock import patch

import main
from input_validation import parse_input


class InputValidationTests(unittest.TestCase):
    def test_accepted_inputs(self):
        cases = [
            ("example.com", "Domain", "example.com"),
            ("sub.example.com", "Domain", "sub.example.com"),
            ("http://example.com/login", "HTTP URL", "example.com"),
            ("https://Example.com/Login?Ref=Test#Section", "HTTPS URL", "example.com"),
            ("  EXAMPLE.COM  ", "Domain", "example.com"),
            ("https://EXAMPLE.COM", "HTTPS URL", "example.com"),
            ("my-domain.example", "Domain", "my-domain.example"),
            ("not-in-any-list.example", "Domain", "not-in-any-list.example"),
            ("HTTPS://Example.com/Path", "HTTPS URL", "example.com"),
            ("a" * 63 + ".example", "Domain", "a" * 63 + ".example"),
        ]
        for supplied, input_type, hostname in cases:
            with self.subTest(supplied=supplied):
                self.assertEqual(parse_input(supplied), {
                    "submitted_input": supplied.strip(" "),
                    "input_type": input_type,
                    "hostname": hostname,
                })

    def test_hostname_length_boundary(self):
        hostname = ".".join(["a" * 63] * 3 + ["b" * 61])
        self.assertEqual(len(hostname), 253)
        self.assertEqual(parse_input(hostname)["hostname"], hostname)
        with self.assertRaisesRegex(ValueError, "253"):
            parse_input(hostname + "b")

    def test_rejected_inputs(self):
        cases = [
            "", "   ", "exam ple.com", "https://example.com/a b",
            "http://", "https:///login", "http:example.com", "http:/example.com",
            "ftp://example.com", "mailto:user@example.com", "//example.com",
            "example.com/path", "example.com?x=1", "example.com#part",
            "example..com", ".example.com", "example_com.org",
            "-example.com", "example-.com", "a" * 64 + ".com",
            "example.com.", "example.123", "127.0.0.1", "http://127.0.0.1",
            "http://user:password@example.com", "http://@example.com",
            "http://example.com:80", "http://example.com:", "http://example.com:abc",
            "example.com:80", "http://[::1]", "[::1]", "localhost",
            "http://localhost", "exämple.com", "https://example.com/é",
            "xn--example.com", "XN--example.com", "sub.xn--example.com",
            "http://XN--example.com", "example\\.com", "http://example.com\\path",
            "http://[example.com", "http://example.com]", "http://:80",
            "http://example%2ecom", "http://example.com;other.com",
        ]
        for supplied in cases:
            with self.subTest(supplied=supplied):
                with self.assertRaises(ValueError):
                    parse_input(supplied)

    def test_raw_control_characters_are_rejected(self):
        for codepoint in [*range(32), 127]:
            character = chr(codepoint)
            for supplied in (character + "example.com", "https://exam" + character + "ple.com", "example.com" + character):
                with self.subTest(codepoint=codepoint, supplied=supplied):
                    with self.assertRaisesRegex(ValueError, "control characters"):
                        parse_input(supplied)


class CliTests(unittest.TestCase):
    def run_cli(self, supplied=None, error=None):
        output = io.StringIO()
        with patch("builtins.input", return_value=supplied, side_effect=error):
            with contextlib.redirect_stdout(output):
                main.main()
        return output.getvalue()

    def test_import_does_not_prompt(self):
        with patch("builtins.input") as prompt:
            importlib.reload(main)
        prompt.assert_not_called()

    def test_success_output(self):
        output = self.run_cli("https://Example.com/Login?Ref=Test")
        self.assertIn("Input type: HTTPS URL", output)
        self.assertIn("Hostname: example.com", output)
        self.assertIn("This confirms supported syntax only.", output)
        self.assertIn("Phishing assessment is not implemented yet.", output)

    def test_expected_failures_have_no_traceback_or_assessment(self):
        for supplied in ("", "example..com", "ftp://example.com", "http://[bad"):
            with self.subTest(supplied=supplied):
                output = self.run_cli(supplied)
                self.assertNotIn("Traceback", output)
                self.assertNotIn("Input accepted", output)
                self.assertNotIn("Hostname:", output)
                self.assertTrue(output.strip())

    def test_eof_and_keyboard_interrupt(self):
        for error in (EOFError, KeyboardInterrupt):
            with self.subTest(error=error):
                self.assertIn("Input cancelled. Exiting.", self.run_cli(error=error))


if __name__ == "__main__":
    unittest.main()
