import os
import sys
import base64
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
MODEL = "google/gemini-4-hydrogen"


class Item(BaseModel):
    name: str
    quantity: float
    price: float


class Bill(BaseModel):
    shop: str
    date: str
    currency: str
    items: list[Item]
    tax: float
    total: float
    category: str


PROMPT = (
    "Read this bill and fill every field. Write the date as YYYY-MM-DD. "
    "Category must be one of: Groceries, Food, Travel, Health, Software, Bills, Shopping, Other."
)


def file_part(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    if path.lower().endswith(".pdf"):
        url = f"data:application/pdf;base64,{data}"
        return {"type": "file", "file": {"filename": os.path.basename(path), "file_data": url}}
    url = f"data:image/jpeg;base64,{data}"
    return {"type": "image_url", "image_url": {"url": url}}


def read_bill(path):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": [{"type": "text", "text": PROMPT}, file_part(path)]}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "bill", "schema": Bill.model_json_schema()},
        },
    )
    return Bill.model_validate_json(response.choices[0].message.content)


if __name__ == "__main__":
    bill = read_bill(sys.argv[1])
    print(bill.model_dump_json(indent=2))
