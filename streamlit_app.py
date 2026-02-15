# ------------------------------------------------------------
# WriteAble – UI-Only Prototype (Streamlit)
# This app shows a basic, accessible UI for your tool.
# It does NOT do real analysis yet – it's just the front-end
# so your teammates can see the layout and flow.
# ------------------------------------------------------------

import streamlit as st
from pathlib import Path

# ------------------------------------------------------------
# BASIC PAGE CONFIG (title, icon, layout)
# ------------------------------------------------------------
st.set_page_config(
    page_title="WriteAble – Accessible Document Helper",
    page_icon="📝",
    layout="wide",
)

# ------------------------------------------------------------
# SIMPLE, HIGH-CONTRAST THEME USING INLINE STYLES
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
</style>
"""
st.markdown(ACCESSIBLE_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------
# TRY TO LOAD LOGO IF IT EXISTS
# ------------------------------------------------------------
logo_path = Path("logo.png")
if logo_path.exists():
    st.sidebar.image(str(logo_path), use_container_width=True)
else:
    st.sidebar.markdown("### WriteAble")
    st.sidebar.markdown("_Logo will go here_")

# ------------------------------------------------------------
# SIDEBAR – NAVIGATION
# ------------------------------------------------------------
st.sidebar.markdown("## Navigation")
page = st.sidebar.selectbox(
    "Go to section:",
    [
        "Overview",
        "Upload & Input (UI only)",
        "Analysis Results (UI only)",
        "Help & Accessibility Info",
    ],
)

# ------------------------------------------------------------
# PAGE 1 – OVERVIEW
# ------------------------------------------------------------
if page == "Overview":
    st.title("WriteAble – Accessible Document Helper")

    st.markdown(
        """
        WriteAble is an accessibility-focused document analysis tool designed to help users
        create clearer, more inclusive content.

        This prototype shows the **user interface only**:
        - No real AI or analysis is running yet.
        - The goal is to preview layout, flow, and accessibility.
        """
    )

    st.markdown("### Goals")
    st.markdown(
        """
        - Help users produce accessible, inclusive documents  
        - Provide educational, plain-language feedback  
        - Support accessibility awareness in academic and professional settings  
        """
    )

    st.markdown("### What you can see in this prototype")
    st.markdown(
        """
        - A document upload and text input area  
        - Placeholder panels for Grammar, Readability, and Accessibility results  
        - A simple, high-contrast layout  
        - Keyboard-friendly controls  
        """
    )

# ------------------------------------------------------------
# PAGE 2 – UPLOAD & INPUT (UI ONLY)
# ------------------------------------------------------------
elif page == "Upload & Input (UI only)":
    st.title("Upload or Paste Your Document")

    st.markdown(
        """
        This page represents how users will provide content to WriteAble.
        For now, this is **UI only** – no real processing happens yet.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Upload a file")
        uploaded_file = st.file_uploader(
            "Choose a document (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            help="In the real app, the file would be analyzed for accessibility issues.",
        )

        if uploaded_file is not None:
            st.info(
                f"You selected: **{uploaded_file.name}**\n\n"
                "In the final version, this file would be scanned for grammar, readability, "
                "and accessibility issues."
            )

    with col2:
        st.subheader("Or paste your text")
        pasted_text = st.text_area(
            "Paste text here:",
            height=250,
            help="In the real app, this text would be analyzed.",
        )

        if pasted_text.strip():
            st.success(
                "Text received. In the final app, this would trigger an accessibility analysis."
            )

    st.markdown("---")
    st.markdown("### Actions (UI only)")
    analyze_clicked = st.button("Run Accessibility Check (placeholder)")

    if analyze_clicked:
        st.warning(
            "This is a prototype. In the full version, this button would run the analysis "
            "and populate the results page."
        )

# ------------------------------------------------------------
# PAGE 3 – ANALYSIS RESULTS (UI ONLY)
# ------------------------------------------------------------
elif page == "Analysis Results (UI only)":
    st.title("Analysis Results – Placeholder UI")

    st.markdown(
        """
        This page shows how results **will** be organized.  
        Right now, it uses sample/placeholder content.
        """
    )

    tab1, tab2, tab3 = st.tabs(["Grammar", "Readability", "Accessibility"])

    with tab1:
        st.subheader("Grammar Issues (Sample)")
        st.markdown(
            """
            - Missing comma in sentence 3  
            - Subject-verb agreement issue in sentence 7  
            - Spelling: "accesibilty" → "accessibility"  
            """
        )

    with tab2:
        st.subheader("Readability (Sample)")
        st.markdown(
            """
            - Average sentence length: 28 words (suggested: 15–20)  
            - Reading level: Grade 14 (suggested: Grade 8–10 for general audiences)  
            - Suggestion: Break long paragraphs into shorter chunks.  
            """
        )

    with tab3:
        st.subheader("Accessibility (Sample)")
        st.markdown(
            """
            - Missing headings for major sections  
            - Non-inclusive phrase: "the disabled" → consider "people with disabilities"  
            - Color contrast issue: light gray text on white background  
            - Suggestion: Use headings (H1, H2, H3) and clear section labels.  
            """
        )

    st.markdown("---")
    st.markdown("### Educational Explanations (Sample)")
    st.info(
        "Accessibility issues are explained in plain language here so users understand "
        "why each issue matters and how to fix it."
    )

# ------------------------------------------------------------
# PAGE 4 – HELP & ACCESSIBILITY INFO
# ------------------------------------------------------------
elif page == "Help & Accessibility Info":
    st.title("Help & Accessibility Information")

    st.markdown(
        """
        This section explains the purpose of WriteAble and how it supports accessibility.
        """
    )

    st.markdown("### Accessibility Principles")
    st.markdown(
        """
        - Use clear, simple language where possible  
        - Provide headings and structure for screen readers  
        - Ensure sufficient color contrast  
        - Support keyboard navigation  
        """
    )

    st.markdown("### Current Prototype Notes")
    st.markdown(
        """
        - This UI is built with Streamlit, which provides basic accessibility support.  
        - We added high-contrast buttons and clear headings.  
        - Future versions can include more detailed WCAG checks.  
        """
    )

    st.markdown("### Planned Features")
    st.markdown(
        """
        - Automated detection of WCAG-related issues in documents  
        - Plain-language explanations for each issue  
        - Suggestions and example rewrites  
        - Exportable accessibility reports  
        """
    )
