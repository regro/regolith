#!/usr/bin/env python3
import base64
import re
import tomllib
from datetime import datetime  # noqa
from typing import Any, Dict, List, Optional

import requests

GITHUB_API = "https://api.github.com"


class GitHubRepoExtractor:
    def __init__(self, owner: str, repo: str, token: Optional[str] = None):
        """Constructor for the GitHubRepoExtractor.

        Parameters
        ----------
        owner: str
            The name of the owner of the package.
        repo: str
            The name of the repository.
        token: str
            The private token for GitHub.
        """
        self.owner = owner
        self.repo = repo
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/vnd.github+json", "User-Agent": "github-repo-extractor"}
        )
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _get(self, path: str) -> Any:
        url = f"{GITHUB_API}{path}"
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def get_repo_metadata(self) -> Dict[str, Any]:
        """Get the metadata of the repository.

        Returns
        -------
        The dictionary of the metadata for the repository.
        """
        return self._get(f"/repos/{self.owner}/{self.repo}")

    def get_contributors(self) -> List[Dict[str, Any]]:
        """Get the contributors of the repository.

        Returns
        -------
        The list of names of the contributors for the repository.
        """
        return self._get(f"/repos/{self.owner}/{self.repo}/contributors")

    def get_releases(self) -> List[Dict[str, Any]]:
        """Get the summaries of each release of the repository.

        Returns
        -------
        The dictionary of releases for the repository.
        """

        return self._get(f"/repos/{self.owner}/{self.repo}/releases")

    def get_file(self, path: str) -> Optional[str]:
        """Get the corresponding file based on path given.

        Parameters
        ----------
        path: str
            The absolute/relative path of the file.

        Returns
        -------
        The decoded file based on the path.
        """
        try:
            data = self._get(f"/repos/{self.owner}/{self.repo}/contents/{path}")
            content = base64.b64decode(data["content"])
            return content.decode("utf-8")
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-rc\.(\d+))?$")

    def parse_version(self, tag: str) -> Optional[Dict[str, Any]]:
        """Parse the version of the repository with a given tag.

        Parameters
        ----------
        tag: str
            The tag/version of the package. The default format is <*.*.*>

        Returns
        -------
        The parsed version of the tag
        """
        match = self.VERSION_RE.match(tag)
        if not match:
            return None

        major, minor, patch, rc = match.groups()
        major, minor, patch = int(major), int(minor), int(patch)

        prerelease = rc is not None
        release_type = "pre-release" if prerelease else "patch" if patch > 0 else "minor" if minor > 0 else "major"

        return {
            "major": major,
            "minor": minor,
            "patch": patch,
            "release_type": release_type,
            "pre_release": int(rc) if prerelease else None,
        }

    def parse_release(self, release: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse the releases of the repository.

        Parameters
        ----------
        release: The dictionary of all releases for the given repository.

        Returns
        -------
        The parsed dictionary of each release for the given repository.
        """
        version = self.parse_version(release["tag_name"])
        if not version:
            return None

        body = release.get("body") or ""
        changes = [line.lstrip("- ").strip() for line in body.splitlines() if line.strip().startswith("-")]

        return {
            **{k: v for k, v in version.items() if v is not None},
            "release_date": release["published_at"][:10],
            "summary": release.get("name") or "",
            "changes": changes,
            "release_id": release["tag_name"],
        }

    def extract_authors(self) -> List[str]:
        """Extract the author of the repository.

        Returns
        -------
        The list of names who are (co)authors of the repository.
        """
        contributors = self.get_contributors()
        return [contributor["login"] for contributor in contributors]

    def extract_releases(self) -> List[Dict[str, Any]]:
        """Extract releases history of the repository.

        Returns
        -------
        The parsed releases of the repository.
        """
        releases = self.get_releases()
        parsed = []
        for release in releases:
            pr = self.parse_release(release)
            if pr:
                parsed.append(pr)
        return parsed

    def extract(self) -> Dict[str, Any]:
        """Wrapper of extractor for all metadata of a given repository.

        Returns
        -------
        The dictionary of metadata of the repository.e
        """
        repo = self.get_repo_metadata()
        pyproject = self.get_file("pyproject.toml")

        data = {
            "_id": f"{repo['owner']['login']}.{repo['name']}",
            "active": not repo["archived"] and not repo["disabled"],
            "author": self.extract_authors(),
            "org_name": repo["owner"]["login"],
            "repo_name": repo["name"],
            "platform_name": "Github",
            "program_description": (
                tomllib.loads(pyproject)["project"]["description"] if pyproject else repo.get("description")
            ),
            "grants": "all",
            "release": self.extract_releases(),
        }

        return data

    def get_owner_type(self) -> str:
        """Detect whether the owner is a user or an organization.

        Returns
        -------
        str
            "org" or "user"
        """
        data = self._get(f"/users/{self.owner}")
        return "org" if data.get("type") == "Organization" else "user"

    def get_active_repositories_for_owner(self) -> List[Dict[str, Any]]:
        """Get all active repositories for the owner.

        Returns
        -------
        List of repository dictionaries.
        """
        owner_type = self.get_owner_type()
        page = 1
        repos: List[Dict[str, Any]] = []

        while True:
            if owner_type == "org":
                path = f"/orgs/{self.owner}/repos"
            else:
                path = f"/users/{self.owner}/repos"

            response = self._get(f"{path}?per_page=100&page={page}")
            if not response:
                break
            for repo in response:
                if not repo.get("archived") and not repo.get("disabled"):
                    repos.append(repo)
            page += 1
        return repos

    def extract_all_active_repositories(self) -> List[Dict[str, Any]]:
        """Extract metadata for all active repositories under the owner.

        Returns
        -------
        List of extracted repository metadata dictionaries.
        """
        repos = self.get_active_repositories_for_owner()
        results = []

        for repo in repos:
            repo_name = repo["name"]
            extractor = GitHubRepoExtractor(self.owner, repo_name)
            extractor.session = self.session
            try:
                results.append(extractor.extract())
            except Exception as exc:
                print(f"Skipping {self.owner}/{repo_name}: {exc}")
        return results


def extract_github(
    owner: str,
    repo: Optional[str] = None,
    *,
    all_repos: bool = False,
    token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Programmatic entry point for Regolith."""
    if all_repos:
        extractor = GitHubRepoExtractor(owner, "", token)
        return extractor.extract_all_active_repositories()
    else:
        if not repo:
            raise ValueError("repo must be provided unless --all is set")
        extractor = GitHubRepoExtractor(owner, repo, token)
        return [extractor.extract()]


def to_software_yaml(data):
    """Convert a list of software records into a YAML-ready dictionary
    keyed by software ID.

    Parameters
    ----------
    data: dict
        The list of dicts of software metadata.

    Returns
    -------
    The dicttionary for yaml file of all software.
    """
    yaml_data = {}
    for entry in data:
        full_id = entry["_id"]
        software_id = full_id.split(".", 1)[1]
        content = {k: v for k, v in entry.items() if k != "_id"}
        yaml_data[software_id] = content
    return yaml_data
