# Pytest annotate pr

Based on [this stackoverflow question](https://stackoverflow.com/questions/67482906/show-coverage-in-github-pr), this is
 a GitHub Action for annotating the commits based on your Pytest coverage report.

## How it works

1. Generates `pytest` report leveraging `coverage` library. More specifically, these set of commands are 
run :
   ```shell
   changed_files=$(git diff --name-only --diff-filter=AM "$PR_BASE_SHA" "$PR_HEAD_SHA" | grep '\.py$' | tr '\n' ' ')
   python -m coverage run -m pytest $changed_files
   python -m coverage json
   ```
   This generates a `coverage.json` report file.
2. Next, a Python script parses the file and generates `warning` annotations using the GitHub Check runs API. We only 
generate `50` annotations in a single run since that's the limit specified by the API specifications.