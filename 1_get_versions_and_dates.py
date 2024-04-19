"""Retrieve all VCS-controlled InVEST versions and their release dates.

This script is part of a pipeline to upload InVEST release artifacts to Zenodo.
The version of the release and its release date are both an important part of
the metadata that Zenodo needs.

A json file with this information is written.
"""
import datetime
import json
import logging
import os
import subprocess

LOGGER = logging.getLogger(os.path.basename(__file__))
REPO_SLUGS = ["invest", "invest.users-guide", "invest.arcgis",
              "invest-natcap.invest-3"]
RELEASE_DATES = {}
for repo_slug in REPO_SLUGS:
    if not os.path.exists(repo_slug):
        LOGGER.info(f"Cloning {repo_slug}")
        subprocess.run(
            ["git", "clone", f"https://github.com/natcap/{repo_slug}.git"])
    else:
        LOGGER.info(f"{repo_slug} exists, fetching latest changes")
        subprocess.run(["git", "-C", repo_slug, "fetch"])

    tag_process = subprocess.run(["git", "-C", repo_slug, "tag", "-l"],
                                 capture_output=True)
    for tag in tag_process.stdout.decode('ascii').split('\n'):
        tag = tag.strip()
        if not tag:  # There's usually a blank line in the printout
            continue

        try:
            int(tag[0])  # skip any tags that aren't normal InVEST versions
        except ValueError:
            continue

        date_proc = subprocess.run(
            ['git', '-C', repo_slug, 'log', '-n1', '--format=%ci', tag],
            capture_output=True)

        # format is 2021-10-29 13:35:28 -0400
        date = datetime.datetime.fromisoformat(
            date_proc.stdout.decode('ascii').split(' ')[0])

        if tag not in RELEASE_DATES:
            RELEASE_DATES[tag] = date
        else:
            known_release_date = RELEASE_DATES[tag]
            if known_release_date != date:
                print(f"Conflicting dates for {tag}, {RELEASE_DATES[tag]} vs"
                      f"{date}, taking the later date")
            RELEASE_DATES[tag] = max(date, known_release_date)

for key, value in RELEASE_DATES.items():
    RELEASE_DATES[key] = value.date().isoformat()

with open('release-dates.json', 'w') as release_dates_json:
    release_dates_json.write(
        json.dumps(RELEASE_DATES, indent=4, sort_keys=True))
