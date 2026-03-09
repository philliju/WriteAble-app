import streamlit as st
from pathlib import Path

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="WriteAble – Accessible Document Helper",
    page_icon="📝",
    layout="wide",
)

# ------------------------------------------------------------
# ACCESSIBLE CSS
# ------------------------------------------------------------
ACCESSIBLE_CSS = """
<style>
    body, .stMarkdown, .stText, .stButton button {
        font-size: 16px;
    }

    h1, h2, h3 {
        font-weight: 700;
    }

    .stButton button {
        background-color: #005A9E;
        color: white;
        border-radius: 4px;
        border: 2px solid #003B6F;
    }

    .stButton button:hover {
        background-color: #0078D4;
        border-color: #005A9E;
    }

    textarea, input {
        border: 1px solid #555 !important;
    }

    .issue-bubble {
        padding: 10px;
        background-color: #eef6ff;
        border-left: 4px solid #0078D4;
        border-radius: 4px;
        margin-bottom: 10px;
    }
</style>
"""
st.markdown(ACCESSIBLE_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------
# LOAD LOGO
# ------------------------------------------------------------
logo_path = Path("logo.png")
if logo_path.exists():
    st.sidebar.image(str(logo_path), use_container_width=True, caption="WriteAble logo")
else:
    st.sidebar.markdown("### WriteAble")
    st.sidebar.markdown("_Logo will go here_")

# ------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------
st.sidebar.markdown("## Navigation")
page = st.sidebar.selectbox(
    "Choose a section:",
    [
        "Overview",
        "Upload & Input",
        "Analysis Results",
        "Quick User Guide",
        "Full User Guide",
        "About Us",
    ],
)

# ------------------------------------------------------------
# PAGE: OVERVIEW
# ------------------------------------------------------------
if page == "Overview":
    st.title("WriteAble – Accessible Document Helper")

    st.markdown("""
        WriteAble helps people create clearer, more inclusive, and more accessible documents.

        This version is a **UI-only prototype**. No real AI or accessibility checks are running yet.
    """)

    st.markdown("### Project Goals")
    st.markdown("""
        - Allow users to upload or paste major document formats (up to 30 MB)  
        - Check documents against accessibility best practices (including WCAG-related issues)  
        - Provide plain-language explanations and suggested fixes  
    """)

    st.markdown("### What You Can Do in This Prototype")
    st.markdown("""
        - Upload or paste sample content  
        - View placeholder analysis results  
        - See how issues are listed, explained, and “AI fix” buttons are placed  
        - Open Quick User Guide, Full User Guide, and About Us pages  
    """)

# ------------------------------------------------------------
# PAGE: UPLOAD & INPUT
# ------------------------------------------------------------
elif page == "Upload & Input":
    st.title("Upload or Paste Your Document")

    st.markdown("""
        In the full version, you’ll be able to upload documents (PDF, DOCX, TXT, etc., up to 30 MB)
        or paste text, and WriteAble will analyze them for accessibility, readability, and grammar.
        For now, this is a **UI-only** page.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Upload a file")
        uploaded_file = st.file_uploader(
            "Choose a document (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            help="In the full app, this file will be analyzed for accessibility and related issues.",
        )

        if uploaded_file:
            st.info(f"You selected: **{uploaded_file.name}** (no analysis is performed yet).")

    with col2:
        st.subheader("Paste text")
        pasted_text = st.text_area(
            "Paste your document text here:",
            height=250,
            help="In the full app, this text will be analyzed.",
        )

        if pasted_text.strip():
            st.success("Text received. In the full app, this would trigger an analysis.")

    st.markdown("---")
    if st.button("Run Accessibility Check (placeholder)"):
        st.warning("This is a prototype. The analysis is not active yet.")

# ------------------------------------------------------------
# PAGE: ANALYSIS RESULTS
# ------------------------------------------------------------
elif page == "Analysis Results":
    st.title("Analysis Results (UI Only)")

    st.markdown("""
        This page shows how issues will be organized and displayed once analysis is active.
        The content below is sample data.
    """)

    # Sample issues
    issues = {
        "Grammar": [
            {"id": 1, "text": "Missing comma in sentence 3.", "explanation": "A comma is needed to separate clauses for clarity."},
            {"id": 2, "text": "Spelling: 'accesibilty' → 'accessibility'.", "explanation": "Correct spelling improves professionalism and readability."},
        ],
        "Readability": [
            {"id": 3, "text": "Sentence is too long (28 words).", "explanation": "Shorter sentences are easier to read and understand."},
        ],
        "Accessibility": [
            {"id": 4, "text": "Non-inclusive phrase: 'the disabled'.", "explanation": "Use people-first language, such as 'people with disabilities'."},
            {"id": 5, "text": "Missing headings for major sections.", "explanation": "Headings help screen reader users navigate the document."},
        ],
    }

    tab1, tab2, tab3 = st.tabs(["Grammar", "Readability", "Accessibility"])

    # --- GRAMMAR TAB ---
    with tab1:
        st.subheader("Grammar Issues (Sample)")
        for issue in issues["Grammar"]:
            with st.expander(issue["text"]):
                st.markdown(f"<div class='issue-bubble'>{issue['explanation']}</div>", unsafe_allow_html=True)
                st.button(f"AI Fix Issue #{issue['id']}", key=f"fix_{issue['id']}")

    # --- READABILITY TAB ---
    with tab2:
        st.subheader("Readability Issues (Sample)")
        for issue in issues["Readability"]:
            with st.expander(issue["text"]):
                st.markdown(f"<div class='issue-bubble'>{issue['explanation']}</div>", unsafe_allow_html=True)
                st.button(f"AI Fix Issue #{issue['id']}", key=f"fix_{issue['id']}")

    # --- ACCESSIBILITY TAB ---
    with tab3:
        st.subheader("Accessibility Issues (Sample)")
        for issue in issues["Accessibility"]:
            with st.expander(issue["text"]):
                st.markdown(f"<div class='issue-bubble'>{issue['explanation']}</div>", unsafe_allow_html=True)
                st.button(f"AI Fix Issue #{issue['id']}", key=f"fix_{issue['id']}")

# ------------------------------------------------------------
# PAGE: QUICK USER GUIDE
# ------------------------------------------------------------
elif page == "Quick User Guide":
    st.title("Quick User Guide")

    st.markdown("""
        **1. Go to “Upload & Input”**  
        Upload a document or paste your text.

        **2. Run the check**  
        In the full version, the “Run Accessibility Check” button will analyze your content.

        **3. Open “Analysis Results”**  
        View issues grouped under Grammar, Readability, and Accessibility.

        **4. Expand an issue**  
        Click an issue to see a short explanation in a bubble.

        **5. Use “AI Fix”**  
        In the full version, the AI Fix button will suggest a corrected version of the text.
    """)

# ------------------------------------------------------------
# PAGE: FULL USER GUIDE
# ------------------------------------------------------------
elif page == "Full User Guide":
    st.title("Full User Guide")

    st.markdown("""
        ### 1. Supported Documents
        - Major document formats (e.g., PDF, DOCX, TXT)  
        - File size up to 30 MB (planned)  

        ### 2. Analysis Types
        - Grammar and spelling  
        - Readability (sentence length, reading level, structure)  
        - Accessibility (headings, contrast issues in text descriptions, inclusive language, etc.)  

        ### 3. Understanding Issues
        - Each issue is listed with a short description  
        - Expanding an issue shows a plain-language explanation  
        - Issues are grouped by category for easier navigation  

        ### 4. Fixing Issues
        - “AI Fix” will propose a rewrite or correction (planned)  
        - Users can review and decide whether to apply the change  

        ### 5. Accessibility of WriteAble Itself
        - High-contrast buttons and text  
        - Clear headings and labels  
        - Keyboard-friendly controls (Streamlit + design choices)  
    """)

# ------------------------------------------------------------
# PAGE: ABOUT US
# ------------------------------------------------------------
elif page == "About Us":
    st.title("About WriteAble")

    st.markdown("""
        WriteAble is designed to help people create documents that are clearer, more inclusive,
        and more accessible for everyone.

        **Our focus:**
        - Make accessibility checks understandable, not intimidating  
        - Support learning, not just error-flagging  
        - Align with accessibility standards such as WCAG where possible  

        This prototype is an early UI-only version. The next steps are:
        - Implement real document analysis  
        - Add WCAG-related checks  
        - Provide suggested fixes powered by AI  
    """)

