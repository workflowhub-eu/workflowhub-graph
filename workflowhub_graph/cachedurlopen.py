

from unittest.mock import patch, MagicMock
from contextlib import contextmanager
import io


cached_urls = {
        "https://w3id.org/ro/crate/1.0/context": "ro-crate-context-1.0.json",
        "https://w3id.org/ro/crate/1.1/context": "ro-crate-context-1.1.json",
    }


@contextmanager
def patch_rdflib_urlopen(file_locator):    
    def cached_urlopen(request):
        url = request.get_full_url()
        
        if url not in cached_urls:
            # TODO: store and use cache
            raise ValueError(f"URL {url} not in cache, have: {cached_urls.keys()}")

        class Response(io.StringIO):
            content_type = "text/html"
            headers = {"Content-Type": "text/html"}

            def info(self):
                return self.headers
            
            def geturl(self):
                return url
            
        content = open(file_locator(cached_urls[url]), "rt").read()

        return Response(content)
    
    with patch("rdflib.parser.urlopen", cached_urlopen):
        yield

