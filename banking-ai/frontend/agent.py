import os
import time
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, DeferredToolRequests, ModelRetry, RunContext, SkipToolExecution, UsageLimits
from pydantic_ai.capabilities import Hooks
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from api import BankAPI

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

model = OpenRouterModel(
    "google/gemini-4-hydrogen",
    provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
)


@dataclass
class BankDeps:
    user_name: str
    api: BankAPI


class TransferSummary(BaseModel):
    transaction_id: int
    recipient: str
    amount: Decimal
    new_balance: Decimal
    message: str


TRANSFER_LIMIT = Decimal("100000")

hooks = Hooks()


@hooks.on.before_tool_execute
async def audit_log(ctx: RunContext[BankDeps], *, call, tool_def, args):
    with open("audit.log", "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} user={ctx.deps.user_name} tool={call.tool_name} args={args}\n")
    return args


@hooks.on.before_tool_execute(tools=["transfer_money"])
async def security_check(ctx: RunContext[BankDeps], *, call, tool_def, args):
    if not ctx.tool_call_approved:
        raise SkipToolExecution("Blocked: transfers need the user's approval.")
    if Decimal(str(args["amount"])) > TRANSFER_LIMIT:
        raise SkipToolExecution(f"Blocked: amount is above the ₹{TRANSFER_LIMIT:,} limit.")
    return args


@hooks.on.tool_execute
async def measure_time(ctx: RunContext[BankDeps], *, call, tool_def, args, handler):
    start = time.perf_counter()
    result = await handler(args)
    print(f"[tool] {call.tool_name} took {time.perf_counter() - start:.2f}s")
    return result


bank_info = MCPToolset(Path(__file__).parent.parent / "mcp_server" / "bank_info.py")

agent = Agent(
    model,
    deps_type=BankDeps,
    output_type=[str, DeferredToolRequests],
    toolsets=[bank_info],
    capabilities=[hooks],
    instructions=(
        "You are pyGuru Bank's assistant. You help the logged-in user with their own accounts only. "
        "Amounts are in Indian rupees, write them like ₹5,000. "
        "Always use the tools to get balances and transactions, never guess numbers. "
        "To send money, find the beneficiary first, then call transfer_money. "
        "Keep answers short."
    ),
)


@agent.instructions
def user_name(ctx: RunContext[BankDeps]) -> str:
    return f"The user's name is {ctx.deps.user_name}."


@agent.tool
def get_balance(ctx: RunContext[BankDeps]) -> list[dict]:
    """Get the user's accounts with their balances."""
    return ctx.deps.api.accounts()


@agent.tool
def get_transactions(ctx: RunContext[BankDeps], limit: int = Field(default=5, ge=1, le=20)) -> list[dict]:
    """Get the user's latest transactions, newest first."""
    return ctx.deps.api.transactions(limit)


@agent.tool
def list_beneficiaries(ctx: RunContext[BankDeps]) -> list[dict]:
    """List the people the user can send money to."""
    return ctx.deps.api.beneficiaries()


@agent.tool(requires_approval=True)
def transfer_money(
    ctx: RunContext[BankDeps],
    beneficiary_name: str,
    amount: Decimal = Field(gt=0, decimal_places=2),
    note: str | None = None,
) -> TransferSummary:
    """Send money from the user's account to a saved beneficiary."""
    matches = [b for b in ctx.deps.api.beneficiaries() if b["name"].lower() == beneficiary_name.lower()]
    if not matches:
        raise ModelRetry(f"No beneficiary called {beneficiary_name}. Call list_beneficiaries and use an exact name.")
    account = ctx.deps.api.accounts()[0]
    txn = ctx.deps.api.transfer(account["account_number"], matches[0]["account_number"], float(amount),
                                note, idempotency_key=ctx.tool_call_id)
    balance = ctx.deps.api.accounts()[0]["balance"]
    return TransferSummary(transaction_id=txn["id"], recipient=matches[0]["name"], amount=amount,
                           new_balance=Decimal(str(balance)), message="Transfer completed")


LIMITS = UsageLimits(request_limit=8, tool_calls_limit=10)
