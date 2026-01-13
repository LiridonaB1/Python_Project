import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000/api")
DEFAULT_API_KEY = os.getenv("API_KEY", "")

st.set_page_config(page_title="Tech News Tracker", layout="wide")
st.title("📰 Tech News Tracker (Hacker News)")

# --- session state ---
if "authed" not in st.session_state:
    st.session_state.authed = False
if "api_key" not in st.session_state:
    st.session_state.api_key = DEFAULT_API_KEY

def verify_key(key: str) -> bool:
    try:
        r = requests.get(
            f"{BASE_URL}/auth/check",
            headers={"X-API-Key": key},
            timeout=10,
        )
        return r.ok
    except requests.RequestException:
        return False


if not st.session_state.authed:
    st.subheader("🔐 Enter API key to continue")

    key_input = st.text_input("X-API-Key", value=st.session_state.api_key, type="password")

    colA, colB = st.columns([1, 5])
    with colA:
        if st.button("Continue"):
            if not key_input.strip():
                st.error("Duhet të shkruash API key.")
            elif verify_key(key_input.strip()):
                st.session_state.api_key = key_input.strip()
                st.session_state.authed = True
                st.rerun()
            else:
                st.error("API key është gabim ose API nuk po përgjigjet.")
    st.caption(f"API Base: {BASE_URL}")
    st.stop()


api_key = st.session_state.api_key

with st.sidebar:
    st.header("Settings")
    st.write("API Base:", BASE_URL)

    limit = st.slider("Scrape limit", min_value=5, max_value=100, value=30, step=5)

    if st.button("🔄 Refresh from Hacker News"):
        r = requests.post(
            f"{BASE_URL}/articles/refresh?limit={limit}",
            headers={"X-API-Key": api_key},
            timeout=30,
        )
        if r.ok:
            st.success(r.json())
        else:
            st.error(f"{r.status_code}: {r.text}")

    if st.button("🚪 Logout"):
        st.session_state.authed = False
        st.session_state.api_key = ""
        st.rerun()

st.subheader("Browse Articles")

col1, col2, col3 = st.columns([2, 1, 1])
q = col1.text_input("Search title", value="")
saved_filter = col2.selectbox("Saved filter", ["All", "Saved only", "Not saved"])
page_size = col3.selectbox("Page size", [20, 50, 100], index=1)

saved_param = None
if saved_filter == "Saved only":
    saved_param = True
elif saved_filter == "Not saved":
    saved_param = False

params = {"limit": page_size, "offset": 0}
if q:
    params["q"] = q
if saved_param is not None:
    params["saved"] = saved_param

r = requests.get(f"{BASE_URL}/articles", params=params, timeout=30)
if not r.ok:
    st.error(f"API error: {r.status_code} {r.text}")
    st.stop()

data = r.json()
st.caption(f"Total in DB: {data['total']}")

for item in data["items"]:
    with st.container(border=True):
        left, right = st.columns([5, 1])
        left.markdown(f"### [{item['title']}]({item['url']})")
        left.caption(
            f"Points: {item['points']} | Comments: {item['comments']} | Source: {item['source']}"
        )

        is_saved = item["saved"]
        btn_label = "⭐ Unsave" if is_saved else "☆ Save"
        if right.button(btn_label, key=f"save_{item['id']}"):
            rr = requests.patch(
                f"{BASE_URL}/articles/{item['id']}/save",
                json={"saved": (not is_saved)},
                headers={"X-API-Key": api_key},
                timeout=30,
            )
            if rr.ok:
                st.rerun()
            else:
                st.error(f"{rr.status_code}: {rr.text}")
