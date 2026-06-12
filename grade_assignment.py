#!/usr/bin/env python3
"""
grade_assignment.py

Grades Assignment 1 (GitHub Hello World) for a list of GitHub usernames.

For each student it checks their assignment repository for:
  1. A Python "Hello World" script   (hello.py or *.py)
  2. A JavaScript "Hello World" script (hello.js or *.js)
  3. A README.md file
  4. "Personal flare" -> the greeting contains more than a bare
     "Hello World" (a name, hometown, interest, fun fact, etc.)

Usage:
  python grade_assignment.py students.txt
  python grade_assignment.py alice bob carol

  # Optional: set a token to raise the API rate limit (60/hr -> 5000/hr)
  export GITHUB_TOKEN=ghp_xxx

Output: a printed report and a grades.csv file.
"""

import os
import sys
import csv
import base64
import urllib.request
import urllib.error

API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Repo names students were told they might use. The grader tries each
# student's repos and picks the first that looks like the assignment.
LIKELY_NAMES = ["hello-world-ai-engineering", "course-introduction", "hello-world"]

# Total points and how they break down
RUBRIC = {
    "repo_exists":   20,
    "python_script": 20,
    "js_script":     20,
    "readme":        20,
    "personal_flare": 20,
}


def api_get(url):
    """GET a GitHub API URL, returning parsed JSON or None on 404."""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            import json
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code == 403:
            print("  ! Rate limited (403). Set GITHUB_TOKEN to raise the limit.")
        return None
    except Exception as e:
        print(f"  ! Request failed: {e}")
        return None


def get_repo_files(user, repo):
    """Return a dict {filename_lower: download/content info} for the repo root."""
    data = api_get(f"{API}/repos/{user}/{repo}/contents/")
    if not isinstance(data, list):
        return {}
    return {item["name"].lower(): item for item in data if item.get("type") == "file"}


def file_text(user, repo, path):
    """Fetch and decode a file's text content."""
    data = api_get(f"{API}/repos/{user}/{repo}/contents/{path}")
    if isinstance(data, dict) and data.get("content"):
        try:
            return base64.b64decode(data["content"]).decode("utf-8", "ignore")
        except Exception:
            return ""
    return ""


def find_assignment_repo(user):
    """Pick the student's assignment repo by name, else scan their repos."""
    for name in LIKELY_NAMES:
        if api_get(f"{API}/repos/{user}/{name}"):
            return name
    repos = api_get(f"{API}/users/{user}/repos?per_page=100")
    if isinstance(repos, list):
        for r in repos:
            files = get_repo_files(user, r["name"])
            if "hello.py" in files or "hello.js" in files:
                return r["name"]
    return None


def has_flare(text):
    """A bare 'Hello World' fails; any added personal content passes."""
    if not text:
        return False
    lowered = text.lower()
    # Strip the boilerplate greeting and see if meaningful content remains.
    stripped = lowered.replace("hello, world", "").replace("hello world", "")
    # Keep only letters/digits to measure remaining substance.
    remaining = "".join(c for c in stripped if c.isalnum())
    return len(remaining) > 15


def grade_student(user):
    """Return (scores_dict, total, notes_list) for one student."""
    scores = {k: 0 for k in RUBRIC}
    notes = []

    repo = find_assignment_repo(user)
    if not repo:
        notes.append("No assignment repo found.")
        return scores, 0, notes, None

    scores["repo_exists"] = RUBRIC["repo_exists"]
    files = get_repo_files(user, repo)

    py = next((f for f in files if f.endswith(".py")), None)
    js = next((f for f in files if f.endswith(".js")), None)
    readme = next((f for f in files if f == "readme.md"), None)

    py_text = file_text(user, repo, files[py]["path"]) if py else ""
    js_text = file_text(user, repo, files[js]["path"]) if js else ""

    if py:
        scores["python_script"] = RUBRIC["python_script"]
    else:
        notes.append("Missing Python script.")

    if js:
        scores["js_script"] = RUBRIC["js_script"]
    else:
        notes.append("Missing JavaScript script.")

    if readme:
        scores["readme"] = RUBRIC["readme"]
    else:
        notes.append("Missing README.md.")

    if has_flare(py_text) or has_flare(js_text):
        scores["personal_flare"] = RUBRIC["personal_flare"]
    else:
        notes.append("No personal flare detected (bare Hello World).")

    total = sum(scores.values())
    if not notes:
        notes.append("All criteria met.")
    return scores, total, notes, repo


def load_usernames(args):
    """Usernames from a file (one per line) or directly from CLI args."""
    if len(args) == 1 and os.path.isfile(args[0]):
        with open(args[0]) as f:
            return [line.strip() for line in f if line.strip()
                    and not line.startswith("#")]
    return args


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    usernames = load_usernames(sys.argv[1:])
    rows = []

    print(f"\nGrading {len(usernames)} student(s)\n" + "=" * 50)
    for user in usernames:
        print(f"\n@{user}")
        scores, total, notes, repo = grade_student(user)
        status = "PASS" if total >= 80 else "NEEDS WORK"
        print(f"  Repo:  {repo or '(none)'}")
        print(f"  Score: {total}/100  -> {status}")
        for n in notes:
            print(f"   - {n}")
        rows.append({
            "username": user,
            "repo": repo or "",
            **scores,
            "total": total,
            "status": status,
            "notes": "; ".join(notes),
        })

    out = "grades.csv"
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved results to {out}")


if __name__ == "__main__":
    main()
