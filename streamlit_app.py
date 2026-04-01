"""
WriteAble – Accessible Document Helper
Real accessibility checking + interactive AI-powered fix report.
"""
import io
import re
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

import streamlit as st
import textstat

# ── Optional deps ─────────────────────────────────────────────────────────────
try:
    from spellchecker import SpellChecker
    _spell = SpellChecker()
    HAS_SPELL = True
except Exception:
    HAS_SPELL = False

try:
    import anthropic as _anthropic
    HAS_ANTHROPIC = True
except Exception:
    HAS_ANTHROPIC = False

try:
    import docx as _docx
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

try:
    import pdfplumber as _pdfplumber
    HAS_PDF = True
except Exception:
    HAS_PDF = False


# ════════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG & CSS
# ════════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="WriteAble – Accessible Document Helper",
                   page_icon="📝", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] { font-size: 16px; }
h1, h2, h3 { font-weight: 700; }

.stButton > button {
    background: #005A9E; color: white;
    border: 2px solid #003B6F; border-radius: 4px;
    font-size: 14px;
}
.stButton > button:hover { background: #0078D4; border-color: #005A9E; }

/* Issue row */
.issue-row {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: 6px; margin: 5px 0;
    border-left: 5px solid #ccc; background: #fafafa;
}
.issue-row.error   { border-color: #C62828; background: #fff5f5; }
.issue-row.warning { border-color: #E65100; background: #fffbf0; }
.issue-row.info    { border-color: #1565C0; background: #f0f6ff; }

/* Badges */
.badge {
    padding: 2px 9px; border-radius: 12px;
    font-size: 11px; font-weight: 800;
    color: white; white-space: nowrap; display: inline-block;
}
.b-error   { background: #C62828; }
.b-warning { background: #E65100; }
.b-info    { background: #1565C0; }
.b-cat     { background: #444; font-size: 11px; }

/* Code snippet */
.snippet {
    font-family: monospace; font-size: 13px;
    background: #eeeeee; color: #000000 !important; padding: 6px 10px;
    border-radius: 4px; margin: 8px 0; word-break: break-word;
    white-space: pre-wrap;
}

/* AI fix box */
.fix-box {
    background: #e8f5e9; border-left: 4px solid #2E7D32;
    padding: 10px 14px; border-radius: 4px; margin-top: 8px;
    font-size: 14px;
}

/* Summary stat boxes */
.stat-box {
    text-align: center; padding: 18px 10px;
    border-radius: 10px; font-weight: 700; line-height: 1.4;
}
.stat-num { font-size: 32px; display: block; }

textarea, input[type="text"] { border: 1px solid #555 !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# DATA MODEL
# ════════════════════════════════════════════════════════════════════════════════
@dataclass
class Issue:
    id: int
    category: str   # Grammar | Readability | Accessibility
    severity: str   # error | warning | info
    title: str
    explanation: str
    snippet: str
    suggestion: str = ""   # quick pre-computed replacement (may be empty)


# ════════════════════════════════════════════════════════════════════════════════
# CHECKER ENGINE
# ════════════════════════════════════════════════════════════════════════════════

_INCLUSIVE_RULES = [
    (r"\bthe\s+disabled\b",               "people with disabilities"),
    (r"\bthe\s+blind\b",                  "people who are blind"),
    (r"\bthe\s+deaf\b",                   "people who are Deaf or hard of hearing"),
    (r"\bwheelchair[\s\-]?bound\b",       "wheelchair user"),
    (r"\bconfined\s+to\s+a\s+wheelchair\b","wheelchair user"),
    (r"\bsuffers?\s+from\b",              "has / lives with"),
    (r"\bmentally\s+ill\b",               "person with a mental health condition"),
    (r"\bcrippled?\b",                    "person with a disability"),
    (r"\bmankind\b",                      "humanity or humankind"),
    (r"\bmanpower\b",                     "workforce or staffing"),
    (r"\bblacklist\b",                    "blocklist or denylist"),
    (r"\bwhitelist\b",                    "allowlist"),
    (r"\bhe\s+or\s+she\b",               "they"),
    (r"\bhis\s+or\s+her\b",              "their"),
    (r"\bcrazy\b",                        "unexpected / surprising"),
    (r"\binsane\b",                       "extreme / unreasonable"),
    (r"\bdumb\b",                         "confusing or unclear"),
    (r"\bstupid\b",                       "unclear / poorly designed"),
    (r"\blow[\s\-]functioning\b",         "person who needs significant support"),
    (r"\bhigh[\s\-]functioning\b",        "person who needs minimal support"),
    (r"\bnormal\s+people\b",             "people without disabilities"),
]

_PASSIVE_RE = re.compile(
    r'\b(?:am|is|are|was|were|be|been|being)\s+\w+(?:ed|en)\b',
    re.IGNORECASE
)
_ACRONYM_RE = re.compile(r'\b([A-Z]{2,7})\b')


def _word_count(text: str) -> int:
    return len(re.findall(r'\b[a-zA-Z]+\b', text))


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def run_checks(text: str) -> List[Issue]:
    issues: List[Issue] = []
    _id = 0

    def add(cat, sev, title, expl, snip, sug=""):
        nonlocal _id
        _id += 1
        issues.append(Issue(_id, cat, sev, title, expl, snip, sug))

    all_words = re.findall(r'\b[a-zA-Z]+\b', text)
    sentences  = _sentences(text)
    total_words = _word_count(text)

    # ── 1. Spelling ──────────────────────────────────────────────────────────
    if HAS_SPELL:
        # Only check lowercase, length > 3 to avoid proper nouns & abbreviations
        check_words = [w for w in all_words if not w[0].isupper() and len(w) > 3]
        misspelled  = _spell.unknown(check_words)
        for word in sorted(misspelled)[:12]:
            correction = _spell.correction(word)
            if correction and correction != word:
                add("Grammar", "error",
                    f"Possible misspelling: '{word}'",
                    f"Did you mean '{correction}'? Correct spelling improves professionalism and clarity.",
                    word, correction)

    # ── 2. Repeated consecutive words ────────────────────────────────────────
    for m in re.finditer(r'\b(\w+)\s+\1\b', text, re.IGNORECASE):
        add("Grammar", "error",
            f"Repeated word: '{m.group()}'",
            "The same word appears twice in a row — this is likely a typo.",
            m.group())

    # ── 3. Double / extra spaces ──────────────────────────────────────────────
    if re.search(r'  +', text):
        add("Grammar", "info",
            "Multiple consecutive spaces found",
            "Extra spaces can break formatting and confuse screen readers. Use a single space between words.",
            "Multiple consecutive spaces detected in the document")

    # ── 4. Per-sentence length ────────────────────────────────────────────────
    for s in sentences:
        wc   = _word_count(s)
        snip = (s[:110] + "…") if len(s) > 110 else s
        if wc > 35:
            add("Readability", "error",
                f"Very long sentence ({wc} words)",
                "Sentences over 35 words are very hard to follow. Try splitting into 2–3 shorter sentences.",
                snip)
        elif wc > 25:
            add("Readability", "warning",
                f"Long sentence ({wc} words)",
                "Aim for sentences under 25 words. Shorter sentences are easier for all readers, including those using screen readers.",
                snip)

    # ── 5. Flesch Reading Ease & Grade ───────────────────────────────────────
    if total_words >= 30:
        fre  = textstat.flesch_reading_ease(text)
        fkgl = textstat.flesch_kincaid_grade(text)

        if fre < 30:
            add("Readability", "error",
                f"Very difficult to read (Flesch score {fre:.1f}/100)",
                "Below 30 is college-level and above. For general audiences, aim for 60+. "
                "Try using shorter sentences and simpler words.",
                f"Flesch Reading Ease score: {fre:.1f} / 100")
        elif fre < 50:
            add("Readability", "warning",
                f"Difficult to read (Flesch score {fre:.1f}/100)",
                "A score of 30–50 is considered 'difficult'. Simplify vocabulary and shorten sentences.",
                f"Flesch Reading Ease score: {fre:.1f} / 100")

        if fkgl > 12:
            add("Readability", "warning",
                f"College reading level detected (grade {fkgl:.1f})",
                "For broad audiences—including people with cognitive disabilities—target grade 8 or below.",
                f"Flesch-Kincaid Grade Level: {fkgl:.1f}")

    # ── 6. Passive voice overuse ──────────────────────────────────────────────
    passive_hits = _PASSIVE_RE.findall(text)
    if len(passive_hits) > 4:
        examples = "; ".join(passive_hits[:3])
        add("Readability", "info",
            f"Heavy use of passive voice ({len(passive_hits)} instances)",
            "Active voice is clearer and more direct. E.g., 'Errors were found by the team' → 'The team found errors'.",
            f"Examples: {examples}")

    # ── 7. Inclusive language ─────────────────────────────────────────────────
    for pattern, suggestion in _INCLUSIVE_RULES:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            s0  = max(0, m.start() - 50)
            e0  = min(len(text), m.end() + 50)
            ctx = ("…" if s0 > 0 else "") + text[s0:e0].strip() + ("…" if e0 < len(text) else "")
            add("Accessibility", "warning",
                f"Non-inclusive language: '{m.group()}'",
                f"Consider '{suggestion}' instead. Inclusive language ensures all readers feel respected and represented.",
                ctx, suggestion)

    # ── 8. Excessive ALL CAPS ─────────────────────────────────────────────────
    defined_acr = set(re.findall(r'\(([A-Z]{2,7})\)', text))
    all_caps    = re.findall(r'\b[A-Z]{4,}\b', text)
    # Exclude defined acronyms
    caps_non_acr = [w for w in all_caps if w not in defined_acr]
    unique_caps  = list(dict.fromkeys(caps_non_acr))
    if len(unique_caps) > 3:
        add("Accessibility", "info",
            f"Excessive ALL CAPS text ({len(unique_caps)} instances)",
            "All-caps text is harder to read and can feel aggressive. "
            "Screen readers may read each letter individually. Use it sparingly.",
            "Examples: " + ", ".join(unique_caps[:7]))

    # ── 9. Undefined acronyms ─────────────────────────────────────────────────
    all_acr   = list(dict.fromkeys(_ACRONYM_RE.findall(text)))
    undefined = [a for a in all_acr if a not in defined_acr]
    # Filter very common ones people wouldn't need to define
    skip_acr  = {"I", "A", "OK", "US", "UK", "UN", "AM", "PM", "AI", "IT"}
    undefined = [a for a in undefined if a not in skip_acr]
    if undefined:
        add("Accessibility", "info",
            f"Possibly undefined acronyms: {', '.join(undefined[:6])}",
            "Always spell out acronyms on first use, e.g. 'Web Content Accessibility Guidelines (WCAG)'. "
            "Screen reader users and non-specialist readers may not recognise them.",
            ", ".join(undefined[:8]))

    # ── 10. Missing headings in long document ─────────────────────────────────
    has_md_headings = bool(re.search(r'^#{1,6}\s+\w+', text, re.MULTILINE))
    # Also detect plain-text heading style (line of text alone on a line, all caps or Title Case)
    has_plaintext_headings = bool(re.search(r'^[A-Z][A-Za-z ]{3,50}$', text, re.MULTILINE))
    if total_words > 200 and not has_md_headings and not has_plaintext_headings:
        add("Accessibility", "warning",
            "No headings detected in a long document",
            "Documents over 200 words should use headings so screen reader users can navigate. "
            "In Markdown, use # Heading, ## Sub-heading, etc.",
            f"Document has {total_words} words with no headings detected")

    # ── 11. Very short paragraphs / wall of text ──────────────────────────────
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if len(paragraphs) == 1 and total_words > 150:
        add("Readability", "info",
            "Text appears as a single block (no paragraph breaks)",
            "Breaking text into shorter paragraphs (every 3–5 sentences) improves readability and accessibility.",
            f"Entire document is one paragraph ({total_words} words)")

    # ── 12. Ambiguous link text (URLs used as link labels) ────────────────────
    bare_urls = re.findall(r'https?://[^\s]+', text)
    if bare_urls:
        add("Accessibility", "warning",
            f"Bare URL(s) used as link text ({len(bare_urls)} found)",
            "Screen readers read URLs aloud character by character. Replace bare URLs with descriptive link text like "
            "[Read our accessibility guide](https://…) in Markdown.",
            bare_urls[0][:80])

    return issues


# ════════════════════════════════════════════════════════════════════════════════
# AI FIX
# ════════════════════════════════════════════════════════════════════════════════
def get_ai_fix(issue: Issue, full_text: str, api_key: str) -> str:
    client = _anthropic.Anthropic(api_key=api_key)
    resp   = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=350,
        messages=[{"role": "user", "content": (
            "You are an expert in document accessibility, plain language, and inclusive writing.\n\n"
            f"Issue category: {issue.category}\n"
            f"Issue: {issue.title}\n"
            f"Explanation: {issue.explanation}\n"
            f"Problematic text: {issue.snippet}\n\n"
            "Provide a specific, concise fix.\n"
            "- If it's a word or phrase problem → give only the corrected wording.\n"
            "- If it's a sentence that's too long → rewrite it as 2 shorter sentences.\n"
            "- If it's structural (e.g. 'add headings') → give a concrete 1-sentence action.\n"
            "No preamble. No explanation. Just the fix itself."
        )}]
    )
    return resp.content[0].text.strip()


# ════════════════════════════════════════════════════════════════════════════════
# FILE EXTRACTION
# ════════════════════════════════════════════════════════════════════════════════
def extract_text(f) -> Optional[str]:
    name = f.name.lower()
    try:
        if name.endswith(".txt"):
            return f.read().decode("utf-8", errors="replace")
        if name.endswith(".docx"):
            if HAS_DOCX:
                doc = _docx.Document(io.BytesIO(f.read()))
                return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
            else:
                st.warning("python-docx not installed. Install it to support .docx files.")
                return None
        if name.endswith(".pdf"):
            if HAS_PDF:
                with _pdfplumber.open(io.BytesIO(f.read())) as pdf:
                    return "\n\n".join(pg.extract_text() or "" for pg in pdf.pages)
            else:
                st.warning("pdfplumber not installed. Install it to support .pdf files.")
                return None
        # Fallback
        return f.read().decode("utf-8", errors="replace")
    except Exception as e:
        st.error(f"Could not read file: {e}")
        return None


# ════════════════════════════════════════════════════════════════════════════════
# REPORT RENDERING
# ════════════════════════════════════════════════════════════════════════════════
_SEV_COLOR = {"error": "#C62828",  "warning": "#E65100", "info": "#1565C0"}
_BG_COLOR  = {"error": "#fff5f5",  "warning": "#fffbf0", "info": "#f0f6ff"}
_CAT_ICON  = {"Grammar": "📝",     "Readability": "📖",  "Accessibility": "♿"}


def render_issue(issue: Issue, full_text: str, api_key: Optional[str], tab_prefix: str = ""):
    # wk  = widget key  (must be unique across ALL tabs rendered simultaneously)
    # stk = state key   (shared across tabs so accept/dismiss is consistent everywhere)
    wk  = f"{tab_prefix}{issue.id}"
    stk = str(issue.id)

    # Skip if dismissed
    if st.session_state.get(f"dis_{stk}"):
        return

    # ── Header row ────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="issue-row {issue.severity}">'
        f'<span class="badge b-{issue.severity}">{issue.severity.upper()}</span>'
        f'<span class="badge b-cat">{_CAT_ICON.get(issue.category,"")} {issue.category}</span>'
        f'<span style="font-weight:600">{issue.title}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    with st.expander("Details & Fix", expanded=False):
        st.markdown(f"**What's wrong:** {issue.explanation}")
        st.markdown(
            f'<div class="snippet">{issue.snippet}</div>',
            unsafe_allow_html=True
        )

        if issue.suggestion:
            st.info(f"💡 Quick suggestion: **{issue.suggestion}**")

        col_fix, col_dis = st.columns([3, 1])

        with col_fix:
            accepted = st.session_state.get(f"acc_{stk}")
            ai_fix   = st.session_state.get(f"fix_{stk}")

            if accepted:
                st.success(f"✅ Fix accepted: _{accepted}_")
            elif ai_fix:
                st.markdown(
                    f'<div class="fix-box">🤖 <b>AI suggestion:</b><br><br>{ai_fix}</div>',
                    unsafe_allow_html=True
                )
                if st.button("✅ Accept this fix", key=f"acc_btn_{wk}"):
                    st.session_state[f"acc_{stk}"] = ai_fix
                    st.rerun()
            else:
                if api_key and HAS_ANTHROPIC:
                    if st.button("🤖 Get AI Fix", key=f"ai_btn_{wk}"):
                        with st.spinner("Generating AI fix…"):
                            fix = get_ai_fix(issue, full_text, api_key)
                            st.session_state[f"fix_{stk}"] = fix
                            st.rerun()
                elif not HAS_ANTHROPIC:
                    st.caption("⚠ Install the `anthropic` package to enable AI fixes.")
                else:
                    st.caption("🔑 Add your Anthropic API key in the sidebar to enable AI fixes.")

        with col_dis:
            if not accepted:
                if st.button("✖ Dismiss", key=f"dis_btn_{wk}"):
                    st.session_state[f"dis_{stk}"] = True
                    st.rerun()


def render_report(issues: List[Issue], text: str, api_key: Optional[str]):
    """Full interactive report with summary, filters, tabs, and export."""

    if not issues:
        st.success("🎉 No accessibility issues found! Your document looks great.")
        return

    # ── Summary statistics ────────────────────────────────────────────────────
    errors   = sum(1 for i in issues if i.severity == "error")
    warnings = sum(1 for i in issues if i.severity == "warning")
    infos    = sum(1 for i in issues if i.severity == "info")
    active   = sum(1 for i in issues if not st.session_state.get(f"dis_{i.id}"))
    accepted = sum(1 for i in issues if st.session_state.get(f"acc_{i.id}"))

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(
        f'<div class="stat-box" style="background:#fff5f5;color:#C62828">'
        f'<span class="stat-num">{errors}</span>Errors</div>', unsafe_allow_html=True)
    c2.markdown(
        f'<div class="stat-box" style="background:#fffbf0;color:#E65100">'
        f'<span class="stat-num">{warnings}</span>Warnings</div>', unsafe_allow_html=True)
    c3.markdown(
        f'<div class="stat-box" style="background:#f0f6ff;color:#1565C0">'
        f'<span class="stat-num">{infos}</span>Suggestions</div>', unsafe_allow_html=True)
    c4.markdown(
        f'<div class="stat-box" style="background:#f5fff5;color:#2E7D32">'
        f'<span class="stat-num">{accepted}</span>Fixes Accepted</div>', unsafe_allow_html=True)
    c5.markdown(
        f'<div class="stat-box" style="background:#f5f5f5;color:#333">'
        f'<span class="stat-num">{active}</span>Remaining</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Filters ───────────────────────────────────────────────────────────────
    with st.expander("🔍 Filter issues", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            show_cats = st.multiselect(
                "Category",
                ["Grammar", "Readability", "Accessibility"],
                default=["Grammar", "Readability", "Accessibility"],
                key="filter_cat"
            )
        with fc2:
            show_sevs = st.multiselect(
                "Severity",
                ["error", "warning", "info"],
                default=["error", "warning", "info"],
                key="filter_sev"
            )
        with fc3:
            search_q = st.text_input("Search", placeholder="Filter by keyword…", key="filter_q")

    def apply_filters(issue_list):
        return [
            i for i in issue_list
            if i.category in show_cats
            and i.severity in show_sevs
            and not st.session_state.get(f"dis_{i.id}")
            and (not search_q
                 or search_q.lower() in i.title.lower()
                 or search_q.lower() in i.explanation.lower()
                 or search_q.lower() in i.snippet.lower())
        ]

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_grammar, tab_read, tab_access, tab_all = st.tabs(
        ["📝 Grammar", "📖 Readability", "♿ Accessibility", "🔍 All Issues"]
    )

    with tab_grammar:
        filtered = apply_filters([i for i in issues if i.category == "Grammar"])
        st.markdown(f"**{len(filtered)} issue(s)**")
        if not filtered:
            st.info("No Grammar issues match the current filters.")
        for issue in filtered:
            render_issue(issue, text, api_key, tab_prefix="g_")

    with tab_read:
        filtered = apply_filters([i for i in issues if i.category == "Readability"])
        st.markdown(f"**{len(filtered)} issue(s)**")
        if not filtered:
            st.info("No Readability issues match the current filters.")
        for issue in filtered:
            render_issue(issue, text, api_key, tab_prefix="r_")

    with tab_access:
        filtered = apply_filters([i for i in issues if i.category == "Accessibility"])
        st.markdown(f"**{len(filtered)} issue(s)**")
        if not filtered:
            st.info("No Accessibility issues match the current filters.")
        for issue in filtered:
            render_issue(issue, text, api_key, tab_prefix="a_")

    with tab_all:
        filtered = apply_filters(issues)
        st.markdown(f"**{len(filtered)} issue(s) shown**")
        if not filtered:
            st.info("No issues match the current filters.")
        for issue in filtered:
            render_issue(issue, text, api_key, tab_prefix="all_")

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📥 Export")
    ec1, ec2 = st.columns(2)

    with ec1:
        st.download_button(
            "⬇ Download original text (.txt)",
            data=text.encode("utf-8"),
            file_name="document_original.txt",
            mime="text/plain"
        )

    with ec2:
        # Build a fixes summary report
        accepted_issues = [(i, st.session_state.get(f"acc_{i.id}"))
                           for i in issues if st.session_state.get(f"acc_{i.id}")]
        if accepted_issues:
            report_lines = ["WRITEABLE – ACCEPTED FIXES REPORT", "=" * 45, ""]
            for iss, fix in accepted_issues:
                report_lines += [
                    f"[{iss.category.upper()} / {iss.severity.upper()}]",
                    f"Issue   : {iss.title}",
                    f"Original: {iss.snippet}",
                    f"Fix     : {fix}",
                    ""
                ]
            st.download_button(
                "⬇ Download fixes report (.txt)",
                data="\n".join(report_lines).encode("utf-8"),
                file_name="fixes_report.txt",
                mime="text/plain"
            )
        else:
            st.caption("Accept at least one AI fix to download a fixes report.")


# ════════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════════
logo_path = Path("logo.png")
if logo_path.exists():
    st.sidebar.image(str(logo_path), use_container_width=True)
else:
    st.sidebar.markdown("## 📝 WriteAble")

st.sidebar.markdown("---")
st.sidebar.markdown("## Navigation")
page = st.sidebar.selectbox(
    "Choose a section:",
    ["Overview", "Upload & Analyze", "Analysis Results", "Quick Guide", "Full Guide", "About"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🤖 AI Fix Settings")
api_key = st.sidebar.text_input(
    "Anthropic API Key",
    type="password",
    help="Needed for AI Fix suggestions. Your key is never stored.",
    placeholder="sk-ant-…"
) or None

# Status indicators
st.sidebar.markdown("---")
st.sidebar.markdown("**Package status**")
st.sidebar.markdown(f"{'✅' if HAS_SPELL else '⚠'} Spell checker ({'pyspellchecker' if HAS_SPELL else 'not installed'})")
st.sidebar.markdown(f"{'✅' if HAS_ANTHROPIC else '⚠'} AI fixes ({'anthropic' if HAS_ANTHROPIC else 'not installed'})")
st.sidebar.markdown(f"{'✅' if HAS_DOCX else '⚠'} DOCX support ({'python-docx' if HAS_DOCX else 'not installed'})")
st.sidebar.markdown(f"{'✅' if HAS_PDF else '⚠'} PDF support ({'pdfplumber' if HAS_PDF else 'not installed'})")


# ════════════════════════════════════════════════════════════════════════════════
# PAGES
# ════════════════════════════════════════════════════════════════════════════════

# ── OVERVIEW ──────────────────────────────────────────────────────────────────
if page == "Overview":
    st.title("WriteAble – Accessible Document Helper")
    st.markdown("""
    WriteAble analyzes documents for **accessibility, readability, and grammar issues**
    and provides plain-language explanations and AI-powered fix suggestions.
    """)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Check types", "12", "Grammar, Readability, Accessibility")
    col_b.metric("Max file size", "30 MB", "PDF, DOCX, TXT")
    col_c.metric("AI fix model", "Claude Haiku", "Fast & accurate")

    st.markdown("---")
    st.markdown("### What WriteAble checks")

    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        st.markdown("**📝 Grammar**")
        st.markdown("- Spelling mistakes\n- Repeated words\n- Extra spaces")
    with r1c2:
        st.markdown("**📖 Readability**")
        st.markdown("- Long sentences\n- Flesch Reading Ease\n- Grade level\n- Passive voice")
    with r1c3:
        st.markdown("**♿ Accessibility**")
        st.markdown("- Non-inclusive language\n- Undefined acronyms\n- Missing headings\n- ALL CAPS overuse\n- Bare URLs")

    st.markdown("---")
    st.info("👉 Go to **Upload & Analyze** in the sidebar to get started.")


# ── UPLOAD & ANALYZE ──────────────────────────────────────────────────────────
elif page == "Upload & Analyze":
    st.title("Upload or Paste Your Document")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📁 Upload a file")
        uploaded = st.file_uploader(
            "Choose a file (TXT, DOCX, or PDF)",
            type=["txt", "docx", "pdf"],
            help="Files are processed locally and never stored."
        )
        if uploaded:
            st.info(f"File loaded: **{uploaded.name}** ({uploaded.size / 1024:.1f} KB)")

    with col2:
        st.subheader("✏ Paste text")
        pasted = st.text_area(
            "Paste your document text here:",
            height=220,
            placeholder="Paste any document text here…",
            help="Paste plain text, Markdown, or any document copy."
        )

    st.markdown("---")

    if st.button("🔍 Run Accessibility Check", type="primary"):
        # Determine text source
        text = None
        source_label = ""

        if uploaded:
            with st.spinner("Reading file…"):
                text = extract_text(uploaded)
                source_label = uploaded.name
        elif pasted and pasted.strip():
            text = pasted.strip()
            source_label = "pasted text"
        else:
            st.warning("Please upload a file or paste some text first.")

        if text and text.strip():
            if len(text.strip()) < 20:
                st.warning("Text is too short to analyze (need at least 20 characters).")
            else:
                with st.spinner("Running accessibility checks…"):
                    issues = run_checks(text)

                # Store in session state
                st.session_state["analysis_text"]   = text
                st.session_state["analysis_issues"]  = issues
                st.session_state["analysis_source"]  = source_label
                # Clear previous fix state
                for key in [k for k in st.session_state if k.startswith(("fix_", "acc_", "dis_"))]:
                    del st.session_state[key]

                st.success(f"✅ Analysis complete: **{len(issues)} issue(s)** found in {source_label}")

                # Mini preview
                errors   = sum(1 for i in issues if i.severity == "error")
                warnings = sum(1 for i in issues if i.severity == "warning")
                infos    = sum(1 for i in issues if i.severity == "info")
                pc1, pc2, pc3 = st.columns(3)
                pc1.metric("🔴 Errors",     errors)
                pc2.metric("🟡 Warnings",   warnings)
                pc3.metric("🔵 Suggestions", infos)

                st.info("👉 Go to **Analysis Results** in the sidebar to view the full interactive report.")


# ── ANALYSIS RESULTS ──────────────────────────────────────────────────────────
elif page == "Analysis Results":
    st.title("Analysis Results")

    if "analysis_issues" not in st.session_state:
        st.info("No analysis has been run yet. Go to **Upload & Analyze** first.")
    else:
        issues = st.session_state["analysis_issues"]
        text   = st.session_state["analysis_text"]
        source = st.session_state.get("analysis_source", "document")

        st.markdown(f"**Source:** {source} &nbsp;|&nbsp; **{len(text.split())} words** &nbsp;|&nbsp; **{len(issues)} issue(s) found**")
        st.markdown("---")

        render_report(issues, text, api_key)


# ── QUICK GUIDE ───────────────────────────────────────────────────────────────
elif page == "Quick Guide":
    st.title("Quick User Guide")
    st.markdown("""
    **1. Upload & Analyze**
    Go to *Upload & Analyze* in the sidebar. Upload a TXT/DOCX/PDF file or paste text directly,
    then click **Run Accessibility Check**.

    **2. View Results**
    Navigate to *Analysis Results*. You'll see a summary dashboard showing Errors, Warnings, and Suggestions.

    **3. Browse issues by tab**
    Issues are grouped into three tabs: **Grammar**, **Readability**, and **Accessibility**.
    Use the *All Issues* tab to see everything at once.

    **4. Filter & search**
    Use the filter panel to narrow by category or severity, or search for specific keywords.

    **5. Expand an issue**
    Click any issue row to expand it. You'll see:
    - A plain-English explanation of the problem
    - The problematic text snippet
    - A quick suggested replacement (where applicable)

    **6. Get an AI Fix**
    Add your Anthropic API key in the sidebar, then click **🤖 Get AI Fix** on any issue.
    Review the suggestion and click **✅ Accept this fix** to log it.

    **7. Export**
    Scroll to the bottom of the report to download the original text or a **Fixes Report**
    summarizing every fix you accepted.
    """)


# ── FULL GUIDE ────────────────────────────────────────────────────────────────
elif page == "Full Guide":
    st.title("Full User Guide")
    st.markdown("""
    ### Supported Input

    | Format | Support |
    |--------|---------|
    | Plain text (.txt) | ✅ Full support |
    | Word document (.docx) | ✅ Requires `python-docx` |
    | PDF (.pdf) | ✅ Requires `pdfplumber` |
    | Pasted text | ✅ Always available |

    Maximum recommended file size: **30 MB**.

    ---

    ### What Each Check Does

    **Grammar**
    - *Spelling* — Flags words that may be misspelled and suggests corrections. Proper nouns and
      capitalised words are skipped to reduce false positives.
    - *Repeated words* — Detects unintentional double words (e.g. "the the").
    - *Extra spaces* — Flags multiple consecutive spaces.

    **Readability**
    - *Sentence length* — Flags sentences over 25 words (warning) or 35 words (error).
    - *Flesch Reading Ease* — A 0–100 score: 60+ is suitable for general audiences.
    - *Flesch-Kincaid Grade Level* — U.S. school grade equivalent; aim for Grade 8 or below.
    - *Passive voice* — Flags documents with more than 4 passive constructions.

    **Accessibility**
    - *Inclusive language* — Flags 20+ patterns of non-inclusive phrasing and suggests alternatives.
    - *ALL CAPS overuse* — Flags documents with more than 3 all-caps words (excluding defined acronyms).
    - *Undefined acronyms* — Flags acronyms that never appear in parenthetical definitions.
    - *Missing headings* — Warns when documents over 200 words have no heading structure.
    - *Bare URLs* — Flags URLs used as raw link text (inaccessible to screen readers).

    ---

    ### AI Fix Feature

    Each issue has a **🤖 Get AI Fix** button. This calls **Claude Haiku** to generate a specific,
    context-aware correction. You can:
    - **Accept** the fix → it's logged in the Fixes Report
    - **Dismiss** the issue → it's hidden from the report

    Your API key is used only for the current session and is never stored.

    ---

    ### Exporting

    - **Download original text** — Your source document as plain text.
    - **Download fixes report** — A structured summary of every fix you accepted, showing the original
      snippet alongside the corrected version.

    ---

    ### Accessibility of WriteAble Itself

    - High-contrast badges and colour-coded severity
    - Keyboard-navigable interface via Streamlit
    - Plain-language explanations for every issue
    - No animations or auto-playing media
    """)


# ── ABOUT ────────────────────────────────────────────────────────────────────
elif page == "About":
    st.title("About WriteAble")
    st.markdown("""
    WriteAble helps writers, content creators, and teams produce documents that are clearer,
    more inclusive, and accessible to all readers — including people who use assistive technology.

    **Our principles:**
    - Accessibility checks should be *understandable*, not just flagged
    - Plain-language explanations help writers learn, not just   fix
    - AI suggestions should assist human judgment, not replace it

    **Technology stack:**
    - [Streamlit](https://streamlit.io) — UI framework
    - [textstat](https://github.com/textstat/textstat) — Readability metrics
    - [pyspellchecker](https://github.com/barrust/pyspellchecker) — Spelling
    - [Anthropic Claude](https://www.anthropic.com) — AI fix suggestions

    **Standards alignment:**
    - Reading level targets follow [Plain Language Guidelines](https://www.plainlanguage.gov/)
    """)