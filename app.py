# ============================================================
# WriteAble – Main UI
# ============================================================
# This is the main Streamlit UI.
# It lets the user:
# - upload a file (future: connect to extractor.py)
# - paste text
# - see placeholder checker scores
# - see placeholder issue bubbles
# Other team members will plug in real analysis later.
# ============================================================

import streamlit as st

# --- Basic page setup ---#
st.set_page_config(
    page_title="WriteAble – Accessible Document Helper",
    page_icon="📝",
    layout="wide",
)

# --- Simple CSS for nicer look + bubbles ---
st.markdown(
    """
    <style>
        .issue-bubble {
            padding: 10px;
            background-color: #dceeff;
            border-left: 5px solid #005A9E;
            border-radius: 4px;
            margin-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- App title ---
st.title("WriteAble – Document Checker UI")

st.markdown(
    "This is the main UI. Other team members will plug in real scores and issues later."
)

# ============================================================
# --- Input Area (Upload or Paste) ---
# ============================================================
st.header("1. Document Input")

col_in1, col_in2 = st.columns(2)

with col_in1:
    # --- File upload (placeholder, not wired to extractor here) ---
    st.subheader("Upload a file")
    uploaded_file = st.file_uploader(
        "Choose a document (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        help="Future: connect this to extractor.py to pull text.",
    )

with col_in2:
    # --- Paste text area ---
    st.subheader("Paste text")
    pasted_text = st.text_area(
        "Paste your document text here:",
        height=200,
        help="Team can decide if they analyze this text directly.",
    )

# --- Student note: for now we just show what text we have ---
if uploaded_file or pasted_text.strip():
    st.success("Document content received (either file or pasted text).")
else:
    st.info("Upload a file or paste some text to see how the results UI looks.")


# ============================================================
# --- Checker Scores Section (Template) ---
# ============================================================
st.header("2. Checker Scores (Template)")

# --- Tabs for different checker scores ---
score_tab1, score_tab2, score_tab3 = st.tabs(
    ["Grammar Score", "Readability Score", "Accessibility Score"]
)

# --- Grammar Score tab ---
with score_tab1:
    st.subheader("Grammar Score")

    # --- Placeholder metric ---
    st.metric(
        label="Grammar Score (placeholder)",
        value="-- / 100",
        delta=None,
    )

    # --- Placeholder explanation ---
    st.text_area(
        "Grammar Notes (placeholder)",
        "This is where the grammar checker will explain the score.",
        height=120,
    )

# --- Readability Score tab ---
with score_tab2:
    st.subheader("Readability Score")

    st.metric(
        label="Readability Score (placeholder)",
        value="-- / 100",
        delta=None,
    )

    st.text_area(
        "Readability Notes (placeholder)",
        "This is where the readability checker will explain the score.",
        height=120,
    )

# --- Accessibility Score tab ---
with score_tab3:
    st.subheader("Accessibility Score")

    st.metric(
        label="Accessibility Score (placeholder)",
        value="-- / 100",
        delta=None,
    )

    st.text_area(
        "Accessibility Notes (placeholder)",
        "This is where the accessibility checker will explain the score.",
        height=120,
    )


# ============================================================
# --- Issue Details Section (Template) ---
# ============================================================
st.header("3. Issue Details (Template)")

# --- Tabs for issue lists ---
issue_tab1, issue_tab2, issue_tab3 = st.tabs(
    ["Grammar Issues", "Readability Issues", "Accessibility Issues"]
)

# --- Grammar Issues tab ---
with issue_tab1:
    st.subheader("Grammar Issues")

    st.info("Grammar issues will appear here once the grammar checker is built.")

    # --- Example issue bubble (placeholder) ---
    with st.expander("Example: Missing comma in sentence 3"):
        st.markdown(
            """
            <div class='issue-bubble'>
                This is where the explanation for the grammar issue will go.
                Team can also show suggested fix text here.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("AI Fix (placeholder)", key="grammar_fix_example")

# --- Readability Issues tab ---
with issue_tab2:
    st.subheader("Readability Issues")

    st.info("Readability issues will appear here once the readability checker is built.")

    with st.expander("Example: Sentence too long (28 words)"):
        st.markdown(
            """
            <div class='issue-bubble'>
                This is where the explanation for the readability issue will go.
                Team can show a shorter suggested version here.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("AI Fix (placeholder)", key="readability_fix_example")

# --- Accessibility Issues tab ---
with issue_tab3:
    st.subheader("Accessibility Issues")

    st.info(
        "Accessibility issues will appear here once the accessibility checker is built."
    )

    with st.expander("Example: Non-inclusive phrase used"):
        st.markdown(
            """
            <div class='issue-bubble'>
                This is where the explanation for the accessibility issue will go.
                Team can show a more inclusive alternative here.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("AI Fix (placeholder)", key="accessibility_fix_example")


# ============================================================
# --- Student Notes for Team ---
# ============================================================
st.header("4. Dev Notes (for the team)")

st.markdown(
    """
- The **scores section** is just a template.  
  Each checker team can replace `"-- / 100"` and the notes with real values.

- The **issue tabs** are also templates.  
  Teams can loop over real issues and create one expander per issue.

- The **input section** is not wired to any backend yet.  
  Later, you can:
  - send `pasted_text` to your analysis
  - or send extracted text from `extractor.py`
"""
)
