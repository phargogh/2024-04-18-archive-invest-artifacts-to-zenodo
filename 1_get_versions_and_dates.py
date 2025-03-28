"""Retrieve all VCS-controlled InVEST versions and their release dates.

This script is part of a pipeline to upload InVEST release artifacts to Zenodo.
The version of the release and its release date are both an important part of
the metadata that Zenodo needs.

A json file with this information is written.
"""
import collections
import datetime
import json
import logging
import os
import subprocess

import requests

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(os.path.basename(__file__))
REPOS = {
    "invest": {
        "label": "InVEST source code",
    },
    "invest-natcap.invest-3": {
        "label": "InVEST source code",
    },
    "invest.arcgis": {
        "label": "InVEST ArcGIS Toolboxes (InVEST 2.x series)",
    },
    "invest.users-guide": {
        "label": "InVEST User's Guide",
    },
}
RELEASE_ASSETS = collections.defaultdict(dict)
for repo_slug, repo_data in REPOS.items():
    if not os.path.exists(repo_slug):
        LOGGER.info(f"Cloning {repo_slug}")
        subprocess.run(
            ["git", "clone", f"https://github.com/natcap/{repo_slug}.git"])
    else:
        LOGGER.info(f"{repo_slug} exists, fetching latest changes")
        subprocess.run(["git", "--work-tree", repo_slug, "fetch", "--tags"],
                       check=True)

    tag_process = subprocess.run(
        ["git", "--work-tree", repo_slug, "tag", "-l"],
        capture_output=True, check=True)
    tags = [tag.strip() for tag in
            tag_process.stdout.decode('ascii').split('\n')
            if tag]
    LOGGER.info(f'{repo_slug}: Processing {len(tags)} tags')
    for index, tag in enumerate(tags):
        LOGGER.info(f'Processing tag {tag}')
        try:
            int(tag[0])  # skip any tags that aren't normal InVEST versions
        except ValueError:
            continue

        date_proc = subprocess.run(
            ['git', '--work-tree', repo_slug, 'log', '-n1',
             '--format=%ci', tag],
            capture_output=True, check=True)

        # format is 2021-10-29 13:35:28 -0400
        date = datetime.datetime.fromisoformat(
            date_proc.stdout.decode('ascii').split(' ')[0])

        if tag not in RELEASE_ASSETS:
            RELEASE_ASSETS[tag]['date'] = date
        else:
            known_release_date = RELEASE_ASSETS[tag]['date']
            if known_release_date != date:
                print(f"Conflicting dates for {tag}, "
                      f"{RELEASE_ASSETS[tag]['date']} vs "
                      f"{date}, taking the later date")
            RELEASE_ASSETS[tag]['date'] = max(date, known_release_date)

        url = (f'https://github.com/natcap/{repo_slug}'
               f'/archive/refs/tags/{tag}.zip')
        if not requests.head(url).ok:
            LOGGER.warning(f"Archive asset not found at {url}")
            continue
        else:
            RELEASE_ASSETS[tag][repo_data['label']] = url
    LOGGER.info(f"Finished processing tags for repo {repo_slug}")

for key, value in RELEASE_ASSETS.items():
    try:
        RELEASE_ASSETS[key]['date'] = value['date'].date().isoformat()
    except Exception:
        LOGGER.exception(f"Could not parse date on key: {key}, value: {value}")
        continue

# This was clearly a version typo on the invest-natcap.invest-3 repo.
RELEASE_ASSETS['2.2.1rc1'].update(RELEASE_ASSETS['2.21rc1'])
del RELEASE_ASSETS['2.21rc1']

with open('release-dates.json', 'w') as release_dates_json:
    release_dates_json.write(
        json.dumps(RELEASE_ASSETS, indent=4, sort_keys=True))
