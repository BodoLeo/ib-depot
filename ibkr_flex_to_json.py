# pip install requests
import os, datetime, pathlib, requests

TOKEN   = os.getenv("FLEX_TOKEN")
QUERYID = os.getenv("FLEX_QUERY_ID")
BASE    = "https://gdcdyn.interactivebrokers.com/Universal/servlet/"

def send_request():
    r = requests.get(
        BASE + "FlexStatementService.SendRequest",
        params=dict(t=TOKEN, q=QUERYID, v="3"), timeout=30
    )
    r.raise_for_status()
    return r.text                     # schon als XML-String

def store(xml: str):
    stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"raw_{stamp}.xml"        # z. B. raw_20250730T204501Z.xml
    pathlib.Path(fname).write_text(xml)
    pathlib.Path("raw.xml").write_text(xml)  # letzter Bericht (symlink-Ersatz)
    print("✅  XML saved as", fname, "and raw.xml")

if __name__ == "__main__":
    store(send_request())
