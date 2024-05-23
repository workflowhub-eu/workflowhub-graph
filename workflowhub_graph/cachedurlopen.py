import os
import re
from unittest.mock import patch, MagicMock
from contextlib import contextmanager
import io
from urllib.parse import urlparse
from urllib.request import urlopen


def url_to_filename(url):
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        raise ValueError(f"Unsupported scheme {parsed.scheme}")

    return re.sub("[^0-9a-z]+", "-", (parsed.netloc + parsed.path).lower().strip("_"))


@contextmanager
def patch_rdflib_urlopen(
    cache_base_dir=None,
    write_cache=True,
    allowed_urls_pattern=r"https://w3id.org/ro/crate/1\.[01]/context",
):
    allowed_urls_re = re.compile(allowed_urls_pattern)
    if cache_base_dir is None:
        cache_base_dir = "cached_urlopen"
        os.makedirs(cache_base_dir, exist_ok=True)

    def cached_urlopen(request):
        url = request.get_full_url()

        if not allowed_urls_re.match(url):
            raise ValueError(
                f"URL {url} not allowed to cache, allowed: {allowed_urls_pattern}"
            )

        class Response(io.StringIO):
            content_type = "text/html"
            headers = {"Content-Type": "text/html"}

            def info(self):
                return self.headers

            def geturl(self):
                return url

        cached_filename = os.path.join(cache_base_dir, url_to_filename(url))

        if not os.path.exists(cached_filename):
            if write_cache:
                response = urlopen(request)
                content = response.read().decode("utf-8")

                with open(cached_filename, "wt") as f:
                    f.write(content)
            else:
                raise ValueError(
                    f"Cache file {cached_filename} not found, not allowed to download and update cache"
                )

        content = open(cached_filename, "rt").read()

        return Response(content)

    with patch("rdflib.parser.urlopen", cached_urlopen):
        yield
