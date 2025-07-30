# pip install requests xmltodict
import os, json, datetime, pathlib, requests, xmltodict

TOKEN   = os.getenv("FLEX_TOKEN")
QUERYID = os.getenv("FLEX_QUERY_ID")
BASE    = "https://gdcdyn.interactivebrokers.com/Universal/servlet/"

def send_request():
    url = f"{BASE}FlexStatementService.SendRequest"
    params = dict(t=TOKEN, q=QUERYID, v="3")
    res = requests.get(url, params=params, timeout=30)
    res.raise_for_status()
    data = xmltodict.parse(res.text)
    return data["FlexStatementResponse"]["ReferenceCode"]

def get_statement(refcode: str):
    url = f"{BASE}FlexStatementService.GetStatement"
    params = dict(t=TOKEN, q=QUERYID, v="3", ref=refcode)
    res = requests.get(url, params=params, timeout=60)
    res.raise_for_status()
    return xmltodict.parse(res.text)

def main():
    ref = send_request()
    xml = get_statement(ref)
    if "FlexStatements" in xml:
        stmt = xml["FlexStatements"]["FlexStatement"]
    else:                       # Einzel-Statement
        stmt = xml["FlexStatement"]


    snapshot = {
        "generated": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "positions": stmt.get("OpenPositions", {}).get("OpenPosition", []),
        "cash":      stmt.get("CashReport", {}).get("CashBalances", []),
    }

    pathlib.Path("latest.json").write_text(json.dumps(snapshot, indent=2))
    print("latest.json written with",
          len(snapshot["positions"]), "positions and",
          len(snapshot["cash"]), "cash lines")

if __name__ == "__main__":
    main()
