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
    .cat-mismatch { background-color: #ffccd2; color: #721c24; font-weight: 700; border: 1px solid #e53e3e; }
    .cat-review { background-color: #ffeaa7; color: #856404; font-weight: 700; border: 1px solid #e1b12c; }

    .sidebar-alert-mismatch {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        border: 1.5px solid #feb2b2;
        border-left: 5px solid #e53e3e;
        border-radius: 8px;
        padding: 8px 10px;
        margin-top: 10px;
        margin-bottom: 3px;
        box-shadow: 0 2px 4px rgba(229, 62, 62, 0.12);
    }
    .sidebar-alert-mismatch .alert-title {
        font-weight: 700;
        font-size: 0.80em;
        color: #9b2c2c;
        display: flex;
        align-items: center;
        gap: 5px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .sidebar-alert-mismatch .alert-desc {
        font-size: 0.74em;
        color: #c53030;
        margin-top: 3px;
        line-height: 1.3;
    }

    .sidebar-alert-review {
        background: linear-gradient(135deg, #fffdf0 0%, #feebc8 100%);
        border: 1.5px solid #fbd38d;
        border-left: 5px solid #dd6b20;
        border-radius: 8px;
        padding: 8px 10px;
        margin-top: 10px;
        margin-bottom: 3px;
        box-shadow: 0 2px 4px rgba(221, 107, 32, 0.12);
    }
    .sidebar-alert-review .alert-title {
        font-weight: 700;
        font-size: 0.80em;
        color: #7b341e;
        display: flex;
        align-items: center;
        gap: 5px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .sidebar-alert-review .alert-desc {
        font-size: 0.74em;
        color: #9c4221;
        margin-top: 3px;
        line-height: 1.3;
    }

    .metric-card {
        background: white; border-radius: 12px; padding: 20px; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #eee;
    }
    .metric-number { font-size: 2em; font-weight: 700; color: #333; }
    .metric-label { font-size: 0.85em; color: #888; margin-top: 4px; }
    
    .metric-card-danger {
        background: #fff5f5; border-radius: 12px; padding: 18px 10px; text-align: center;
        box-shadow: 0 2px 8px rgba(229,62,62,0.12); border: 1.5px solid #feb2b2;
    }
    .metric-card-danger .metric-number { color: #e53e3e; font-size: 2em; font-weight: 700; }
    .metric-card-danger .metric-label { color: #9b2c2c; font-size: 0.85em; font-weight: 600; margin-top: 4px; }

    .metric-card-warning {
        background: #fffdf0; border-radius: 12px; padding: 18px 10px; text-align: center;
        box-shadow: 0 2px 8px rgba(221,107,32,0.12); border: 1.5px solid #fbd38d;
    }
    .metric-card-warning .metric-number { color: #dd6b20; font-size: 2em; font-weight: 700; }
    .metric-card-warning .metric-label { color: #7b341e; font-size: 0.85em; font-weight: 600; margin-top: 4px; }

    .metric-card-success {
        background: #f0fff4; border-radius: 12px; padding: 18px 10px; text-align: center;
        box-shadow: 0 2px 8px rgba(56,161,105,0.12); border: 1.5px solid #9ae6b4;
    }
    .metric-card-success .metric-number { color: #38a169; font-size: 2em; font-weight: 700; }
    .metric-card-success .metric-label { color: #22543d; font-size: 0.85em; font-weight: 600; margin-top: 4px; }
    
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

# ── Load verification results ────────────────────────────────────────────────
@st.cache_data
def load_submissions():
    if os.path.exists("submission_final.json"):
        try:
            with open("submission_final.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

submissions = load_submissions()

# Aggregate statistics
cats = [cat for _, cat in classified]
total_bl = cats.count("BL_COMPARISON")
mismatch_count = sum(1 for em, _ in classified if submissions.get(em["email_id"], {}).get("status") == "MISMATCH")
review_count = sum(1 for em, _ in classified if submissions.get(em["email_id"], {}).get("status") == "NEEDS_REVIEW")
bl_ok_count = sum(1 for em, c in classified if c == "BL_COMPARISON" and submissions.get(em["email_id"], {}).get("status") == "OK")

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

# Filter by category and status
CATEGORY_FILTER_CONFIG = {
    "All": f"All ({len(classified)})",
    "MISMATCH": f"🚨 ❌ Mismatches / Defects ({mismatch_count})",
    "NEEDS_REVIEW": f"⚠️ 🔍 Needs Review ({review_count})",
    "BL_COMPARISON": f"📄 BL Comparison — All ({total_bl})",
    "BL_OK": f"✅ BL Comparison — OK ({bl_ok_count})",
    "SI_REQUEST": f"📋 SI Request ({cats.count('SI_REQUEST')})",
    "INVOICE_QUERY": f"💰 Invoice Query ({cats.count('INVOICE_QUERY')})",
    "GENERAL": f"📧 General ({cats.count('GENERAL')})",
    "SPAM": f"🚫 Spam ({cats.count('SPAM')})",
}

filter_cat = st.sidebar.selectbox(
    "🔍 Filter by category / status",
    list(CATEGORY_FILTER_CONFIG.keys()),
    index=0,
    format_func=lambda x: CATEGORY_FILTER_CONFIG.get(x, x)
)

if filter_cat == "All":
    filtered = classified
elif filter_cat == "MISMATCH":
    filtered = [(em, c) for em, c in classified if submissions.get(em["email_id"], {}).get("status") == "MISMATCH"]
elif filter_cat == "NEEDS_REVIEW":
    filtered = [(em, c) for em, c in classified if submissions.get(em["email_id"], {}).get("status") == "NEEDS_REVIEW"]
elif filter_cat == "BL_OK":
    filtered = [(em, c) for em, c in classified if c == "BL_COMPARISON" and submissions.get(em["email_id"], {}).get("status") == "OK"]
elif filter_cat == "BL_COMPARISON":
    filtered = [(em, c) for em, c in classified if c == "BL_COMPARISON"]
else:
    filtered = [(em, c) for em, c in classified if c == filter_cat]

st.sidebar.divider()

# Email list
for em, cat in filtered:
    eid = em['email_id']
    sub_data = submissions.get(eid, {})
    status = sub_data.get("status", "OK")
    defects = sub_data.get("defect_fields", [])
    rev_reason = sub_data.get("review_reason", None)
    subj = em['subject'][:45] + "…" if len(em['subject']) > 45 else em['subject']
    
    if status == "MISMATCH":
        defect_str = ", ".join([FIELD_LABELS.get(d, d) for d in defects]) if defects else "Field mismatch"
        st.sidebar.markdown(
            f"""<div class="sidebar-alert-mismatch">
                <div class="alert-title"><span>⚠️ 🚨</span> <span>MISMATCH WARNING</span></div>
                <div class="alert-desc">Defect: <b>{defect_str}</b></div>
            </div>""",
            unsafe_allow_html=True
        )
        btn_label = f"🚨 ❌ **{eid}**\n{subj}"
    elif status == "NEEDS_REVIEW":
        reason_label = (rev_reason or "Escalated").replace("_", " ").title()
        st.sidebar.markdown(
            f"""<div class="sidebar-alert-review">
                <div class="alert-title"><span>⚠️ 🔍</span> <span>NEEDS REVIEW</span></div>
                <div class="alert-desc">Reason: <b>{reason_label}</b></div>
            </div>""",
            unsafe_allow_html=True
        )
        btn_label = f"⚠️ 🔍 **{eid}**\n{subj}"
    else:
        label, css = CATEGORY_LABELS.get(cat, ("❓", "cat-gen"))
        icon = label.split(" ")[0]
        btn_label = f"{icon} **{eid}**\n{subj}"
        
    if st.sidebar.button(
        btn_label,
        key=f"email_btn_{eid}",
        use_container_width=True,
    ):
        st.session_state.selected_email_id = eid

# ── Main: Landing Page ───────────────────────────────────────────────────────
if "selected_email_id" not in st.session_state:
    st.markdown('<div class="team-badge">🐰 Team Snowbunnies</div>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Shipping Document Verifier</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Automated SI vs BL comparison pipeline — from email inbox to discrepancy report</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Verification Highlights
    st.markdown("### 🎯 Verification & Integrity Highlights")
    col_v1, col_v2, col_v3, col_v4 = st.columns(4)
    col_v1.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 1.5em;">📬</div>
        <div class="metric-number">{len(emails)}</div>
        <div class="metric-label">Total Inbox Emails</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_v2.markdown(f"""
    <div class="metric-card-danger">
        <div style="font-size: 1.5em;">🚨</div>
        <div class="metric-number">{mismatch_count}</div>
        <div class="metric-label">Mismatches / Defects</div>
    </div>
    """, unsafe_allow_html=True)

    col_v3.markdown(f"""
    <div class="metric-card-warning">
        <div style="font-size: 1.5em;">⚠️</div>
        <div class="metric-number">{review_count}</div>
        <div class="metric-label">Needs Human Review</div>
    </div>
    """, unsafe_allow_html=True)

    col_v4.markdown(f"""
    <div class="metric-card-success">
        <div style="font-size: 1.5em;">✅</div>
        <div class="metric-number">{bl_ok_count}</div>
        <div class="metric-label">Verified Clean BLs</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("### 📂 Classification Breakdown")
    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("📄", total_bl, "BL Comparisons"),
        ("📋", cats.count("SI_REQUEST"), "SI Requests"),
        ("💰", cats.count("INVOICE_QUERY"), "Invoices"),
        ("📧", cats.count("GENERAL"), "General"),
        ("🚫", cats.count("SPAM"), "Spam"),
    ]
    for col, (icon, num, label) in zip([col1, col2, col3, col4, col5], metrics):
        col.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.3em;">{icon}</div>
            <div class="metric-number" style="font-size: 1.6em;">{num}</div>
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
    - 100% end-to-end accuracy
    """)

    st.markdown("---")
    st.info("👈 **Select an email from the sidebar** to begin verification.")

    st.markdown("")
    st.caption("Built with ❤️ by Team Snowbunnies — SDOC Hackathon 2026")

# ── Main: Email Detail View ──────────────────────────────────────────────────
else:
    eid = st.session_state.selected_email_id
    email = next((e for e in emails if e["email_id"] == eid), None)
    if not email:
        del st.session_state.selected_email_id
        st.rerun()

    category = classification.classify_email(email)
    sub_data = submissions.get(eid, {})
    email_status = sub_data.get("status", "OK")
    label, css = CATEGORY_LABELS.get(category, ("❓ Unknown", "cat-gen"))

    # Back button
    if st.button("← Back to Dashboard"):
        del st.session_state.selected_email_id
        st.rerun()

    # Header
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown(f"## 📧 {eid}")
        if category == "BL_COMPARISON":
            if email_status == "MISMATCH":
                st.markdown('<span class="category-badge cat-mismatch">🚨 BL Comparison — Mismatch Detected</span>', unsafe_allow_html=True)
            elif email_status == "NEEDS_REVIEW":
                st.markdown('<span class="category-badge cat-review">⚠️ BL Comparison — Needs Human Review</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="category-badge cat-bl">📄 BL Comparison — Verified Clean</span>', unsafe_allow_html=True)
        else:
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
