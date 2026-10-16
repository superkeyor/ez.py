#!/usr/bin/env bash

usage() {
    cat <<'HELP'
Prepare, build, and publish ez to PyPI using uv.

Usage:
    bash publish.sh
    -h, --help    Show this help and exit.

Notes:
    1. Updates catalogs/CLI metadata, bumps the version with legacy rollover, and
       publishes a fresh sdist and universal wheel.
    2. Uses UV_PUBLISH_TOKEN, otherwise ~/.pypirc [pypi] token credentials.
    3. After upload, stages all changes, commits, pushes origin/master, and runs
       ezupdate three times. Requires uv, Git, and ezupdate from ~/.bash_profile.
    4. Failures stop the release. An uploaded version cannot be rolled back.

Example:
    bash /path/to/ez/publish.sh

See also:
    python ez/prepublish.py --help
HELP
}

case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
    "")
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac
if (( $# > 0 )); then
    usage >&2
    exit 2
fi

csd="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || exit 1
if [[ "$csd" == *.app/Contents/Resources ]]; then
    csd="$(cd "$csd/../../.." && pwd)" || exit 1
fi
cd "$csd" || exit 1

if [[ -f "$HOME/.bash_profile" ]]; then
    if ! source "$HOME/.bash_profile"; then
        printf 'Could not load ~/.bash_profile; release stopped.\n' >&2
        exit 1
    fi
fi
shopt -s expand_aliases
export PATH="$PATH:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin"

set -e -o pipefail
stage="checking prerequisites"
trap 'status=$?; printf "Release failed while %s (exit %s). Any completed PyPI upload remains published.\n" "$stage" "$status" >&2; exit "$status"' ERR
for required in uv git ezupdate; do
    if ! command -v "$required" >/dev/null 2>&1; then
        printf 'Required command not found: %s\n' "$required" >&2
        exit 1
    fi
done

stage="preparing, building, or uploading the release"
uv run --no-project --python '>=3.11' "$csd/scripts/publish.py"

stage="staging release changes (PyPI upload already completed)"
git add -A
stage="committing release changes (PyPI upload already completed)"
git commit -m 'update'
stage="pushing origin/master (PyPI upload already completed)"
git push origin master

stage="upgrading the local installation (PyPI upload already completed)"
for _ in 1 2 3; do
    ezupdate
done

stage="reporting distribution and installed versions (PyPI upload already completed)"

ver="$(uv version --short 2>/dev/null)"
distfiles="$(ls "$csd/dist" 2>/dev/null | tr '\n' ',' | sed 's/,$//' | sed 's/,/, /g')"
printf 'Distribution: %s (%s)\n' "$ver" "$distfiles"

printf '\n'
eval "$(uv pip show ez 2>/dev/null | awk -F': ' '
  /^Name:/ { name = $2 }
  /^Version:/ { version = $2 }
  /^Location:/ { location = $2 }
  END {
    print "location=\"" location "\""
    print "package=\"" name " " version "\""
  }
')"
printf 'Local: %s (%s)\n' "$package" "$location"

printf 'Done.\n'
