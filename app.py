import streamlit as st
import json
import sys
import os
import pandas as pd

sys.path.insert(0, "sdoc-hackathon-bundle")
from loader import Inbox
import extraction
import comparison
import doc_parser
import classification
import llm_extraction

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SDOC Verifier",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main .block-container { padding-top: 1rem; }
    .status-ok { background-color: #d4edda; color: #155724; padding: 8px 16px; border-radius: 8px; font-weight: bold; font-size: 1.2em; text-align: center; }
    .status-mismatch { background-color: #f8d7da; color: #721c24; padding: 8px 16px; border-radius: 8px; font-weight: bold; font-size: 1.2em; text-align: center; }
    .status-review { background-color: #fff3cd; color: #856404; padding: 8px 16px; border-radius: 8px; font-weight: bold; font-size: 1.2em; text-align: center; }
    .category-badge { padding: 4px 10px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .cat-bl { background-color: #cce5ff; color: #004085; }
    .cat-si { background-color: #d4edda; color: #155724; }
    .cat-inv { background-color: #fff3cd; color: #856404; }
    .cat-gen { background-color: #e2e3e5; color: #383d41; }
    .cat-spam { background-color: #f8d7da; color: #721c24; }
    .field-match { background-color: #d4edda; }
    .field-mismatch { background-color: #f8d7da; }
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_emails():
    inbox = Inbox("sdoc-hackathon-bundle")
    return inbox.emails()

@st.cache_data
def load_inbox():
    return Inbox("sdoc-hackathon-bundle")

emails = load_emails()
inbox = load_inbox()

CATEGORY_LABELS = {
    "BL_COMPARISON": ("📄 BL Comparison", "cat-bl"),
    "SI_REQUEST": ("📋 SI Request", "cat-si"),
    "INVOICE_QUERY": ("💰 Invoice Query", "cat-inv"),
    "GENERAL": ("📧 General", "cat-gen"),
    "SPAM": ("🚫 Spam", "cat-spam"),
}

FIELD_LABELS = {
    "shipper": "Shipper",
    "consignee": "Consignee",
    "notify_party": "Notify Party",
    "port_of_loading": "Port of Loading",
    "port_of_discharge": "Port of Discharge",
    "container_count": "Container Count",
    "gross_weight_kg": "Gross Weight (KG)",
}

# ── Sidebar: Inbox ──────────────────────────────────────────────────────────
st.sidebar.title("🚢 SDOC Verifier")
st.sidebar.caption("Shipping Document Verification System")
st.sidebar.divider()

# LLM Settings
with st.sidebar.expander("⚙️ AI Model Settings", expanded=False):
    use_llm = st.checkbox("Enable LLM-powered extraction", value=False)
    llm_provider = st.selectbox("Provider", ["openai", "anthropic"], index=0)
    if llm_provider == "openai":
        api_key = st.text_input("OpenAI API Key", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    else:
        api_key = st.text_input("Anthropic API Key", type="password", value=os.environ.get("ANTHROPIC_API_KEY", ""))
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key

st.sidebar.divider()

# Filter
filter_cat = st.sidebar.selectbox(
    "Filter by category",
    ["All", "BL_COMPARISON", "SI_REQUEST", "INVOICE_QUERY", "GENERAL", "SPAM"],
    index=0,
)

# Classify all emails and build list
classified = []
for em in emails:
    cat = classification.classify_email(em)
    classified.append((em, cat))

if filter_cat != "All":
    classified = [(em, cat) for em, cat in classified if cat == filter_cat]

st.sidebar.markdown(f"**{len(classified)} emails**")
st.sidebar.divider()

# Email list
selected_idx = None
for i, (em, cat) in enumerate(classified):
    label, css = CATEGORY_LABELS.get(cat, ("❓ Unknown", "cat-gen"))
    truncated_subject = em['subject'][:50] + "..." if len(em['subject']) > 50 else em['subject']
    if st.sidebar.button(
        f"**{em['email_id']}**\n{truncated_subject}",
        key=f"email_{i}",
        use_container_width=True,
    ):
        st.session_state.selected_email_idx = i

# ── Main content ─────────────────────────────────────────────────────────────
if "selected_email_idx" not in st.session_state:
    # Landing page
    st.title("🚢 Shipping Document Verification System")
    st.markdown("### Automated SI vs BL Comparison Pipeline")
    st.markdown("---")

    # Stats
    cats = [cat for _, cat in classified]
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📄 BL Comparison", cats.count("BL_COMPARISON"))
    col2.metric("📋 SI Requests", cats.count("SI_REQUEST"))
    col3.metric("💰 Invoice", cats.count("INVOICE_QUERY"))
    col4.metric("📧 General", cats.count("GENERAL"))
    col5.metric("🚫 Spam", cats.count("SPAM"))

    st.markdown("---")
    st.info("👈 Select an email from the sidebar to begin verification.")

    # Architecture diagram
    st.markdown("### System Architecture")
    st.markdown("""
    ```
    ┌─────────────┐    ┌──────────────────┐    ┌──────────────┐    ┌────────────────┐
    │  Email Inbox │───▶│  Classification   │───▶│  Extraction  │───▶│   Comparison   │
    │  (520 emails)│    │  (5 categories)  │    │  (7 fields)  │    │  (SI vs BL)    │
    └─────────────┘    └──────────────────┘    └──────────────┘    └────────────────┘
                                                      │                     │
                                                      ▼                     ▼
                                               ┌──────────────┐    ┌────────────────┐
                                               │  LLM Fallback│    │  OK / MISMATCH │
                                               │  (GPT/Claude)│    │  NEEDS_REVIEW  │
                                               └──────────────┘    └────────────────┘
    ```
    """)
else:
    idx = st.session_state.selected_email_idx
    email, category = classified[idx]
    eid = email["email_id"]

    # Header
    label, css = CATEGORY_LABELS.get(category, ("❓ Unknown", "cat-gen"))
    st.markdown(f"## 📧 {eid}")
    st.markdown(f'<span class="category-badge {css}">{label}</span>', unsafe_allow_html=True)
    st.markdown("---")

    # Email details
    col_meta1, col_meta2 = st.columns(2)
    col_meta1.markdown(f"**From:** {email['from']}")
    col_meta2.markdown(f"**Attachments:** {len(email.get('attachments', []))}")
    st.markdown(f"**Subject:** {email['subject']}")

    with st.expander("📨 Email Body", expanded=False):
        st.text(email["body"])

    st.markdown("---")

    if category == "BL_COMPARISON":
        attachments = email.get("attachments", [])
        si_path = next((a for a in attachments if "si" in a.lower()), None)
        bl_path = next((a for a in attachments if "bl" in a.lower()), None)

        if not si_path and len(attachments) >= 1:
            si_path = attachments[0]
        if not bl_path and len(attachments) >= 2:
            bl_path = attachments[1]

        if not si_path or not bl_path:
            st.markdown('<div class="status-review">⚠️ NEEDS REVIEW — Missing Attachment</div>', unsafe_allow_html=True)
        else:
            # Parse documents
            si_bytes = inbox.read_bytes(si_path)
            bl_bytes = inbox.read_bytes(bl_path)
            si_text = doc_parser.extract_text_from_bytes(si_bytes, si_path)
            bl_text = doc_parser.extract_text_from_bytes(bl_bytes, bl_path)

            if not si_text.strip() or not bl_text.strip():
                st.markdown('<div class="status-review">⚠️ NEEDS REVIEW — Unreadable Document</div>', unsafe_allow_html=True)
            else:
                # Show raw documents side by side
                st.markdown("### 📑 Source Documents")
                doc_col1, doc_col2 = st.columns(2)
                with doc_col1:
                    st.markdown(f"**Shipping Instruction (SI)** — `{os.path.basename(si_path)}`")
                    st.code(si_text[:2000], language=None)
                with doc_col2:
                    st.markdown(f"**Draft Bill of Lading (BL)** — `{os.path.basename(bl_path)}`")
                    st.code(bl_text[:2000], language=None)

                st.markdown("---")

                # Extract fields
                si_fields_regex = extraction.extract_fields(si_text)
                bl_fields_regex = extraction.extract_fields(bl_text)

                si_fields = si_fields_regex
                bl_fields = bl_fields_regex

                llm_used = False
                if use_llm and api_key:
                    with st.spinner(f"🤖 Running {llm_provider.upper()} extraction..."):
                        si_llm = llm_extraction.llm_extract_fields(si_text, provider=llm_provider)
                        bl_llm = llm_extraction.llm_extract_fields(bl_text, provider=llm_provider)

                    if si_llm and bl_llm:
                        llm_used = True
                        # Merge: use LLM values to fill in regex gaps
                        for field in FIELD_LABELS:
                            if si_fields.get(field) is None and si_llm.get(field) is not None:
                                si_fields[field] = si_llm[field]
                            if bl_fields.get(field) is None and bl_llm.get(field) is not None:
                                bl_fields[field] = bl_llm[field]

                # Compare
                status, has_defect, defect_fields, review_reason = comparison.compare_fields(si_fields, bl_fields)

                # Status banner
                st.markdown("### 🔍 Verification Result")
                if status == "OK":
                    st.markdown('<div class="status-ok">✅ OK — No Mismatch Detected</div>', unsafe_allow_html=True)
                elif status == "MISMATCH":
                    st.markdown(f'<div class="status-mismatch">❌ MISMATCH — {len(defect_fields)} field(s) differ</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="status-review">⚠️ NEEDS REVIEW — {review_reason}</div>', unsafe_allow_html=True)

                if llm_used:
                    st.caption(f"🤖 Enhanced with {llm_provider.upper()} LLM extraction")

                st.markdown("")

                # Comparison table
                st.markdown("### 📊 Field-by-Field Comparison")
                rows = []
                for field, label in FIELD_LABELS.items():
                    si_val = si_fields.get(field)
                    bl_val = bl_fields.get(field)
                    match = field not in defect_fields
                    rows.append({
                        "Field": label,
                        "SI Value": str(si_val) if si_val is not None else "—",
                        "BL Value": str(bl_val) if bl_val is not None else "—",
                        "Status": "✅ Match" if match else "❌ Mismatch",
                    })

                df = pd.DataFrame(rows)

                def highlight_row(row):
                    if row["Status"] == "❌ Mismatch":
                        return ["background-color: #f8d7da"] * len(row)
                    else:
                        return ["background-color: #d4edda"] * len(row)

                st.dataframe(
                    df.style.apply(highlight_row, axis=1),
                    use_container_width=True,
                    hide_index=True,
                )

                # Defect summary
                if defect_fields:
                    st.markdown("### ⚠️ Discrepancies Found")
                    for f in defect_fields:
                        label = FIELD_LABELS.get(f, f)
                        si_v = si_fields.get(f, "—")
                        bl_v = bl_fields.get(f, "—")
                        st.error(f"**{label}:** SI = `{si_v}` → BL = `{bl_v}`")

    else:
        # Non-BL emails
        st.info(f"This email was classified as **{label}**. No document comparison is needed.")
        st.markdown("Only **BL Comparison** emails proceed to the extraction and comparison stage.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.caption("Built for the SDOC Hackathon 2026")
