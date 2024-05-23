import os
import requests


def main():
    # TODO: this is very preliminary, needs to be improved
    
    token = os.getenv("ZENODO_ACCESS_TOKEN")

    if token is None:
        raise Exception("ZENODO_ACCESS_TOKEN environment variable is not set")

    headers = {"Content-Type": "application/json"}
    params = {'access_token': token}
    r = requests.post('https://sandbox.zenodo.org/api/deposit/depositions',
                    params=params,
                    json={},
                    headers=headers
                    )
    
    if r.status_code != 201:
        raise Exception(f'Failed to create deposition: {r} {r.text}')
    
    print(r.json())
    
    bucket_url = r.json()["links"]["bucket"]

    
    for filename in "merged.ttl", "merged.pdf":
        path = filename

        with open(path, "rb") as fp:
            r = requests.put(
                "%s/%s" % (bucket_url, filename),
                data=fp,
                params=params,
            )
        r.json()
        if r.status_code != 201:
            raise Exception(f'Failed to upload file: {r} {r.text}')


if __name__ == "__main__":
    main()