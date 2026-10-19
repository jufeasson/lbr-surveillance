import datetime as dt
import io
import unittest
from monitor import BASE, NoRedirect, checks_at, probe
import urllib.error


class Response(io.BytesIO):
    status = 200

    def __init__(self, url, body, content_type):
        super().__init__(body)
        self.url = url
        self.headers = {"Content-Type": content_type}

    def geturl(self):
        return self.url


class Opener:
    def __init__(self, response):
        self.response = response

    def open(self, request, timeout):
        assert timeout == 10
        return self.response


class Tests(unittest.TestCase):
    def test_night_guard_paris_and_first_day(self):
        for stamp, count in [("2026-10-19T12:00:00+02:00", 2),
                             ("2026-10-20T05:59:00+02:00", 2),
                             ("2026-10-20T06:00:00+02:00", 3),
                             ("2026-10-25T06:00:00+01:00", 3)]:
            self.assertEqual(len(checks_at(dt.datetime.fromisoformat(stamp))), count)

    def test_strict_health_and_bounds(self):
        url = BASE + "/api/health-v2.php"
        for body, mime, expected in [(b'{"status":"ok"}', "application/json", True),
                                     (b'{"status":"unavailable"}', "application/json", False),
                                     (b'{"status":"ok","other":1}', "application/json", False),
                                     (b'{"status":"ok"}', "text/html", False),
                                     (b" " * 257, "application/json", False)]:
            self.assertEqual(probe(url, "health", Opener(Response(url, body, mime))), expected)

    def test_redirect_rejected(self):
        with self.assertRaises(urllib.error.HTTPError):
            NoRedirect().redirect_request(urllib.request.Request(BASE), None, 302, "", {}, "https://example.invalid")


if __name__ == "__main__":
    unittest.main()
