"""Shared assessment data and the current preparation flow."""

from dataclasses import dataclass

from input_validation import parse_input


@dataclass
class Assessment:
    """Carry parsed input; None means a later result has not been produced."""

    submitted_input: str
    input_type: str
    hostname: str
    reason_codes: list[str] | None = None
    score: int | None = None
    verdict: str | None = None
    registry_status: str | None = None


def prepare_assessment(raw_input: str) -> Assessment:
    """Validate input and prepare its data without performing an assessment."""
    parsed_input = parse_input(raw_input)
    return Assessment(
        submitted_input=parsed_input["submitted_input"],
        input_type=parsed_input["input_type"],
        hostname=parsed_input["hostname"],
    )
