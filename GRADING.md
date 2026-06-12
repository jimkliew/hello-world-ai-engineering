# GRADING.md — Assignment 1 Auto-Grader

A helper script (`grade_assignment.py`) that loops over a list of GitHub
usernames and grades whether each student completed **Assignment 1 – GitHub
Hello World** properly.

## What it checks

For each username, the script locates the student's assignment repository and
scores it against a 100-point rubric:

| Criterion        | Points | How it's checked                                    |
|------------------|:------:|-----------------------------------------------------|
| Repository exists |  20   | A repo named `hello-world-ai-engineering` (or similar), or any repo containing `hello.py`/`hello.js` |
| Python script     |  20   | A `.py` file is present                             |
| JavaScript script |  20   | A `.js` file is present                             |
| README.md         |  20   | A `README.md` file is present                       |
| Personal flare    |  20   | The greeting contains more than a bare "Hello World" |

A total of **80 or higher** is marked `PASS`; below that is `NEEDS WORK`.

## Requirements

- Python 3 (standard library only — no `pip install` needed)
- Internet access to reach the GitHub API
- *(Optional)* A GitHub token to raise the API rate limit from 60 to 5,000
  requests per hour:

  ```bash
  export GITHUB_TOKEN=ghp_your_token_here
  ```

## Usage

**Option A — pass a file of usernames** (one per line, `#` for comments):

```bash
python grade_assignment.py students.txt
```

Example `students.txt`:

```
# AI Engineering – Section 1
jimkliew
classmate-one
classmate-two
```

**Option B — pass usernames directly:**

```bash
python grade_assignment.py jimkliew classmate-one classmate-two
```

## Output

The script prints a per-student report to the screen and writes a
`grades.csv` file with one row per student, including the score breakdown,
pass/fail status, and notes on anything missing.

## Notes and limitations

- The "personal flare" check is a heuristic: it strips the boilerplate
  greeting and passes if meaningful text remains. Spot-check borderline
  cases manually.
- If a student named their repo something unusual and it contains no
  `hello.py`/`hello.js` at the root, the script may not find it — verify
  any `(none)` results by hand.
- The Canvas reply requirement (commenting on a classmate's post) cannot be
  verified through the GitHub API and must be checked in Canvas.
