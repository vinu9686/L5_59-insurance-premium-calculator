# Lab 5 – Reflection

**Name:** Vinodkumar L  **SRN:** PES1UG25AM817

**1. Which issues were easiest to fix, and which were hardest?**
Easiest were the mechanical ones: Flake8 blank lines and line length, Pylint docstrings and `snake_case` renames, and swapping `random` for `secrets`. Hardest were the ones needing a design decision. The tar extraction fix needed me to understand path traversal and the PEP 706 `filter="data"` option (my first attempt, a hand-written member check, still triggered Bandit B202). Deciding what a negative premium should do was also a judgement call, because it is a business rule, not a coding rule.

**2. Did the tools report any false positives or unhelpful warnings?**
Mostly no, but some need context. B310 (`urlopen` scheme) still fires after I restrict the URL to `https`, because Bandit cannot see my check, so I suppressed it with `# nosec B310` and a comment saying why. B105 (hardcoded password) was a real finding here, but would be noise for a constant like `TOKEN_HEADER = "X-Token"`. Pylint's "too many arguments" is a heuristic, though in this case it pointed at a real design smell.

**3. How would you integrate static analysis into a real workflow?**
Run Flake8 and Pylint in a pre-commit hook so style problems never reach review, and run all three in CI on every pull request, failing the build on any Bandit Medium/High or a Pylint score under a threshold. Add `defusedxml` and the other tools to `requirements.txt`. Suppressions (`# nosec`, `# pylint: disable`) should need a comment and a reviewer's eye.

**4. What tangible improvements did I see after the fixes?**
The scores went from Bandit 10 issues to 0, Pylint 5.73 to 10.00, and Flake8 19 warnings to 0. More important were the behavioural gains: identical customers now get identical quotes, non-smokers are no longer charged the smoker loading, premiums can't go negative, ages are correct, and a leap-day policy no longer crashes the renewal. Untrusted archives, XML and URLs are now handled safely. A key lesson is that the tools did not catch the mutable-state quote bug, the `"no"` smoker bug or the age bug. Running the program and checking whether the numbers made sense found those, so static analysis complements testing rather than replacing it.
