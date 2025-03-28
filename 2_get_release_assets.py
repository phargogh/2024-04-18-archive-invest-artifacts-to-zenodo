import collections
import json
import logging
import os

import requests

logging.basicConfig(level=logging.INFO)
JSON_FILENAME = 'release-dates.json'
LOGGER = logging.getLogger(os.path.basename(__file__))

try:
    with open(JSON_FILENAME, 'r') as release_dates_json:
        release_dates = json.load(release_dates_json)
except FileNotFoundError:
    print('Run $ python 1_get_versions_and_dates.py first')
    sys.exit(1)

RELEASE_ASSETS = collections.defaultdict(dict)
for version in release_dates.keys():
    LOGGER.info(f"Processing version {version}")

    # get the HEAD from each to see if there's a response.
    invest_repos = [
        f'https://github.com/natcap/{repo}/archive/refs/tags/{version}.zip'
        for repo in ['invest', 'invest.users-guide', 'invest.arcgis',
                     'invest-natcap.invest-3']]

    for label, repo in [
            ('InVEST source code', 'invest'),
            ('InVEST user guide', 'invest.users-guide'),
            ('InVEST ArcGIS Toolboxes (InVEST 2.x series)', 'invest.arcgis'),
            ('InVEST source code', 'invest-natcap.invest-3')]:
        url = (
            f'https://github.com/natcap/{repo}/'
            f'archive/refs/tags/{version}.zip')
        resp = requests.head(url)
        if resp.status_code >= 400:  # This isn't the right check. Some 302 pass
            LOGGER.info(f"Link does not exist: {url}")
            continue
        RELEASE_ASSETS[version][label] = url

        # instead, how about we merge the release assets into the
        # 1_get_versions_and_dates script?


print(json.dumps(RELEASE_ASSETS, indent=4, sort_keys=True))
