from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from api import BankAPI
from assistant import assistant_page

st.set_page_config(page_title="pyGuru Bank", page_icon="🏦", layout="wide")
st.markdown(f"<style>{Path(__file__).with_name('style.css').read_text()}</style>", unsafe_allow_html=True)

if "token" not in st.session_state:
    st.session_state.token = None


def rupees(amount) -> str:
    return f"₹{float(amount):,.2f}"


def login_page():
    left, center, right = st.columns([1, 1.2, 1])
    with center:
        st.title("pyGuru Bank")
        st.caption("Simple, safe banking. Demo app with simulated money.")
        login_tab, register_tab = st.tabs(["Login", "Register"])

        with login_tab:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", type="primary", use_container_width=True):
                try:
                    st.session_state.token = BankAPI().login(email, password)
                    st.rerun()
                except ValueError as e:
                    st.error(e)

        with register_tab:
            name = st.text_input("Name")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            if st.button("Create account", type="primary", use_container_width=True):
                try:
                    BankAPI().register(name, email, password)
                    st.success("Account created! Now login.")
                except ValueError as e:
                    st.error(e)


def money_flow(txns, my_number):
    df = pd.DataFrame(txns)
    df["amount"] = df["amount"].astype(float)
    df["signed"] = df.apply(lambda t: t["amount"] if t["to_account"] == my_number else -t["amount"], axis=1)
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df.sort_values("id")


def dashboard():
    api = BankAPI(st.session_state.token)
    user = api.me()
    account = api.accounts()[0]
    txns = api.transactions(limit=50)

    st.sidebar.title("pyGuru Bank")
    st.sidebar.write(f"Hello, **{user['name']}**")
    page = st.sidebar.radio("Go to", ["Dashboard", "Assistant"])
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if page == "Assistant":
        assistant_page(st.session_state.token, user["name"])
        return

    st.title("Dashboard")
    df = money_flow(txns, account["account_number"]) if txns else None
    money_in = df[df["signed"] > 0]["signed"].sum() if df is not None else 0
    money_out = -df[df["signed"] < 0]["signed"].sum() if df is not None else 0

    card, stat_in, stat_out = st.columns([2, 1, 1])
    card.markdown(f"""
        <div class="bank-card">
            <div class="label">{account['account_type'].title()} account balance</div>
            <div class="balance">{rupees(account['balance'])}</div>
            <div class="number">{account['account_number'][:4]} {account['account_number'][4:8]} {account['account_number'][8:]}</div>
            <div class="name">{user['name']}</div>
        </div>""", unsafe_allow_html=True)
    stat_in.markdown(f"""<div class="stat-card"><div class="label">Money in</div>
        <div class="value green">{rupees(money_in)}</div></div>""", unsafe_allow_html=True)
    stat_out.markdown(f"""<div class="stat-card"><div class="label">Money out</div>
        <div class="value red">{rupees(money_out)}</div></div>""", unsafe_allow_html=True)

    st.write("")
    chart_col, action_col = st.columns([3, 2])

    with chart_col:
        st.subheader("Balance over time")
        if df is not None:
            df["balance"] = df["signed"].cumsum()
            chart = alt.Chart(df).mark_area(
                line={"color": "#4f46e5"}, color=alt.Gradient(
                    gradient="linear", x1=1, x2=1, y1=1, y2=0,
                    stops=[alt.GradientStop(color="white", offset=0), alt.GradientStop(color="#a5b4fc", offset=1)]),
            ).encode(x=alt.X("id:O", title="Transaction"), y=alt.Y("balance:Q", title="Balance (₹)"))
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No transactions yet.")

    with action_col:
        st.subheader("Quick actions")
        deposit_tab, withdraw_tab, transfer_tab, payees_tab = st.tabs(["Deposit", "Withdraw", "Transfer", "Beneficiaries"])

        with deposit_tab:
            amount = st.number_input("Amount", min_value=1.0, step=100.0, key="deposit_amount")
            if st.button("Deposit", type="primary"):
                try:
                    api.deposit(account["account_number"], amount)
                    st.rerun()
                except ValueError as e:
                    st.error(e)

        with withdraw_tab:
            amount = st.number_input("Amount", min_value=1.0, step=100.0, key="withdraw_amount")
            if st.button("Withdraw", type="primary"):
                try:
                    api.withdraw(account["account_number"], amount)
                    st.rerun()
                except ValueError as e:
                    st.error(e)

        with transfer_tab:
            payees = api.beneficiaries()
            if not payees:
                st.info("Add a beneficiary first.")
            else:
                names = {f"{p['name']} ({p['account_number']})": p["account_number"] for p in payees}
                to = st.selectbox("To", list(names))
                amount = st.number_input("Amount", min_value=1.0, step=100.0, key="transfer_amount")
                note = st.text_input("Note")
                if st.button("Send money", type="primary"):
                    try:
                        api.transfer(account["account_number"], names[to], amount, note)
                        st.rerun()
                    except ValueError as e:
                        st.error(e)

        with payees_tab:
            name = st.text_input("Beneficiary name")
            number = st.text_input("Account number", max_chars=12)
            if st.button("Add beneficiary", type="primary"):
                try:
                    api.add_beneficiary(name, number)
                    st.rerun()
                except ValueError as e:
                    st.error(e)

    st.subheader("Recent transactions")
    if df is not None:
        table = df.sort_values("id", ascending=False)[["created_at", "type", "note", "signed", "status"]]
        st.dataframe(table, hide_index=True, use_container_width=True, column_config={
            "created_at": st.column_config.DatetimeColumn("Date", format="D MMM YYYY, h:mm a"),
            "type": "Type", "note": "Note", "status": "Status",
            "signed": st.column_config.NumberColumn("Amount (₹)", format="%+.2f"),
        })


if st.session_state.token:
    dashboard()
else:
    login_page()
