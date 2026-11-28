import asyncio

import streamlit as st
from pydantic_ai import (AgentRunResultEvent, DeferredToolRequests, DeferredToolResults,
                         FunctionToolCallEvent, PartDeltaEvent, TextPartDelta, ToolDenied)

from agent import LIMITS, BankDeps, agent
from api import BankAPI

TOOL_LABELS = {
    "get_balance": "Checking your balance",
    "get_transactions": "Reading your transactions",
    "list_beneficiaries": "Looking up your beneficiaries",
    "transfer_money": "Sending money",
    "get_exchange_rate": "Fetching today's exchange rate",
    "find_branch": "Finding the branch",
    "search_faq": "Searching the FAQ",
}


async def run_agent(prompt, deps, deferred_results=None):
    box = st.empty()
    text = ""
    result = None
    async with agent.run_stream_events(prompt, deps=deps, message_history=st.session_state.history,
                                       deferred_tool_results=deferred_results, usage_limits=LIMITS) as events:
        async for event in events:
            if isinstance(event, FunctionToolCallEvent):
                st.caption(f"{TOOL_LABELS.get(event.part.tool_name, event.part.tool_name)}...")
            elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                text += event.delta.content_delta
                box.markdown(text)
            elif isinstance(event, AgentRunResultEvent):
                result = event.result
    return result


def handle(result):
    st.session_state.history = result.all_messages()
    if isinstance(result.output, DeferredToolRequests):
        st.session_state.pending = result.output
    else:
        st.session_state.chat.append({"role": "assistant", "content": result.output})


def assistant_page(token, user_name):
    st.title("Banking Assistant")
    st.session_state.setdefault("chat", [])
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("pending", None)
    deps = BankDeps(user_name=user_name, api=BankAPI(token))

    for message in st.session_state.chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    pending = st.session_state.pending
    if pending:
        call = pending.approvals[0]
        args = call.args_as_dict()
        with st.chat_message("assistant"):
            with st.container(border=True):
                st.markdown("**Approval required**")
                st.write(f"Send **₹{float(args['amount']):,.2f}** to **{args['beneficiary_name']}**")
                if args.get("note"):
                    st.write(f"Note: {args['note']}")
                approve, reject = st.columns(2)
                decision = None
                if approve.button("Approve", type="primary"):
                    decision = True
                if reject.button("Reject"):
                    decision = ToolDenied("The user rejected this transfer.")
            if decision is not None:
                st.session_state.pending = None
                results = DeferredToolResults(approvals={call.tool_call_id: decision})
                result = asyncio.run(run_agent(None, deps, results))
                handle(result)
                st.rerun()

    if prompt := st.chat_input("Ask about your account, or send money..."):
        st.session_state.chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            result = asyncio.run(run_agent(prompt, deps))
        handle(result)
        st.rerun()
