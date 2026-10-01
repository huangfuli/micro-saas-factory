from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class SmokeChecker:
    def check(self, base_url: str, paths: list[str]) -> dict[str, bool]:
        base = base_url.rstrip("/")
        results = {}
        for path in paths:
            url = base + (path if path.startswith("/") else "/" + path)
            request = Request(
                url,
                headers={"User-Agent": "micro-saas-factory-launch/0.1"},
            )
            try:
                with urlopen(request, timeout=20) as response:
                    results[path] = 200 <= response.status < 400
            except (HTTPError, URLError, TimeoutError):
                results[path] = False
        return results
