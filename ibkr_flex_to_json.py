# pip install ibflex
import os, json, datetime, pathlib, ibflex

TOKEN   = os.getenv("FLEX_TOKEN")
QUERYID = os.getenv("FLEX_QUERY_ID")

xml_data = ibflex.Client(token=TOKEN).get(QUERYID, "xml")
parsed   = ibflex.parser.parse(xml_data)

snapshot = {
    "generated": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "positions": parsed["OpenPositions"],
    "cash":      parsed.get("CashReport", [])
}

pathlib.Path("latest.json").write_text(json.dumps(snapshot, indent=2))
print("latest.json written with", len(snapshot["positions"]), "positions")
