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
              ("Traitements serveur", BASE + "/api/health-v2.php", "health"),
              # Incident 149: the health check never reads Microsoft Bookings.
              ("Creneaux de reservation", BASE + "/api/reservation-v2.php", "slots")]
    paris = now.astimezone(ZoneInfo("Europe/Paris"))
    if paris.date() >= FIRST_NIGHT and paris.hour >= 6:
        checks.append(("Sauvegarde nocturne", BASE + "/api/health-v2.php?check=nightly-backup", "health"))
    return checks


# The public slots read can legitimately take up to its 10 s server budget.
TIMEOUTS = {"home": 10, "health": 10, "slots": 15}
CAPS = {"home": 262144, "health": 256, "slots": 65536}


def probe(url, kind, opener):
    headers = {"User-Agent": "LBR-public-monitor/1.0"}
    if kind == "slots":
        # Same read-only GET as the booking page; no JavaScript, so no Analytics.
        headers.update({"X-LBR-Request": "reservation-v2", "Cache-Control": "no-cache"})
    request = urllib.request.Request(url, headers=headers)
    with opener.open(request, timeout=TIMEOUTS[kind]) as response:
        if response.status != 200 or response.geturl() != url:
            return False
        cap = CAPS[kind]
        data = response.read(cap + 1)
        if len(data) > cap:
            return False
        if kind == "home":
            return "text/html" in response.headers.get("Content-Type", "") and b"Le Bouton Rouge" in data and b"CEE" in data
        if "application/json" not in response.headers.get("Content-Type", ""):
            return False
        value = json.loads(data)
        if kind == "slots":
            # An empty week is a business state, not an outage: only the shape is required.
            return (isinstance(value, dict) and set(value) == {"ok", "slots"}
                    and value["ok"] is True and isinstance(value["slots"], list))
        return value == {"status": "ok"}


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
