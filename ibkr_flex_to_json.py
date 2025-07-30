# pip install requests
import os, datetime, pathlib, requests

TOKEN   = os.getenv("FLEX_TOKEN")
QUERYID = os.getenv("FLEX_QUERY_ID")
BASE    = "https://gdcdyn.interactivebrokers.com/Universal/servlet/"

def send_request():
    """Step 1 – Liefert ReferenceCode für den Bericht."""
    r = requests.get(
        BASE + "FlexStatementService.SendRequest",
        params=dict(t=TOKEN, q=QUERYID, v="3"), timeout=30
    )
    r.raise_for_status()
    xml = r.text
    # Mini-Parsing ohne externe Bibliothek:
    start = xml.index("<ReferenceCode>") + 15
    end   = xml.index("</ReferenceCode>")
    return xml[start:end]

def get_statement(refcode):
    """Step 2 – Holt das komplette Depot-Statement."""
    r = requests.get(
        BASE + "FlexStatementService.GetStatement",
        params=dict(t=TOKEN, q=QUERYID, v="3", ref=refcode), timeout=60
    )
    r.raise_for_status()
    return r.text

def main():
    ref = send_request()
    xml = get_statement(ref)

    # Sicher speichern – einmal mit Zeitstempel (Archiv) & einmal als raw.xml
    ts   = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base = pathlib.Path(f"raw_{ts}.xml")
    base.write_text(xml)
    pathlib.Path("raw.xml").write_text(xml)  # letzte Version überschreiben
    print(f"✅  Depot-Statement gespeichert ({len(xml)} Bytes)")

if __name__ == "__main__":
    main()
