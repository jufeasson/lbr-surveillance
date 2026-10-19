"""Public HTTPS smoke checks only; no credentials or access to customer data."""
import argparse
import datetime as dt
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

BASE = "https://www.leboutonrouge.fr"
FIRST_NIGHT = dt.date(2026, 10, 20)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "redirect refused", headers, fp)


def checks_at(now):
    checks = [("Accueil HTTPS", BASE + "/", "home"),
              ("Traitements serveur", BASE + "/api/health-v2.php", "health")]
    paris = now.astimezone(ZoneInfo("Europe/Paris"))
    if paris.date() >= FIRST_NIGHT and paris.hour >= 6:
        checks.append(("Sauvegarde nocturne", BASE + "/api/health-v2.php?check=nightly-backup", "health"))
    return checks


def probe(url, kind, opener):
    request = urllib.request.Request(url, headers={"User-Agent": "LBR-public-monitor/1.0"})
    with opener.open(request, timeout=10) as response:
        if response.status != 200 or response.geturl() != url:
            return False
        cap = 262144 if kind == "home" else 256
        data = response.read(cap + 1)
        if len(data) > cap:
            return False
        if kind == "home":
            return "text/html" in response.headers.get("Content-Type", "") and b"Le Bouton Rouge" in data and b"CEE" in data
        return ("application/json" in response.headers.get("Content-Type", "")
                and json.loads(data) == {"status": "ok"})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exercise", action="store_true")
    args = parser.parse_args()
    if args.exercise:
        print("TEST LBR : echec volontaire pour verifier la notification GitHub. Site inchange.")
        return 1
    opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    failed = False
    for name, url, kind in checks_at(dt.datetime.now(dt.timezone.utc)):
        ok = False
        for attempt in range(3):
            try:
                ok = probe(url, kind, opener)
            except (OSError, ValueError, urllib.error.HTTPError):
                ok = False
            if ok:
                break
            if attempt < 2:
                time.sleep(5)
        # Never log response bodies, headers, customer identifiers or arbitrary errors.
        print(name + (" : OK" if ok else " : A VERIFIER (3 essais)"))
        failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
