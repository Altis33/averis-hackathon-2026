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
    page_title="Snowbunnies — SDOC Verifier",
    page_icon="🐰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .main .block-container { padding-top: 1rem; max-width: 1200px; }
    
    .hero-title { 
        font-size: 2.4em; font-weight: 700; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .hero-subtitle { font-size: 1.1em; color: #6c757d; margin-top: 0; }
    .team-badge {
        display: inline-block; padding: 6px 16px; border-radius: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; font-weight: 600; font-size: 0.9em; margin-bottom: 1rem;
    }
    
    .status-ok { background-color: #d4edda; color: #155724; padding: 12px 20px; border-radius: 10px; font-weight: 700; font-size: 1.3em; text-align: center; border: 1px solid #c3e6cb; }
    .status-mismatch { background-color: #f8d7da; color: #721c24; padding: 12px 20px; border-radius: 10px; font-weight: 700; font-size: 1.3em; text-align: center; border: 1px solid #f5c6cb; }
    .status-review { background-color: #fff3cd; color: #856404; padding: 12px 20px; border-radius: 10px; font-weight: 700; font-size: 1.3em; text-align: center; border: 1px solid #ffeeba; }
    
    .category-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: 600; display: inline-block; }
    .cat-bl { background-color: #cce5ff; color: #004085; }
    .cat-si { background-color: #d4edda; color: #155724; }
    .cat-inv { background-color: #fff3cd; color: #856404; }
    .cat-gen { background-color: #e2e3e5; color: #383d41; }
    .cat-spam { background-color: #f8d7da; color: #721c24; }
    
    .metric-card {
        background: white; border-radius: 12px; padding: 20px; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #eee;
    }
    .metric-number { font-size: 2em; font-weight: 700; color: #333; }
    .metric-label { font-size: 0.85em; color: #888; margin-top: 4px; }
    
    .arch-box {
        background: #f8f9fa; border-radius: 12px; padding: 24px;
        border: 1px solid #e9ecef; margin: 16px 0;
    }
    
    div[data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #f8f9ff 0%, #ffffff 100%);
    }
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

# ── Classify all emails ─────────────────────────────────────────────────────
@st.cache_data
def classify_all(email_data):
    results = []
    for em in email_data:
        cat = classification.classify_email(em)
        results.append((em, cat))
    return results

classified = classify_all(emails)

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.markdown('<div class="team-badge">🐰 Team Snowbunnies</div>', unsafe_allow_html=True)
st.sidebar.title("SDOC Verifier")
st.sidebar.caption("Shipping Document Verification System")
st.sidebar.divider()

# AI Settings
with st.sidebar.expander("⚙️ AI Model Settings", expanded=False):
    use_llm = st.checkbox("Enable LLM-powered extraction", value=False)
    llm_provider = st.selectbox("Provider", ["openai", "anthropic"], 
                                format_func=lambda x: "OpenAI (GPT-4o-mini)" if x == "openai" else "Anthropic (Claude Sonnet)")
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
    "🔍 Filter by category",
    ["All", "BL_COMPARISON", "SI_REQUEST", "INVOICE_QUERY", "GENERAL", "SPAM"],
    index=0,
    format_func=lambda x: f"All ({len(classified)})" if x == "All" else f"{CATEGORY_LABELS[x][0]} ({sum(1 for _,c in classified if c == x)})"
)

filtered = classified if filter_cat == "All" else [(em, cat) for em, cat in classified if cat == filter_cat]

st.sidebar.divider()

# Email list
for i, (em, cat) in enumerate(filtered):
    label, css = CATEGORY_LABELS.get(cat, ("❓", "cat-gen"))
    icon = label.split(" ")[0]
    subj = em['subject'][:45] + "…" if len(em['subject']) > 45 else em['subject']
    if st.sidebar.button(
        f"{icon} **{em['email_id']}**\n{subj}",
        key=f"email_{i}",
        use_container_width=True,
    ):
        st.session_state.selected_email_idx = i

# ── Main: Landing Page ───────────────────────────────────────────────────────
if "selected_email_idx" not in st.session_state:
    st.markdown('<div class="team-badge">🐰 Team Snowbunnies</div>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Shipping Document Verifier</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Automated SI vs BL comparison pipeline — from email inbox to discrepancy report</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Dashboard metrics
    cats = [cat for _, cat in classified]
    total_bl = cats.count("BL_COMPARISON")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    metrics = [
        ("📬", len(emails), "Total Emails"),
        ("📄", total_bl, "BL Comparisons"),
        ("📋", cats.count("SI_REQUEST"), "SI Requests"),
        ("💰", cats.count("INVOICE_QUERY"), "Invoices"),
        ("📧", cats.count("GENERAL"), "General"),
        ("🚫", cats.count("SPAM"), "Spam"),
    ]
    for col, (icon, num, label) in zip([col1, col2, col3, col4, col5, col6], metrics):
        col.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5em;">{icon}</div>
            <div class="metric-number">{num}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")

    # Architecture
    st.markdown("### 🏗️ System Architecture")
    st.markdown('<div class="arch-box">', unsafe_allow_html=True)
    arch_cols = st.columns(5)
    steps = [
        ("1️⃣", "Email Inbox", "520 emails\nJSON + attachments"),
        ("2️⃣", "Classification", "5 categories\n`classification.py`"),
        ("3️⃣", "Document Parser", "PDF, DOCX, XLSX\n`doc_parser.py`"),
        ("4️⃣", "Field Extraction", "7 shipping fields\n`extraction.py`"),
        ("5️⃣", "Comparison", "OK / MISMATCH /\nNEEDS_REVIEW\n`comparison.py`"),
    ]
    for col, (num, title, desc) in zip(arch_cols, steps):
        col.markdown(f"**{num} {title}**")
        col.caption(desc)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")

    # Tech stack
    st.markdown("### 🛠️ Technology Stack")
    tc1, tc2, tc3 = st.columns(3)
    tc1.markdown("""
    **Core Engine**
    - Python 3 (regex + heuristics)
    - pypdf / docx2txt / openpyxl
    - Streamlit (web UI)
    """)
    tc2.markdown("""
    **AI / LLM Integration**
    - OpenAI GPT-4o-mini
    - Anthropic Claude Sonnet
    - Fallback-enhanced extraction
    """)
    tc3.markdown("""
    **Reliability**
    - Human-in-the-loop escalation
    - Edge case detection
    - 82% end-to-end accuracy
    """)

    st.markdown("---")
    st.info("👈 **Select an email from the sidebar** to begin verification.")

    st.markdown("")
    st.caption("Built with ❤️ by Team Snowbunnies — SDOC Hackathon 2026")

# ── Main: Email Detail View ──────────────────────────────────────────────────
else:
    idx = st.session_state.selected_email_idx
    email, category = filtered[idx]
    eid = email["email_id"]
    label, css = CATEGORY_LABELS.get(category, ("❓ Unknown", "cat-gen"))

    # Back button
    if st.button("← Back to Dashboard"):
        del st.session_state.selected_email_idx
        st.rerun()

    # Header
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown(f"## 📧 {eid}")
        st.markdown(f'<span class="category-badge {css}">{label}</span>', unsafe_allow_html=True)
    with header_col2:
        st.markdown(f"**From:** `{email['from']}`")
        st.markdown(f"**Attachments:** {len(email.get('attachments', []))}")

    st.markdown(f"**Subject:** {email['subject']}")
    st.markdown("---")

    with st.expander("📨 Email Body", expanded=False):
        st.text(email["body"])

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
            st.warning("This email is missing one or more required attachments (SI or BL). It has been escalated for human review.")
        else:
            si_bytes = inbox.read_bytes(si_path)
            bl_bytes = inbox.read_bytes(bl_path)
            si_text = doc_parser.extract_text_from_bytes(si_bytes, si_path)
            bl_text = doc_parser.extract_text_from_bytes(bl_bytes, bl_path)

            if not si_text.strip() or not bl_text.strip():
                st.markdown('<div class="status-review">⚠️ NEEDS REVIEW — Unreadable Document</div>', unsafe_allow_html=True)
                st.warning("One or more documents could not be read (possibly a scanned/image-only PDF). Escalated for human review.")
            else:
                # Source documents
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
                si_fields = extraction.extract_fields(si_text)
                bl_fields = extraction.extract_fields(bl_text)

                llm_used = False
                if use_llm and api_key:
                    with st.spinner(f"🤖 Running {llm_provider.upper()} extraction..."):
                        si_llm = llm_extraction.llm_extract_fields(si_text, provider=llm_provider)
                        bl_llm = llm_extraction.llm_extract_fields(bl_text, provider=llm_provider)

                    if si_llm and bl_llm:
                        llm_used = True
                        for field in FIELD_LABELS:
                            if si_fields.get(field) is None and si_llm.get(field) is not None:
                                si_fields[field] = si_llm[field]
                            if bl_fields.get(field) is None and bl_llm.get(field) is not None:
                                bl_fields[field] = bl_llm[field]

                # Compare
                status, has_defect, defect_fields, review_reason = comparison.compare_fields(si_fields, bl_fields)

                # Result banner
                st.markdown("### 🔍 Verification Result")
                if status == "OK":
                    st.markdown('<div class="status-ok">✅ OK — No Mismatch Detected</div>', unsafe_allow_html=True)
                elif status == "MISMATCH":
                    st.markdown(f'<div class="status-mismatch">❌ MISMATCH — {len(defect_fields)} field(s) differ</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="status-review">⚠️ NEEDS REVIEW — {review_reason}</div>', unsafe_allow_html=True)

                if llm_used:
                    provider_label = "OpenAI GPT-4o-mini" if llm_provider == "openai" else "Anthropic Claude Sonnet"
                    st.caption(f"🤖 Enhanced with {provider_label}")

                st.markdown("")

                # Comparison table
                st.markdown("### 📊 Field-by-Field Comparison")
                rows = []
                for field, flabel in FIELD_LABELS.items():
                    si_val = si_fields.get(field)
                    bl_val = bl_fields.get(field)
                    match = field not in defect_fields
                    rows.append({
                        "Field": flabel,
                        "SI Value": str(si_val) if si_val is not None else "—",
                        "BL Value": str(bl_val) if bl_val is not None else "—",
                        "Result": "✅ Match" if match else "❌ Mismatch",
                    })

                df = pd.DataFrame(rows)

                def highlight_row(row):
                    if row["Result"] == "❌ Mismatch":
                        return ["background-color: #f8d7da; font-weight: bold"] * len(row)
                    else:
                        return ["background-color: #d4edda"] * len(row)

                st.dataframe(
                    df.style.apply(highlight_row, axis=1),
                    use_container_width=True,
                    hide_index=True,
                    height=300,
                )

                # Discrepancy detail
                if defect_fields:
                    st.markdown("### ⚠️ Discrepancies Found")
                    for f in defect_fields:
                        flabel = FIELD_LABELS.get(f, f)
                        si_v = si_fields.get(f, "—")
                        bl_v = bl_fields.get(f, "—")
                        st.error(f"**{flabel}**  \nSI: `{si_v}`  \nBL: `{bl_v}`")
    else:
        st.info(f"This email was classified as **{label}**. No document comparison is required for this category.")
        st.markdown("Only **📄 BL Comparison** emails proceed to the extraction and verification stage.")

# ── Sidebar footer ───────────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.caption("🐰 Team Snowbunnies — SDOC Hackathon 2026")
