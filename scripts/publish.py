"""Prepare and upload artifacts; publish.sh owns post-upload Git and upgrade steps."""

import argparse
import configparser
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parents[1]
PUBLISH_URL = "https://upload.pypi.org/legacy/"


def publish_token():
    """Read environment credentials or the standard PyPI section without exposing secrets."""
    token = os.environ.get("UV_PUBLISH_TOKEN", "").strip()
    if token:
        return token
    path = Path.home() / ".pypirc"
    config = configparser.ConfigParser(interpolation=None)
    try:
        with path.open(encoding="utf-8") as stream:
            config.read_file(stream)
    except (OSError, UnicodeError, configparser.Error):
        raise ValueError(
            "Cannot read ~/.pypirc; supply UV_PUBLISH_TOKEN or a valid [pypi] token configuration."
        ) from None
    if not config.has_section("pypi"):
        raise ValueError("Missing [pypi] section in ~/.pypirc.")
    repository = config.get("pypi", "repository", fallback=PUBLISH_URL).strip()
    if repository.rstrip("/") != PUBLISH_URL.rstrip("/"):
        raise ValueError("The ~/.pypirc [pypi] repository must be the standard PyPI upload URL.")
    username = config.get("pypi", "username", fallback="").strip()
    token = config.get("pypi", "password", fallback="").strip()
    if username != "__token__" or not token:
        raise ValueError("The ~/.pypirc [pypi] section requires username = __token__ and a password token.")
    return token


def bump_component(version):
    """Select uv's bump component while preserving single-digit minor/patch rollover."""
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d\.\d", version):
        raise ValueError("Release version must have a numeric major and single-digit minor and patch.")
    _, minor, patch = version.split(".")
    if patch != "9":
        return "patch"
    return "major" if minor == "9" else "minor"


def release():
    """Validate credentials, prepare metadata, bump with uv, and publish only fresh artifacts."""
    token = publish_token()
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    component = bump_component(project["project"]["version"])
    subprocess.run([sys.executable, str(ROOT / "ez/prepublish.py")], cwd=ROOT, check=True)
    subprocess.run(["uv", "version", "--bump", component, "--frozen"], cwd=ROOT, check=True)
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    with tempfile.TemporaryDirectory(prefix="ez-release-") as directory:
        subprocess.run(["uv", "build", "--out-dir", directory], cwd=ROOT, check=True)
        output = Path(directory)
        artifacts = [output / f"ez-{version}.tar.gz", output / f"ez-{version}-py3-none-any.whl"]
        if any(not artifact.is_file() for artifact in artifacts):
            raise ValueError("uv build did not produce the expected sdist and universal wheel.")
        dist = ROOT / "dist"
        dist.mkdir(exist_ok=True)
        targets = [dist / artifact.name for artifact in artifacts]
        if any(target.exists() for target in targets):
            raise ValueError("Release artifacts already exist for this version; refusing to overwrite them.")
        retained = []
        for artifact, target in zip(artifacts, targets):
            shutil.copy2(artifact, target)
            retained.append(str(target))
        for previous in dist.iterdir():
            if (
                previous not in targets
                and previous.is_file()
                and previous.name.startswith("ez-")
                and previous.name.endswith((".tar.gz", ".whl"))
            ):
                previous.unlink()
        environment = os.environ.copy()
        environment["UV_PUBLISH_TOKEN"] = token
        subprocess.run(
            ["uv", "publish", "--publish-url", PUBLISH_URL,
             "--trusted-publishing", "never", *retained],
            cwd=ROOT, env=environment, check=True,
        )
    print(f"Published ez {version}; artifacts retained in dist/.", flush=True)


def main(argv=None):
    """Run the upload stage or show side-effect-free help."""
    parser = argparse.ArgumentParser(
        description="Prepare and upload ez with uv; use publish.sh for the complete release.",
        epilog="Credentials: UV_PUBLISH_TOKEN, otherwise ~/.pypirc [pypi]. Never pass secrets as arguments.",
    )
    parser.parse_args(argv)
    try:
        release()
    except subprocess.CalledProcessError as exc:
        print(
            f"Release command failed (exit {exc.returncode}). "
            "Version/artifacts may already be updated; inspect before retrying. "
            "Any completed uploads remain published.",
            file=sys.stderr,
        )
        return exc.returncode if exc.returncode > 0 else 1
    except (OSError, ValueError, KeyError) as exc:
        print(f"Release failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
