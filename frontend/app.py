import os
from decimal import Decimal, InvalidOperation
from uuid import UUID

import requests
import streamlit as st

st.set_page_config(
    page_title="Transaction Ledger",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def api_request(method: str, path: str, **kwargs):
    """Call the FastAPI backend and show readable API errors."""
    url = f"{st.session_state.api_base_url.rstrip('/')}{path}"
    try:
        response = requests.request(method, url, timeout=20, **kwargs)
    except requests.RequestException as exc:
        st.error(
            f"Could not connect to the FastAPI backend at {url}. "
            "Make sure the backend is running, then try again."
        )
        with st.expander("Technical details"):
            st.code(str(exc))
        return None

    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        st.error(f"API error ({response.status_code}): {detail}")
        return None

    if response.status_code == 204 or not response.content:
        return {}
    try:
        return response.json()
    except ValueError:
        return {"message": response.text}


def valid_uuid(value: str) -> bool:
    try:
        UUID(value.strip())
        return True
    except (ValueError, AttributeError):
        return False


if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = DEFAULT_API_URL
if "account_id" not in st.session_state:
    st.session_state.account_id = ""
if "refresh_key" not in st.session_state:
    st.session_state.refresh_key = 0

with st.sidebar:
    st.title("💳 Transaction Ledger")
    st.caption("Basic Streamlit frontend for the FastAPI + Supabase API")
    st.text_input(
        "FastAPI base URL",
        key="api_base_url",
        help="Example: http://127.0.0.1:8000",
    )
    st.markdown("---")
    st.subheader("Select an account")
    account_input = st.text_input(
        "Account UUID",
        value=st.session_state.account_id,
        placeholder="Paste an account UUID",
        key="account_input",
    )
    if st.button("Use this account", use_container_width=True):
        if valid_uuid(account_input):
            st.session_state.account_id = account_input.strip()
            st.session_state.refresh_key += 1
            st.success("Account selected.")
            st.rerun()
        else:
            st.error("Enter a valid account UUID.")

    if st.session_state.account_id:
        st.caption(f"Selected: `{st.session_state.account_id}`")

st.title("Transaction Ledger Dashboard")
st.write("Create accounts, check balances, record transactions, transfer funds, and review transaction history.")

tab_dashboard, tab_account, tab_transaction, tab_transfer, tab_history = st.tabs(
    ["Dashboard", "Create account", "Credit / Debit", "Transfer", "History"]
)

with tab_dashboard:
    left, right = st.columns([2, 1])
    with left:
        st.subheader("API status")
        if st.button("Check backend health"):
            health = api_request("GET", "/health")
            if health is not None:
                st.success(f"Backend response: {health}")
    with right:
        st.subheader("Selected account")
        if not st.session_state.account_id:
            st.info("Select an account UUID in the sidebar.")
        else:
            if st.button("Refresh balance", use_container_width=True):
                st.session_state.refresh_key += 1
            balance_data = api_request(
                "GET", f"/accounts/{st.session_state.account_id}/balance"
            )
            if balance_data:
                st.metric("Current balance", f"{balance_data.get('balance', '—')}")
                st.caption(balance_data.get("name", "Account"))
                st.caption(f"Account ID: {balance_data.get('id', st.session_state.account_id)}")

with tab_account:
    st.subheader("Create a new account")
    st.info("The API creates every account with an initial balance of 0.")
    with st.form("create_account_form", clear_on_submit=True):
        account_name = st.text_input("Account holder / account name", max_chars=100)
        create_submitted = st.form_submit_button("Create account", type="primary")
    if create_submitted:
        if not account_name.strip():
            st.warning("Enter an account name.")
        else:
            result = api_request("POST", "/accounts", json={"name": account_name.strip()})
            if result is not None:
                new_id = result.get("id") or result.get("account_id")
                st.success("Account created successfully.")
                st.json(result)
                if new_id:
                    st.session_state.account_id = str(new_id)
                    st.session_state.refresh_key += 1
                    st.rerun()

with tab_transaction:
    st.subheader("Record a credit or debit")
    if not st.session_state.account_id:
        st.warning("Select an account UUID in the sidebar first.")
    else:
        st.caption(f"Account: `{st.session_state.account_id}`")
        with st.form("transaction_form", clear_on_submit=True):
            transaction_type = st.selectbox("Transaction type", ["credit", "debit"])
            amount_text = st.text_input("Amount", placeholder="e.g. 125.50")
            description = st.text_input("Description", placeholder="e.g. Invoice payment", max_chars=500)
            reference_id = st.text_input("Unique reference ID", placeholder="e.g. TXN-2026-001", max_chars=100)
            transaction_submitted = st.form_submit_button("Submit transaction", type="primary")
        if transaction_submitted:
            try:
                amount = Decimal(amount_text)
                if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -2:
                    raise InvalidOperation
            except (InvalidOperation, ValueError):
                st.error("Enter a positive amount with no more than 2 decimal places.")
            else:
                payload = {
                    "account_id": st.session_state.account_id,
                    "type": transaction_type,
                    "amount": str(amount),
                    "description": description.strip(),
                    "reference_id": reference_id.strip(),
                }
                if not reference_id.strip():
                    st.error("Reference ID is required.")
                else:
                    result = api_request("POST", "/transactions", json=payload)
                    if result is not None:
                        st.success("Transaction submitted successfully.")
                        st.json(result)
                        st.session_state.refresh_key += 1

with tab_transfer:
    st.subheader("Transfer money between accounts")
    st.caption("Transfers require two different existing accounts and sufficient source balance.")
    with st.form("transfer_form", clear_on_submit=True):
        from_account = st.text_input(
            "Source account UUID",
            value=st.session_state.account_id,
            placeholder="UUID of account to debit",
        )
        to_account = st.text_input("Destination account UUID", placeholder="UUID of account to credit")
        transfer_amount_text = st.text_input("Transfer amount", placeholder="e.g. 50.00")
        transfer_description = st.text_input("Description", value="Money transfer", max_chars=500)
        transfer_reference = st.text_input("Transfer reference ID", placeholder="e.g. TRF-2026-001", max_chars=100)
        transfer_submitted = st.form_submit_button("Transfer funds", type="primary")
    if transfer_submitted:
        try:
            transfer_amount = Decimal(transfer_amount_text)
            if not transfer_amount.is_finite() or transfer_amount <= 0 or transfer_amount.as_tuple().exponent < -2:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            st.error("Enter a positive transfer amount with no more than 2 decimal places.")
        else:
            if not valid_uuid(from_account) or not valid_uuid(to_account):
                st.error("Enter valid UUIDs for both accounts.")
            elif from_account.strip() == to_account.strip():
                st.error("Source and destination accounts must be different.")
            elif not transfer_reference.strip():
                st.error("Transfer reference ID is required.")
            else:
                payload = {
                    "from_account_id": from_account.strip(),
                    "to_account_id": to_account.strip(),
                    "amount": str(transfer_amount),
                    "description": transfer_description.strip(),
                    "reference_id": transfer_reference.strip(),
                }
                result = api_request("POST", "/transfers", json=payload)
                if result is not None:
                    st.success("Transfer completed.")
                    st.json(result)
                    st.session_state.refresh_key += 1

with tab_history:
    st.subheader("Transaction history")
    if not st.session_state.account_id:
        st.warning("Select an account UUID in the sidebar first.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            history_type = st.selectbox("Filter by type", ["all", "credit", "debit"])
        with c2:
            page = st.number_input("Page", min_value=1, value=1, step=1)
        with c3:
            limit = st.selectbox("Rows per page", [5, 10, 20, 50], index=1)
        if st.button("Load transaction history", type="primary"):
            params = {"page": int(page), "limit": int(limit)}
            if history_type != "all":
                params["type"] = history_type
            result = api_request(
                "GET",
                f"/accounts/{st.session_state.account_id}/transactions",
                params=params,
            )
            if result is not None:
                # Support either a direct list or the common {"items": [...]} response shape.
                rows = result if isinstance(result, list) else result.get("items", result.get("transactions", []))
                if rows:
                    st.dataframe(rows, use_container_width=True, hide_index=True)
                else:
                    st.info("No transactions found for this page/filter.")
                if isinstance(result, dict):
                    meta = {k: result[k] for k in ("page", "limit", "total", "total_pages") if k in result}
                    if meta:
                        st.caption(f"Pagination: {meta}")
                    with st.expander("Raw API response"):
                        st.json(result)

st.markdown("---")
st.caption("Demo frontend only. Keep Supabase credentials in the backend; never add them to this Streamlit app.")
