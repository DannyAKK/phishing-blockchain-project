"""Restricted ASCII domain and HTTP(S) input validation; no network access."""

import re
from urllib.parse import urlsplit


def parse_input(raw_input: str) -> dict[str, str]:
    """Return submitted input, input type and hostname, or raise ValueError.

    Accept bare multi-label ASCII domains or HTTP(S) URLs without ports
    or credentials. This checks supported syntax, not existence or safety.
    """
    if any(ord(character) < 32 or ord(character) == 127 for character in raw_input):
        raise ValueError("Invalid input: control characters are not allowed.")
    if not raw_input.isascii():
        raise ValueError("Unsupported input: only ASCII input is supported.")

    submitted_input = raw_input.strip(" ")
    if not submitted_input:
        raise ValueError("No input provided. Please enter a URL or domain.")
    if any(character.isspace() for character in submitted_input):
        raise ValueError("Invalid input: internal whitespace is not allowed.")
    if "\\" in submitted_input:
        raise ValueError("Invalid input: backslashes are not allowed.")
    if submitted_input.startswith("//"):
        raise ValueError("Unsupported input: scheme-relative URLs are not supported.")

    scheme_match = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*):", submitted_input)
    if scheme_match:
        scheme = scheme_match.group(1).lower()
        if scheme not in ("http", "https"):
            raise ValueError("Unsupported input: use an HTTP or HTTPS URL.")
        if not submitted_input[len(scheme) + 1:].startswith("//"):
            raise ValueError("Invalid URL: the scheme must be followed by ://.")
        try:
            parsed = urlsplit(submitted_input)
            authority = parsed.netloc
            hostname = parsed.hostname
        except ValueError as error:
            raise ValueError("Invalid URL: malformed URL authority.") from error
        if not authority or not hostname:
            raise ValueError("Invalid URL: a hostname is required.")
        if "@" in authority:
            raise ValueError("Unsupported input: URL credentials are not supported.")
        if "[" in authority or "]" in authority:
            raise ValueError("Unsupported input: IP address hosts are not supported.")
        if ":" in authority:
            raise ValueError("Unsupported input: explicit ports are not supported.")
        # Only a plain hostname is allowed in the authority at this stage.
        if authority.lower() != hostname:
            raise ValueError("Invalid URL: malformed URL authority.")
        input_type = f"{scheme.upper()} URL"
    else:
        if any(character in submitted_input for character in "/?#"):
            raise ValueError("Unsupported input: bare domains cannot include paths, queries or fragments.")
        if ":" in submitted_input or "[" in submitted_input or "]" in submitted_input:
            raise ValueError("Unsupported input: ports and IP address hosts are not supported.")
        hostname = submitted_input.lower()
        input_type = "Domain"

    validate_hostname(hostname)
    return {
        "submitted_input": submitted_input,
        "input_type": input_type,
        "hostname": hostname,
    }


def validate_hostname(hostname: str) -> None:
    """Enforce the initial domain policy without registration or suffix lookups."""
    if len(hostname) > 253:
        raise ValueError("Invalid hostname: maximum length is 253 characters.")
    labels = hostname.split(".")
    if len(labels) < 2:
        raise ValueError("Unsupported hostname: at least two labels are required.")
    for label in labels:
        if not label or len(label) > 63:
            raise ValueError("Invalid hostname: labels must contain 1 to 63 characters; no trailing dot.")
        if label.lower().startswith("xn--"):
            raise ValueError("Unsupported hostname: xn-- labels are not supported yet.")
        if not re.fullmatch(r"[a-z0-9]+(?:[a-z0-9-]*[a-z0-9])?", label):
            raise ValueError("Invalid hostname: use letters, digits and internal hyphens only.")
    if labels[-1].isdigit():
        raise ValueError("Unsupported hostname: numeric-only final labels and IPv4 hosts are not supported.")
