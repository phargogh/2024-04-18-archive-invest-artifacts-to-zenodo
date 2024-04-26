import json
import logging
import os
import pprint
import re
import subprocess

from packaging.version import parse
from packaging.version import Version

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(os.path.basename(__file__))


with open('release-dates.json') as release_dates:
    release_data = json.load(release_dates)
    tags = release_data.keys()


def _list_files_from_gsutil(gsutil_path, files_only=True):
    args = ['gsutil', 'ls', gsutil_path]
    if files_only:
        args.insert(2, '-d')
    gsutil_process = subprocess.run(
        args, capture_output=True)
    return [path.strip().replace('gs://', 'https://storage.googleapis.com/')
            for path in gsutil_process.stdout.decode(
                'ascii').strip().split('\n')]


tags = list(tags) + ['1.001', '1.002', '1.003', '1.004', '1.005', '2.0']

DATAPORTAL = 'gs://data.naturalcapitalproject.org'
RELEASES = 'gs://release.naturalcapitalproject.org'

LOGGER.info("Getting top-level files")
_TL_FILES_JSON = 'top-level-files.json'
if not os.path.exists(_TL_FILES_JSON):
    TOP_LEVEL_RELEASE_FILES = [
        path for path in _list_files_from_gsutil(
            f'{DATAPORTAL}/invest-releases/*.*')
        if not path.endswith('/')]
    with open(_TL_FILES_JSON, 'w') as tl_files_json:
        tl_files_json.write(json.dumps(TOP_LEVEL_RELEASE_FILES))
else:
    with open(_TL_FILES_JSON) as tl_files_json:
        TOP_LEVEL_RELEASE_FILES = json.load(tl_files_json)

LOGGER.info(pprint.pformat(TOP_LEVEL_RELEASE_FILES))


def _find_version_files(version_string, files=TOP_LEVEL_RELEASE_FILES):
    match_regex = version_string.replace('.', '[._]')
    match_regex = f'[a-zA-Z][_ -]{match_regex}[_ -]'
    return [file for file in files if bool(re.search(match_regex, file))]


for tag in sorted(tags):
    LOGGER.info(f'Getting links for tag {tag}')
    tag_ver = parse(str(tag))
    if Version('1.0.0') <= tag_ver < Version('2.0.0'):
        data_files = []  # sample data were distributed _in_ the installer
        release_files = _find_version_files(tag)
    if Version('2.0.0') <= tag_ver < Version('2.4.0'):
        # Data files are in the root of the invest-data directory
        data_files = _list_files_from_gsutil(f'{DATAPORTAL}/invest-data/*.zip')
        release_files = _find_version_files(tag)
        if tag_ver == Version('2.1'):  # 2.1.0 == 2.1 when parsed
            release_files += _find_version_files('2.1')
    elif Version('2.4.0') <= tag_ver <= Version('3.6.0'):
        # data files in their own dir of dataportal/invest-data
        data_files = _list_files_from_gsutil(
            f'{DATAPORTAL}/invest-data/{tag}/*.zip')
        release_files = _list_files_from_gsutil(
            f'{DATAPORTAL}/invest-releases/{tag}/*.*')
        pprint.pprint(release_files)
    elif Version('3.6.0') < tag_ver:
        # current data files are in release bucket/* and data are in
        # bucket/data (look for *_sample_data.zip)
        data_files = _list_files_from_gsutil(
            f'{RELEASES}/invest/{tag}/data/*.zip')
        release_files = _list_files_from_gsutil(
            f'{RELEASES}/invest/{tag}/*.*')

        # If a combined sample data file is present, use that instead of all of
        # the individual data files.  Sometimes it's in the data directory,
        # sometimes it's in the release artifact directory.
        for file in set(data_files + release_files):
            if os.path.basename(file) == f'InVEST_{tag}_sample_data.zip':
                data_files = [file]
                break

    # Some early releases are not tracked in source control and first appear in
    # this script.
    if tag not in release_data:
        release_data[tag] = {}

    release_data[tag]['data'] = data_files
    release_data[tag]['release_artifacts'] = release_files


with open('all-InVEST-artifacts.json', 'w') as artifacts_json:
    artifacts_json.write(json.dumps(release_data, indent=4, sort_keys=True))
