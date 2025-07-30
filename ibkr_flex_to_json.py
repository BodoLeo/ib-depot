# pip install requests xmltodict
import os, json, datetime, pathlib, requests, xmltodict

TOKEN   = os.getenv("FLEX_TOKEN")
QUERYID = os.getenv("FLEX_QUERY_ID")
BASE    = "https://gdcdyn.interactivebrokers.com/Universal/servlet/"

def send_request():
    r = requests.get(f"{BASE}FlexStatementService.SendRequest",
                     params=dict(t=TOKEN, q=QUERYID, v="3"), timeout=30)
    r.raise_for_status()
    ref = xmltodict.parse(r.text)["FlexStatementResponse"]["ReferenceCode"]
    return ref

def get_statement(ref):
    r = requests.get(f"{BASE}FlexStatementService.GetStatement",
                     params=dict(t=TOKEN, q=QUERYID, v="3", ref=ref), timeout=60)
    r.raise_for_status()
    return xmltodict.parse(r.text)

def extract_statement(xml: dict):
    """Gibt das erste (und bei dir einzige) FlexStatement-Dict zurück."""
    if "FlexStatements" in xml and "FlexStatement" in xml["FlexStatements"]:
        return xml["FlexStatements"]["FlexStatement"]
    if "FlexStatement" in xml:
        return xml["FlexStatement"]
    # Fallback: eine Ebene tiefer durchsuchen
    for v in xml.values():
        if isinstance(v, dict) and "FlexStatement" in v:
            return v["FlexStatement"]
    raise KeyError("FlexStatement nicht gefunden")

def main():
    stmt_xml = get_statement(send_request())
    stmt     = extract_statement(stmt_xml)

    # Positionen können Dict (einzelne Pos.) oder Liste sein → immer Liste machen
    positions = stmt.get("OpenPositions", {}).get("OpenPosition", [])
    if isinstance(positions, dict):
        positions = [positions]

    cash = stmt.get("CashReport", {}).get("CashBalances", [])
    if isinstance(cash, dict):
        cash = [cash]

    snapshot = {
        "generated": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "positions": positions,
        "cash":      cash,
    }

    pathlib.Path("latest.json").write_text(json.dumps(snapshot, indent=2))
    print("✅ latest.json created –", len(positions), "positions,", len(cash), "cash lines")

if __name__ == "__main__":
    main()
