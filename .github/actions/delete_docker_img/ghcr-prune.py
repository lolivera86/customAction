#!/usr/bin/python3
import os
import requests
from datetime import datetime, timedelta


# GitHub API documentation: https://docs.github.com/en/rest/reference/packages
github_api_accept = 'application/vnd.github.v3+json'
# https://docs.github.com/en/rest/overview/api-versions?apiVersion=2022-11-28
github_api_version = '2022-11-28'


if __name__ == "__main__":
    prune_age = os.environ['INPUT_PRUNE-AGE'];
    container = os.environ['INPUT_CONTAINER'];
    dry_run = os.environ['INPUT_DRY-RUN'];
    token = os.environ['INPUT_GITHUB-TOKEN'];
    
    if token is None:
        raise ValueError('missing authentication token')

    s = requests.Session()
    s.headers.update({'Authorization': f'token {token}',
                      'Accept': github_api_accept,
                      'X-GitHub-Api-Version': github_api_version})

    del_before = datetime.now().astimezone() - timedelta(days=prune_age) \
        if prune_age is not None else None
    if del_before:
        print(f'Pruning images created before {del_before}')

    list_url: str | None = 'https://api.github.com/user/packages/' \
        f'container/{container}/versions'

    while list_url is not None:
        r = s.get(list_url)
        if 'link' in r.headers and 'next' in r.links:
            list_url = r.links['next']['url']
        else:
            list_url = None

        versions = r.json()

        for v in versions:
            created = datetime.fromisoformat(v['created_at'])
            metadata = v["metadata"]["container"]
            print(f'{v["id"]}\t{v["name"]}\t{created}\t{metadata["tags"]}')

            # prune old untagged images if requested
            if del_before is not None and created < del_before \
               and len(metadata['tags']) == 0:
                if dry_run:
                    print(f'would delete {v["id"]}')
                else:
                    r = s.delete(
                        'https://api.github.com/user/packages/'
                        f'container/{container}/versions/{v["id"]}')
                    r.raise_for_status()
                    print(f'deleted {v["id"]}')