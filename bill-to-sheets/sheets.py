import os
import requests
import gspread
from dotenv import load_dotenv

load_dotenv()
HEADERS = ["File", "Shop", "Date", "Month", "Category", "Currency", "Total", "Rate", "Total (INR)", "Items"]

gc = gspread.service_account(filename="service_account.json")
sheet = gc.open_by_key(os.getenv("SHEET_ID"))


def get_tab(name, rows=1000, cols=12):
    try:
        return sheet.worksheet(name)
    except gspread.WorksheetNotFound:
        return sheet.add_worksheet(title=name, rows=rows, cols=cols)


bills_tab = get_tab("Bills")
if bills_tab.row_values(1) != HEADERS:
    bills_tab.update([HEADERS], "A1")


def to_inr(amount, currency, date):
    if currency == "INR":
        return 1.0, amount
    url = f"https://api.frankfurter.dev/v1/{date}?base={currency}&symbols=INR"
    rate = requests.get(url, timeout=10).json()["rates"]["INR"]
    return rate, round(amount * rate, 2)


def already_added():
    rows = bills_tab.get_all_records()
    files = {r["File"] for r in rows}
    bills = {(r["Shop"], r["Date"], float(r["Total"])) for r in rows}
    return files, bills


def add_bill(file_name, bill):
    rate, inr = to_inr(bill.total, bill.currency, bill.date)
    items = ", ".join(f"{i.name} x{i.quantity:g}" for i in bill.items)
    row = [file_name, bill.shop, bill.date, bill.date[:7], bill.category,
           bill.currency, bill.total, rate, inr, items]
    bills_tab.append_row(row, value_input_option="RAW")
    return inr


def write_summary():
    rows = bills_tab.get_all_records()
    months = sorted({r["Month"] for r in rows})
    categories = sorted({r["Category"] for r in rows})
    tab = get_tab("Summary")
    tab.clear()
    table = [["Month"] + categories + ["Total"]]
    for i, month in enumerate(months, start=2):
        line = [month]
        for cat in categories:
            line.append(f'=SUMIFS(Bills!I:I, Bills!D:D, $A{i}, Bills!E:E, "{cat}")')
        last = gspread.utils.rowcol_to_a1(i, len(categories) + 1)
        line.append(f"=SUM(B{i}:{last})")
        table.append(line)
    tab.update(table, "A1", value_input_option="USER_ENTERED")
    add_chart(tab, len(months), len(categories))


def add_chart(tab, n_months, n_cats):
    meta = sheet.fetch_sheet_metadata()
    for s in meta["sheets"]:
        if s["properties"]["sheetId"] == tab.id:
            for chart in s.get("charts", []):
                sheet.batch_update({"requests": [{"deleteEmbeddedObject": {"objectId": chart["chartId"]}}]})

    def col(c):
        return {"sourceRange": {"sources": [{"sheetId": tab.id, "startRowIndex": 0, "endRowIndex": n_months + 1,
                                              "startColumnIndex": c, "endColumnIndex": c + 1}]}}

    chart = {"spec": {"title": "Monthly spend (INR)", "basicChart": {
        "chartType": "COLUMN", "legendPosition": "BOTTOM_LEGEND", "headerCount": 1, "stackedType": "STACKED",
        "domains": [{"domain": col(0)}],
        "series": [{"series": col(c), "targetAxis": "LEFT_AXIS"} for c in range(1, n_cats + 1)]}},
        "position": {"overlayPosition": {"anchorCell": {"sheetId": tab.id, "rowIndex": n_months + 2, "columnIndex": 0}}}}
    sheet.batch_update({"requests": [{"addChart": {"chart": chart}}]})
