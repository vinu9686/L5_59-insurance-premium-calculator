# Lab 5: Static Code Analysis — Insurance Premium Calculator

**Student Name:** Vinodkumar L  
**SRN:** PES1UG25AM817  
**Course:** Software Engineering (5th Semester)  
**Target File:** [`premium_calculator.py`](premium_calculator.py)  

---

## Overview

This repository contains the completed deliverables for **Lab 5: Static Code Analysis**. The objective of this lab is to identify, document, and remediate security vulnerabilities, software engineering code smells, PEP 8 style violations, and subtle runtime logic bugs in an insurance premium calculation system using automated static analysis tools:

- **Bandit**: Security vulnerability scanner for Python code.
- **Pylint**: Source-code, bug and quality checker enforcing coding standards.
- **Flake8**: Style guide enforcement (PEP 8, pyflakes, and McCabe complexity).

---

## Static Analysis & Quality Metrics

| Tool | Metric / Scope | Baseline (`before/`) | Final Result (`after/`) | Status |
|---|---|---|---|---|
| **Bandit** | Security Vulnerabilities | **10 issues** (1 High, 5 Medium, 4 Low) | **0 issues** | :white_check_mark: Clean |
| **Pylint** | Code Quality & Best Practices | **5.73 / 10** | **10.00 / 10** | :white_check_mark: Perfect Score |
| **Flake8** | PEP 8 Style & Formatting | **19 warnings** | **0 warnings** | :white_check_mark: Clean |
| **Logic Bugs** | Calculation & Runtime Correctness | Multiple failures (age, discounts, smoker) | All verified & passing | :white_check_mark: Verified |

---

## Workflow & Methodology

The project followed a structured, seven-stage engineering workflow:

```
[1. Baseline Run & Bug Detection] ➔ [2. Tool Setup] ➔ [3. Baseline Reports Generation]
                                                               ⬇
[6. CI Pipeline Setup] ⬅ [5. Post-Fix Verification] ⬅ [4. Code Hardening & Refactoring]
```

1. **Baseline Execution & Anomaly Detection:**
   - Ran `python premium_calculator.py` and analyzed standard outputs.
   - Identified critical business logic flaws that static analysis tools do not detect (e.g., mutable state pollution, truthy string evaluation, negative premiums, birthday miscalculations).

2. **Toolchain Installation & Environment Setup:**
   - Configured Python virtual environment and installed analysis dependencies:
     ```bash
     python -m pip install -r requirements.txt
     python -m pip install pylint bandit flake8
     ```

3. **Baseline Static Analysis (`before/`):**
   - Generated initial diagnostic reports:
     ```bash
     python -m bandit -r premium_calculator.py > before/bandit_report.txt
     python -m pylint premium_calculator.py > before/pylint_report.txt
     python -m flake8 premium_calculator.py > before/flake8_report.txt
     ```

4. **Issue Documentation & Root-Cause Analysis:**
   - Cataloged all findings in [`issues.md`](issues.md), prioritized by severity (High and Medium security issues first, followed by hidden logic bugs, Pylint quality warnings, and Flake8 formatting issues).

5. **Code Hardening & Refactoring:**
   - Remediated all vulnerabilities and bugs in [`premium_calculator.py`](premium_calculator.py).
   - Introduced strong typing, dataclasses, defensive error handling, safe cryptographic utilities, and strict input validation.

6. **Post-Fix Verification (`after/`):**
   - Re-executed all static analysis suites and verified clean reports:
     ```bash
     python -m bandit -r premium_calculator.py > after/bandit_report.txt
     python -m pylint premium_calculator.py > after/pylint_report.txt
     python -m flake8 premium_calculator.py > after/flake8_report.txt
     ```
   - Confirmed **Bandit 0 issues**, **Pylint 10.00/10**, and **Flake8 0 warnings**.

7. **Continuous Integration (CI Workflow):**
   - Implemented an automated GitHub Actions workflow in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) to automatically validate all pushes and pull requests against the test suite, Flake8, Bandit, and Pylint.

---

## Summary of Fixes

### 1. Security Hardening (Bandit)
- **Arbitrary File Overwrite / Path Traversal (B202 - High):** Unsafe `tar.extractall` replaced with PEP 706 `filter="data"` within a safe context manager (`with tarfile.open(...)`).
- **Insecure TLS Verification (B323 - Medium):** Removed `ssl._create_unverified_context()` and enforced trusted certificate validation with `ssl.create_default_context()`.
- **Arbitrary URL Scheme (B310 - Medium):** Enforced strict `https` scheme verification and a 10-second request timeout on `urlopen`.
- **XML Entity Expansion / Billion Laughs (B314 / B405 - Medium):** Replaced standard library `xml.etree` with `defusedxml.ElementTree` to prevent XXE Denial of Service attacks.
- **Insecure Interface Binding (B104 - Medium):** Replaced default binding to `0.0.0.0` with `127.0.0.1` (configurable via `PREMIUM_HOST`).
- **Insecure Shared Temporary Directory (B108 - Medium):** Replaced `/tmp` log destination with a configurable local path (`premium_quotes.log`).
- **Hardcoded Secrets (B105 - Low):** Extracted hardcoded underwriter authorization token to `UNDERWRITER_TOKEN` environment variable.
- **Timing Attack on Authentication:** Replaced standard `==` string equality with constant-time `hmac.compare_digest`.
- **Predictable PRNG (B311 - Low):** Replaced `random` with cryptographically secure `secrets.randbelow` and added collision detection.
- **Broad Exception Swallowing (B112 / E722):** Replaced bare `except:` with explicit `(TypeError, ValueError)` exception handling and warning logs.

### 2. Business Logic Bugs (Found via Output Inspection)
- **Mutable Default Argument Leak:** `discounts=[]` shared state across invocations causing quote amounts to mutate on successive calls. Fixed using `discounts=None` default.
- **Truthy String Evaluation:** String `"no"` evaluated as truthy for smoker status, inappropriately applying the 1.3× loading. Fixed by implementing `Applicant` dataclass with boolean validation.
- **Negative Premium Underflow:** Stacked discounts could result in negative premiums. Implemented lower floor of `0.0`.
- **Age Calculation Off-by-One:** Year subtraction ignored actual birth dates. Implemented day/month comparison with future date rejection.
- **Leap Year Renewal Crash:** `date.replace(year=...)` crashed on February 29 renewals. Added fallback to February 28.
- **Instalment Rounding Error:** `math.floor` dropped fractional amounts; non-positive months quietly returned the full premium. Fixed with `round(premium / months, 2)` and strict validation.
- **CSV Data Corruption:** Commas in customer names broke log formatting. Replaced string concatenation with Python's standard `csv.writer`.
- **Side-Effects on Import:** Added `if __name__ == "__main__":` guard to isolate execution from module imports.

### 3. Code Style & Architecture (Pylint & Flake8)
- Added module-level and function-level docstrings across all functions.
- Converted non-compliant camelCase function names to PEP 8 standard `snake_case`.
- Refactored functions with high parameter counts into clean dataclass structures (`Applicant`).
- Maintained exact PEP 8 line length limits (<= 79 characters) and two blank lines between top-level definitions.

---

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI pipeline (lint, scan, test)
├── .gitignore                   # Ignore __pycache__, virtual environments, log files
├── README.md                    # Project documentation and lab workflow guide
├── issues.md                    # Detailed catalog of all issues found and remediated
├── reflection.md                # Answers to lab reflection questions
├── requirements.txt             # Project runtime dependencies (defusedxml)
├── premium_calculator.py        # Refactored, hardened, and clean implementation
├── before/                      # Baseline static analysis reports
│   ├── bandit_report.txt        # Initial Bandit report (10 issues)
│   ├── flake8_report.txt        # Initial Flake8 report (19 warnings)
│   └── pylint_report.txt        # Initial Pylint report (5.73/10)
└── after/                       # Final static analysis reports
    ├── bandit_report.txt        # Clean Bandit report (0 issues)
    ├── flake8_report.txt        # Clean Flake8 report (0 warnings)
    └── pylint_report.txt        # Clean Pylint report (10.00/10)
```

---

## How to Run & Verify Locally

### 1. Setup Virtual Environment
```bash
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install pylint bandit flake8
```

### 3. Run the Application
```bash
python premium_calculator.py
```

### 4. Run Static Code Analysis
```bash
# Run Flake8 (PEP 8 style check - 0 warnings expected)
flake8 premium_calculator.py

# Run Bandit (Security check - 0 issues expected)
bandit -r premium_calculator.py

# Run Pylint (Code quality - 10.00/10 expected)
pylint premium_calculator.py
```

---

## Continuous Integration

The repository includes an automated GitHub Actions pipeline (`.github/workflows/ci.yml`) that executes on every push to `main` and on pull requests:
- Verifies program execution on Python 3.12.
- Runs `flake8` to enforce style guidelines.
- Runs `bandit` to block security vulnerabilities.
- Runs `pylint` with a minimum score threshold of `9.5/10`.
