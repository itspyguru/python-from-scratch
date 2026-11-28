from pydantic_ai import DeferredToolRequests, DeferredToolResults

from api import BankAPI
from agent import BankDeps, agent

api = BankAPI(BankAPI().login("priya@example.com", "secret123"))
deps = BankDeps(user_name="Priya", api=api)

result = agent.run_sync("Send 500 to Rahul for lunch", deps=deps)

if isinstance(result.output, DeferredToolRequests):
    for call in result.output.approvals:
        print("Approval needed:", call.tool_name, call.args)
    answer = input("Approve? (y/n): ")
    approvals = {call.tool_call_id: answer == "y" for call in result.output.approvals}
    result = agent.run_sync(deps=deps, message_history=result.all_messages(),
                            deferred_tool_results=DeferredToolResults(approvals=approvals))

print(result.output)
