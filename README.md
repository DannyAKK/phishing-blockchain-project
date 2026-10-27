# Detection of Phishing Attack Using Blockchain Technology

Final-year cybersecurity project.

## Current implementation

`main.py` prints "Phishing Assessment Prototype".

Input handling, URL validation, detection checks, scoring, registry
lookup, evidence generation and blockchain integration are not
implemented.

## Run

Python is required. No external packages are currently required.

From the project directory:

    python main.py

Expected output:

    Phishing Assessment Prototype

## Development approach

Development proceeds in small, separately approved increments.
The next planned increment is command-line input and empty-input
handling.

## Project boundaries

- Supplied destinations must not be visited or fetched.
- Registry membership does not prove safety.
- Registry absence does not prove phishing.
- Evidence verification would establish integrity, not whether
  the original assessment was correct.
- A local file of hashes is not blockchain integration.
