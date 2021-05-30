#!/bin/bash
# If a command fails, exit
set -e
# Treat unset variables as error
set -u
# Fail if command fails
set -o pipefail
# Print commands and their arguments
set -x


# We need GITHUB_TOKEN to operate
if [[ -z "$GITHUB_TOKEN" ]]; then
	echo "GITHUB_TOKEN should be set."
	exit 1
fi


main() {
    curl -sSL -H  "Accept: application/vnd.github.v3+json" -H "Authorization: token ${GITHUB_TOKEN}" \
    "${GITHUB_API_URL}/repos/${GITHUB_REPOSITORY}/pulls?head=${GITHUB_REPOSITORY_OWNER}:${GITHUB_REF##*/}" > pull_request.json

    PR_BASE_SHA=$(jq -r '.[0].base.sha' < pull_request.json)
    PR_HEAD_SHA=$(jq -r '.[0].head.sha' < pull_request.json)

    export PR_BASE_SHA
    export PR_HEAD_SHA

    changed_files=$(git diff --name-only --diff-filter=AM "$PR_BASE_SHA" "$PR_HEAD_SHA" | grep '\.py$' | tr '\n' ' ')

    python -m coverage run -m pytest $changed_files
    python -m coverage json
    python /src/main.py
}

main "$@"
