#!/usr/bin/env bash

set -euo pipefail

workflow="build-installers.yml"
ref="${1:-$(git branch --show-current)}"

if [[ -z "${ref}" ]]; then
    echo "No branch or tag was detected. Pass one explicitly." >&2
    echo "Usage: bash packaging/build_github.sh [branch-or-tag] [download-directory]" >&2
    exit 2
fi

if ! command -v gh >/dev/null 2>&1; then
    echo "GitHub CLI is required: https://cli.github.com/" >&2
    exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
    echo "GitHub CLI is not authenticated. Run: gh auth login -h github.com" >&2
    exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
    echo "The worktree is not clean." >&2
    echo "Commit and push the intended build state before using GitHub builders." >&2
    exit 1
fi

repo="$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"
local_sha="$(git rev-parse "${ref}^{commit}")"
remote_sha="$(gh api "repos/${repo}/commits/${ref}" --jq '.sha')"

if [[ "${local_sha}" != "${remote_sha}" ]]; then
    echo "Local ${ref} does not match GitHub." >&2
    echo "Push the branch or tag before starting the build." >&2
    echo "Local:  ${local_sha}" >&2
    echo "GitHub: ${remote_sha}" >&2
    exit 1
fi

previous_run_id="$(
    gh run list \
        --workflow "${workflow}" \
        --commit "${remote_sha}" \
        --event workflow_dispatch \
        --limit 1 \
        --json databaseId \
        --jq '.[0].databaseId // empty'
)"

echo "Dispatching ${workflow} for ${repo}@${ref} (${remote_sha})..."
dispatch_output="$(gh workflow run "${workflow}" --ref "${ref}")"
printf '%s\n' "${dispatch_output}"

run_id="$(
    printf '%s\n' "${dispatch_output}" |
        sed -nE 's#^.*/actions/runs/([0-9]+).*$#\1#p' |
        tail -n 1
)"

if [[ -z "${run_id}" ]]; then
    echo "Waiting for the new workflow run to appear..."
    for _ in {1..30}; do
        candidate="$(
            gh run list \
                --workflow "${workflow}" \
                --commit "${remote_sha}" \
                --event workflow_dispatch \
                --limit 1 \
                --json databaseId \
                --jq '.[0].databaseId // empty'
        )"
        if [[ -n "${candidate}" && "${candidate}" != "${previous_run_id}" ]]; then
            run_id="${candidate}"
            break
        fi
        sleep 2
    done
fi

if [[ -z "${run_id}" ]]; then
    echo "The workflow was dispatched, but its run ID could not be resolved." >&2
    echo "Inspect it with: gh run list --workflow ${workflow}" >&2
    exit 1
fi

run_url="https://github.com/${repo}/actions/runs/${run_id}"
echo "Watching ${run_url}"
gh run watch "${run_id}" --compact --exit-status

download_dir="${2:-artifacts/github-run-${run_id}}"
mkdir -p "${download_dir}"
gh run download "${run_id}" --dir "${download_dir}"

echo "Downloaded artifacts to ${download_dir}:"
find "${download_dir}" -maxdepth 2 -type f -print | sort
