import json
import os


def main():
    with open('release-dates.json') as release_file:
        github_data = json.load(release_file)

    with open('all-InVEST-artifacts.json') as data_file:
        artifact_data = json.load(data_file)

    consolidated_artifacts = {}
    assert github_data.keys() == artifact_data.keys()

    for version in github_data.keys():
        version_artifacts = {}

        for key, value in github_data[version].items():
            if key in {'date', ""}:
                continue
            version_artifacts[key] = value

        list_keys = {'data', 'release_artifacts'}
        exclude_keys = {'date'}
        for key, value in artifact_data[version].items():
            if key in exclude_keys:
                continue

            if key in list_keys:
                for url in artifact_data[version][key]:
                    if url in version_artifacts.values():
                        continue
                    if not url:
                        continue
                    version_artifacts[os.path.basename(url)] = url
            else:
                url = value
                if url in version_artifacts.values():
                    continue
                version_artifacts[os.path.basename(url)] = url

        consolidated_artifacts[version] = version_artifacts

    with open('consolidated-artifacts.json', 'w') as artifacts_file:
        artifacts_file.write(json.dumps(consolidated_artifacts, indent=4,
                                        sort_keys=True))


if __name__ == '__main__':
    main()
