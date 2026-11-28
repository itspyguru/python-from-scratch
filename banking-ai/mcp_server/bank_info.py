import httpx
from mcp.server.mcpserver import MCPServer

server = MCPServer("pyGuru Bank Info")

BRANCHES = {
    "pune": "pyGuru Bank, FC Road, Shivajinagar, Pune 411005. Open Mon-Sat, 10 am to 4 pm.",
    "mumbai": "pyGuru Bank, Linking Road, Bandra West, Mumbai 400050. Open Mon-Sat, 10 am to 4 pm.",
    "delhi": "pyGuru Bank, Connaught Place, New Delhi 110001. Open Mon-Sat, 10 am to 4 pm.",
}

FAQS = {
    "transfer limit": "You can transfer up to 1,00,000 rupees per transaction.",
    "interest rate": "Savings accounts earn 3.5% interest per year, paid every quarter.",
    "lost card": "Block your card from the app or call 1800-000-000 (demo number).",
}


@server.tool()
def get_exchange_rate(currency: str) -> str:
    """Get today's rate for 1 unit of a foreign currency (like USD or EUR) in Indian rupees."""
    response = httpx.get(f"https://api.frankfurter.dev/v1/latest?base={currency.upper()}&symbols=INR", timeout=10)
    response.raise_for_status()
    data = response.json()
    return f"1 {currency.upper()} = {data['rates']['INR']} INR (date {data['date']})"


@server.tool()
def find_branch(city: str) -> str:
    """Find the pyGuru Bank branch address and timings in a city."""
    return BRANCHES.get(city.lower(), f"No branch in {city}. We have branches in Pune, Mumbai and Delhi.")


@server.tool()
def search_faq(question: str) -> str:
    """Search the bank's FAQ for things like transfer limit, interest rate or lost card."""
    for topic, answer in FAQS.items():
        if topic in question.lower():
            return answer
    return "No FAQ found. Topics: " + ", ".join(FAQS)


if __name__ == "__main__":
    server.run()
