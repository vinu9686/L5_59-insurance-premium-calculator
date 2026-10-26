# Lab 5 – Issues Found and Fixed

**Name:** Vinodkumar L  **SRN:** PES1UG25AM817
**File:** `premium_calculator.py` (insurance premium calculator)
**Line numbers refer to the original file.**

| Baseline | Bandit | Pylint | Flake8 |
|---|---|---|---|
| Before | 10 issues (1 High, 5 Medium, 4 Low) | 5.73/10 | 19 warnings |
| After | 0 issues | 10.00/10 | 0 warnings |

## Security (Bandit) – High and Medium first

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Unsafe `tar.extractall` (B202, **High**) | Security | 63–65 | A customer-uploaded archive can contain `../../x` or absolute paths and overwrite files outside `claims_docs` (path traversal). | `tar.extractall("claims_docs", filter="data")` (PEP 706), inside `with tarfile.open(...)`. Tested: a `../escape.txt` member is rejected. |
| TLS verification disabled (B323, Medium) | Security | 58 | `ssl._create_unverified_context()` accepts any certificate, so a man-in-the-middle can serve fake rate tables. Also a private API (Pylint W0212). | `ssl.create_default_context()`. |
| `urlopen` accepts any scheme (B310, Medium) | Security | 59 | `file:///etc/passwd` or custom schemes could be passed in; no timeout, so it can hang forever. | Allow only `https`, add `timeout=10`, use `with`. `# nosec B310` kept with a comment explaining the scheme check. |
| Untrusted XML parsed with stdlib (B314/B405, Medium) | Security | 7, 48 | `xml.etree` is vulnerable to entity-expansion ("billion laughs") on partner XML. | `defusedxml.ElementTree`; added `requirements.txt`. Tested: an entity payload raises `EntitiesForbidden`. |
| Bind to all interfaces (B104, Medium) | Security | 12 | `HOST = "0.0.0.0"` exposes the service on every network interface. | Default `127.0.0.1`, overridable with `PREMIUM_HOST`. |
| Log file in `/tmp` (B108, Medium) | Security | 14 | World-writable directory; another user can pre-create or symlink the log. | Default to `premium_quotes.log` in the working dir; override with `PREMIUM_LOG_FILE`. |
| Hardcoded secret (B105, Low) | Security | 13 | Underwriter token is in source control (and was repeated in `main()`). | Read from `UNDERWRITER_TOKEN` env var; empty means nobody is authorised; removed from `main()`. |
| Non-constant-time token check | Security | 74 | `==` can leak the token through timing. | `hmac.compare_digest`. |
| `random` for policy numbers (B311, Low) | Security | 37 | Predictable numbers can be guessed. | `secrets.randbelow`. Also: `save_quote` now retries on collision (previously a clash silently overwrote another quote). |
| Bare `except` + `continue` (B112, Low; E722; W0702) | Bug / Security | 53–54 | Swallows every error (even `KeyboardInterrupt`) with no trace. | Catch `(TypeError, ValueError)` and `logging.warning` the bad element. Also reject unknown types and negative values. |

## Bugs the tools do not flag (found by reading the output)

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Mutable default arg + mutation | Bug | 17, 27 | `discounts=[]` is shared across calls and `append(500)` runs every call, so identical customers get different quotes (6000 vs 5500, and later quotes keep shrinking). | Default `None`; never mutate the caller's list; the stray `append(500)` is removed. Quotes 1 and 2 now match (6000.0). |
| `smoker="no"` treated as smoker | Bug | 92 | A non-empty string is truthy, so the 1.3× loading applied to a non-smoker. | `Applicant` dataclass validates `smoker` is a real `bool` (raises `TypeError`). Also cuts the argument count 6 → 4. |
| Negative premium | Bug | 25–26 | Stacked discounts gave **-800.0**. | Negative inputs rejected; result floored at 0 and rounded to 2 decimals. *Assumption:* a floor of zero (the business may prefer a minimum premium). |
| Wrong age | Bug | 33 | `year - year` ignores the birthday (printed 36 for a DOB of 31-12-1990 on 26-10-2026; correct is 35). | Compare `(month, day)`; reject future dates; `today` parameter for testing. |
| 29 Feb renewal crash | Bug | 81 | `date.replace(year=...)` raises `ValueError` for 2024-02-29 + 1 year. | Fall back to 28 Feb. |
| Instalment loses money, `months=0` | Bug | 67–71 | `floor` drops paise (12 × 664 < 7970); `months == 0` quietly returned the full premium. | `round(premium / months, 2)`; `months <= 0` raises `ValueError`. |
| Unknown policy type | Bug | 18 | `BASE_RATES[...]` raised a bare `KeyError`. | Explicit `ValueError` message. |
| Log line breaks on commas | Bug | 43 | Name `Smith, John` corrupts the CSV log. | `csv.writer` handles quoting. |
| `main()` ran on import | Design | 107 | Importing the module executed the demo. | `if __name__ == "__main__":` guard. |

## Code quality (Pylint)

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Missing docstrings (C0114, C0116) | Style | 1, 17, 30 … 89 | 13 missing. | Module and function docstrings. |
| Non-snake_case names (C0103) | Style | 11 functions | e.g. `calculatePremium`. | Renamed (`calculate_premium`, `age_from_dob`, …). |
| Too many arguments (R0913, R0917) | Design | 17 | 6 parameters. | `Applicant` dataclass. |
| `open()` without `with` / encoding (R1732, W1514) | Resource | 42–44 | File leaks if `write` raises. | `with open(..., encoding="utf-8")`. |
| Smaller items (C0209, R1705, R1703, C0200, C0301) | Style | 43, 68, 74, 86, 101 | f-string, redundant `else`, `range(len())`, 148-char line. | f-string, early return, `enumerate`, wrapped line. |

## Style (Flake8)

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| E302 / E305 (12 warnings) | Style | 17–107 | Needed 2 blank lines around top-level definitions. | Added. |
| E501 line too long (5 warnings) | Style | 14, 17, 52, 87, 101 | Over 79 characters. | Wrapped. |
| E722 bare except | Style | 53 | See above. | See above. |

## Verification

Reports are in `before/` and `after/`. Final run: Bandit 0 issues, Pylint 10.00/10, Flake8 0 warnings. Behaviour was checked with small regression tests (mutable default, smoker string, age on and around the birthday, leap-day renewal, `months=0`, tar traversal, XML entities, `file://` URL, CSV names with commas).
