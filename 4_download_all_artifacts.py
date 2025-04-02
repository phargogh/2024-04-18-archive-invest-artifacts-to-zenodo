import json
import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(os.path.basename(__file__))
ASSETS_DIR = 'assets'

with open('consolidated-artifacts.json') as artifacts_file:
    artifacts_by_version = json.load(artifacts_file)

with open('release-dates.json') as dates_file:
    dates_by_version = json.load(dates_file)

for version, version_data in artifacts_by_version.items():
    LOGGER.info(f"Processing {version}")
    date = dates_by_version[version]['date']

    download_dir = os.path.join(ASSETS_DIR, f'assets-{version}')
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for filename, source_url in version_data.items():
        target_filename = os.path.join(download_dir, filename)
        subprocess.run(
            ['wget', '-N', '-O', target_filename, source_url], check=True)
