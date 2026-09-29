#!/usr/bin/env python3
import hashlib
import json
import os
import posixpath
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from packaging.version import Version


def md5sum(filename) -> str:
    with open(filename, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def get_jellyfin_version(csproj: str) -> str:
    tree = ET.parse(csproj)
    root = tree.getroot()

    for pkg in root.iter("PackageReference"):
        if pkg.attrib.get("Include") in ("Jellyfin.Controller", "Jellyfin.Model"):
            return Version(pkg.attrib.get("Version")).base_version

    raise Exception("Jellyfin version not found")


def get_repository() -> str:
    repository = os.environ.get('GITHUB_REPOSITORY')
    if repository:
        return repository.rstrip('/').removesuffix('.git')

    remote = subprocess.check_output(
        ['git', 'config', '--get', 'remote.origin.url'], text=True
    ).strip()
    match = re.search(r'github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$', remote)
    if not match:
        raise Exception(f'Unable to determine GitHub repository from remote: {remote}')

    return match.group(1)


def generate(filename, version, csproj, repository) -> dict:
    return {
        'checksum': md5sum(filename),
        'changelog': 'Auto Released by Actions',
        'targetAbi': f'{get_jellyfin_version(csproj)}.0',
        'sourceUrl': f'https://github.com/{repository}/releases/download/'
                     f'v{version}/{posixpath.basename(filename)}',
        'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'version': version
    }


def main() -> None:
    filename = sys.argv[1]
    version = filename.split('@', maxsplit=1)[1] \
        .removeprefix('v') \
        .removesuffix('.zip')

    csproj = os.path.join(os.path.dirname(__file__),
                          "../Jellyfin.Plugin.MetaTube/Jellyfin.Plugin.MetaTube.csproj")
    repository = get_repository()
    manifest_urls = [
        f'https://raw.githubusercontent.com/{repository}/dist/manifest.json',
        'https://raw.githubusercontent.com/metatube-community/jellyfin-plugin-metatube/'
        'dist/manifest.json'
    ]

    for manifest_url in manifest_urls:
        try:
            with urlopen(manifest_url) as f:
                manifest = json.load(f)
            break
        except (HTTPError, URLError):
            continue
    else:
        raise Exception('Unable to download an existing plugin manifest')

    manifest[0]['versions'].insert(0, generate(filename, version, csproj, repository))

    with open('manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)


if __name__ == '__main__':
    main()
