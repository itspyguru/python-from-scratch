import os
from extract import read_bill
from gmail_fetch import download_bills
from sheets import already_added, add_bill, write_summary

download_bills()

files, bills = already_added()
for name in sorted(os.listdir("bills")):
    if name in files:
        print("Skip (already added):", name)
        continue
    bill = read_bill(os.path.join("bills", name))
    key = (bill.shop, bill.date, bill.total)
    if key in bills:
        print("Skip (same bill, another file):", name)
        continue
    inr = add_bill(name, bill)
    files.add(name)
    bills.add(key)
    print(f"Added {name}: {bill.shop} {bill.currency} {bill.total} = Rs {inr}")

write_summary()
print("Summary updated")
