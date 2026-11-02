"""EconLens AI -- Streamlit app with CommCalc-inspired adapted visual design.

Author: Rishabh Shah | Advisor: Dr. Qingyang Xiao
Original economics/ML/NLP engine is in econolens_core.py.
Uploaded CommCalc interface was an unrelated commission dashboard. Its layout,
colors, cards, and user-supplied hero art are adapted, not its unrelated workflows.
"""
from __future__ import annotations

import base64
import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from safe_visuals import html_table, topic_bars

from econolens_core import (
    ADVISOR_NAME,
    APP_NAME,
    ArticleMetadata,
    EconomicsNewsPipeline,
    FeedbackBandit,
    ReaderProfile,
    STUDENT_NAME,
    fetch_public_article,
)

ROOT = Path(__file__).resolve().parent
PAGES = [
    "Overview",
    "Article Studio",
    "Economic Insights",
    "Personal Impact",
    "Word Forecast Lab",
    "Evidence & Quality",
    "Feedback Studio",
    "About the Project",
]

st.set_page_config(
    page_title="EconLens AI | Clearer Economics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def sample_article() -> str:
    return (ROOT / "sample_article.txt").read_text(encoding="utf-8")


@st.cache_data(show_spinner=False)
def hero_background() -> str:
    image = (ROOT / "assets" / "hero-bg.jpg").read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(image).decode("ascii")


@st.cache_data(show_spinner=False, ttl=1800)
def extract_from_url(url: str) -> dict[str, str]:
    return fetch_public_article(url)


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def app_styles() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --navy: #002333; --teal: #159A9C; --muted: #5A6A78; --mint: #DEEFE7; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1,h2,h3,h4,h5 { font-family: 'Manrope', sans-serif; letter-spacing: -0.035em; color: #002333; }
.stApp { background: #F6F8FA; }
[data-testid="stAppViewBlockContainer"], .block-container {
    padding-top: 5.0rem !important; padding-bottom: 3.0rem !important; max-width: 1250px !important;
}
header[data-testid="stHeader"] { background: rgba(246,248,250,.97); }
[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E2E9EE; }
[data-testid="stSidebar"] .block-container { padding-top: 1.6rem !important; }
[data-testid="stSidebar"] [role="radiogroup"] > label {
    border-radius: 8px; padding: .4rem .6rem; margin: .13rem 0;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:hover { background: #F0F4F2; }
[data-testid="stSidebar"] h3 { font-size: 1.05rem; }
[data-testid="stMetric"] { background: #fff; border: 1px solid #E2E9EE; border-radius: 12px; padding: 1.0rem 1.15rem; }
[data-testid="stMetricLabel"] p { color: #5A6A78; font-weight: 600; }
[data-testid="stMetricValue"] { color: #002333; font-family: 'Manrope'; }
div.stButton > button[kind="primary"], div.stDownloadButton > button[kind="primary"] {
    background: #159A9C; color: #fff; border-radius: 9px; border: 1px solid #159A9C; font-weight: 700;
}
div.stButton > button[kind="primary"]:hover, div.stDownloadButton > button[kind="primary"]:hover {
    background: #0D7A7C; border-color: #0D7A7C;
}
.stTabs [data-baseweb="tab-list"] { gap: .3rem; }
.stTabs [data-baseweb="tab"] { font-weight: 600; }
[data-testid="stExpander"] { background: #fff; border-radius: 10px; border: 1px solid #E2E9EE; }
/* Static HTML displays avoid lazy DataFrame / Vega-Lite JavaScript modules. */
.e-table-container { width:100%; max-width:100%; overflow:auto; background:#FFFFFF;
    border:1px solid #DCE6EA; border-radius:13px; margin:12px 0 22px;
    box-shadow:0 5px 18px rgba(0,35,51,.028); }
.e-native-table { width:100%; min-width:480px; border-collapse:collapse;
    text-align:left; font-size:.85rem; line-height:1.52; color:#163849; }
.e-native-table thead th { padding:13px 15px; font-weight:800; color:#05435A;
    background:#E7F4F2; border-bottom:2px solid #CBE4DE; text-align:left;
    white-space:normal; overflow-wrap:anywhere; }
.e-native-table tbody td { padding:12px 15px; border-bottom:1px solid #EAF0F3;
    min-width:85px; vertical-align:top; overflow-wrap:anywhere; word-break:normal; }
.e-native-table tbody tr:nth-child(even) { background:#F8FBFC; }
.e-native-table tbody tr:last-child td { border-bottom:0; }
.e-empty {padding:16px 20px; color:#607783; background:#fff; border-radius:10px;}
.e-topic-visual {padding:21px 24px 13px; background:white; border:1px solid #DCE6EA;
    border-radius:14px; box-shadow:0 5px 18px rgba(0,35,51,.026); margin:12px 0 23px; }
.e-topic-intro {font-size:.81rem; color:#567786; line-height:1.5; margin:0 0 17px;}
.e-topic-row {margin:0 0 17px;}
.e-topic-label {display:flex;justify-content:space-between;align-items:baseline;gap:12px;
    font-size:.86rem;color:#153D50;margin-bottom:7px;}
.e-topic-label span {flex:1;overflow-wrap:anywhere;}
.e-topic-label strong {font-size:.82rem;color:#007F82;white-space:nowrap;}
.e-topic-track {height:13px;background:#E5F1F0;border-radius:10px;overflow:hidden;}
.e-topic-bar {height:100%;background:linear-gradient(90deg,#14677B,#24B5A6);
    border-radius:10px;min-width:0;}
@media(max-width:750px) {
 .e-topic-visual {padding:16px 12px 5px;}
 .e-native-table {font-size:.79rem;}
 .e-native-table thead th,.e-native-table tbody td {padding:10px 11px;}
}
.e-topline { display:flex; justify-content:space-between; align-items:center; gap:10px;
    padding: 0 0 16px; border-bottom:1px solid #DFE8EA; margin-bottom:23px; flex-wrap:wrap; }
.e-logo { font: 800 1.05rem 'Manrope',sans-serif; letter-spacing:-.025em; color:#002333; }
.e-logo-badge { background:#DDF4EE; color:#118B8E; border-radius:7px; padding:5px 9px; margin-right:9px; }
.e-byline { font-size:.81rem; color:#72818B; margin-top:9px; }
.e-sidebar-brand { font:800 1.45rem 'Manrope',sans-serif; color:#002333; letter-spacing:-.06em; padding: 6px 0 0; }
.e-sidebar-brand span { color:#159A9C; }
.e-sidebar-kicker { color:#82919C; font-size:.68rem; text-transform:uppercase; letter-spacing:.16em; margin:2px 0 18px; }
.e-eyebrow { font-weight:800; font-size:.75rem; letter-spacing:.15em; text-transform:uppercase; color:#159A9C; margin: 0 0 8px; }
.e-section-title { font:800 1.8rem 'Manrope',sans-serif; color:#002333; letter-spacing:-.045em; margin:.25rem 0 .3rem; }
.e-sub { color:#657684; font-size:.97rem; margin:0 0 1.5rem; }
.e-hero { min-height:315px; border-radius:18px; padding:42px 42px 36px;
    overflow:hidden; box-shadow:0 20px 48px rgba(0,35,51,.12); background-size:cover; background-position:center center;
    position:relative; margin-bottom:18px; }
.e-hero h1 { color:#fff; font-weight:800; font-size:clamp(2.1rem,4.2vw,3.9rem);
    line-height:1.11; letter-spacing:-.065em; margin:12px 0 15px; max-width:760px; }
.e-hero h1 span { color:#8CDED1; }
.e-hero p { color:#E2EFF0; font-size:1.05rem; max-width:670px; line-height:1.65; }
.e-hero-chip { display:inline-block; color:#C7FFF1; border:1px solid rgba(162,242,223,.4);
    background:rgba(21,154,156,.20); border-radius:20px; padding:7px 13px;
    font-size:.73rem; letter-spacing:.08em; font-weight:800; }
.e-stat { background:#fff; border:1px solid #DFE9EB; border-radius:13px; padding:21px 20px 17px;
    min-height:119px; margin-bottom:10px; box-shadow:0 7px 23px rgba(0,35,51,.025); }
.e-stat-val {font:800 1.6rem 'Manrope',sans-serif;color:#002333;margin:5px 0 3px;letter-spacing:-.05em;}
.e-stat-lbl {font-size:.75rem;color:#6A7C88;font-weight:700;}
.e-stat-detail {font-size:.75rem;color:#159A9C;margin-top:4px;}
.e-card { background:#fff; border:1px solid #DFE7ED; border-radius:14px; padding:21px;
    margin-bottom:13px; min-height:125px; box-shadow: 0 5px 20px rgba(0,35,51,.02); }
.e-card h4 {font:800 1.00rem 'Manrope',sans-serif;color:#002333;margin:5px 0 8px;}
.e-card p {color:#677B86;font-size:.88rem;line-height:1.62;margin:0;}
.e-icon {display:inline-block;color:#0B888D;background:#E1F6F1;border-radius:10px;padding:7px 10px;font-size:1.17rem;}
.e-mini-label {font-size:.74rem; color:#6D8291;font-weight:750;text-transform:uppercase;letter-spacing:.08em;}
.e-callout { background:#E8F7F2;border-left:4px solid #159A9C;border-radius:9px;
    color:#164D55;padding:15px 20px;font-size:.94rem;line-height:1.55;margin:12px 0 20px; }
.e-step {background:#fff;border:1px solid #DFE7ED;border-radius:12px;padding:14px 16px;margin:8px 0;
    display:flex;gap:14px;align-items:flex-start;}
.e-step-n {border-radius:7px;background:#159A9C;color:#fff;padding:6px 10px;font-weight:800;}
.e-step b {color:#002333;font-size:.93rem;}
.e-step p {margin:3px 0 0;color:#72818B;font-size:.83rem;}
.e-footer {margin-top:32px;padding:19px 0;border-top:1px solid #DBE4E8;font-size:.82rem;color:#6A7C88;}
.e-divider { margin: 20px 0; }
@media (max-width:800px) {
 .e-hero {padding:25px 20px;min-height:270px;}
 .e-hero h1 {font-size:2rem;}
 .e-hero p {font-size:.92rem;}
 .block-container {padding-left:1rem!important;padding-right:1rem!important;padding-top:4.3rem!important;}
 .e-section-title {font-size:1.55rem;}
}
</style>
        """,
        unsafe_allow_html=True,
    )


def nav_to(page: str) -> None:
    st.session_state._next_page = page
    st.rerun()


def page_heading(kicker: str, title: str, intro: str) -> None:
    st.markdown(
        f'<div class="e-eyebrow">{e(kicker)}</div>'
        f'<div class="e-section-title">{e(title)}</div>'
        f'<div class="e-sub">{e(intro)}</div>',
        unsafe_allow_html=True,
    )


def panel(title: str, body: str, icon: str = "✦") -> None:
    st.markdown(
        f'<div class="e-card"><span class="e-icon">{e(icon)}</span>'
        f'<h4>{e(title)}</h4><p>{e(body)}</p></div>',
        unsafe_allow_html=True,
    )


def banner(text: str) -> None:
    st.markdown(f'<div class="e-callout">{e(text)}</div>', unsafe_allow_html=True)


def require_result() -> dict | None:
    result = st.session_state.get("analysis_result")
    if result is None:
        st.info("Start with an economics article. Your analysis will then be available on all pages.")
        if st.button("Go to Article Studio", type="primary"):
            nav_to("Article Studio")
    return result


def report_downloads(result: dict) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "↓ Download readable Markdown report", result["markdown_report"],
            file_name="econolens_report.md", mime="text/markdown", use_container_width=True,
        )
    with c2:
        st.download_button(
            "↓ Download complete analysis JSON",
            json.dumps(result, indent=2, ensure_ascii=False),
            file_name="econolens_analysis.json", mime="application/json", use_container_width=True,
        )


def dashboard() -> None:
    st.markdown(
        f'<div class="e-hero" style="background-image:'
        f'linear-gradient(100deg, rgba(0,35,51,.96) 2%,rgba(0,35,51,.84) 51%,rgba(0,35,51,.22) 100%),'
        f'url(\'{hero_background()}\')">'
        '<span class="e-hero-chip">THE ECONOMICS INTELLIGENCE STUDIO</span>'
        '<h1>Understand the news.<br><span>See what it means for you.</span></h1>'
        '<p>Turn complicated economic headlines into clear explanations, grounded stories, '
        'and everyday-life insights — guided by machine learning and readable evidence.</p>'
        '</div>', unsafe_allow_html=True,
    )
    c1, c2, space = st.columns([1.3, 1.3, 2.3])
    with c1:
        if st.button("Analyze an article →", type="primary", use_container_width=True):
            nav_to("Article Studio")
    with c2:
        if st.button("Explore the workflow", use_container_width=True):
            nav_to("About the Project")

    st.markdown("### Your economics toolkit")
    metrics = [
        ("Learning levels", "05", "From takeaway to implications"),
        ("Insight workspaces", "06+", "Story, impact, evidence and more"),
        ("AI components", "ML + NLP", "Topic DNN and word forecasting"),
    ]
    cols = st.columns(3)
    for col, (label, val, detail) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="e-stat"><div class="e-stat-lbl">{e(label)}</div>'
                        f'<div class="e-stat-val">{e(val)}</div><div class="e-stat-detail">{e(detail)}</div></div>',
                        unsafe_allow_html=True)

    st.markdown("### Made to make economics understandable")
    tiles = [
        ("Readable summaries", "Turn dense news into a 15-second takeaway and a layered summary.", "▤"),
        ("Explain the terminology", "Translate economic phrases into plain-English definitions and examples.", "◎"),
        ("Personal relevance", "Explore possible effects on housing, work, everyday costs and borrowing.", "⌂"),
        ("Check the evidence", "Find the original source sentences, terminology, caveats and quality checks.", "✓"),
    ]
    cols = st.columns(4)
    for col, (title, body, symbol) in zip(cols, tiles):
        with col:
            panel(title, body, symbol)

    left, right = st.columns([1.4, 1])
    with left:
        st.markdown("### How it works")
        for n, title, detail in [
            (1, "Bring an article", "Paste news, submit a public link, or upload a text file."),
            (2, "AI parses economic themes", "TF-IDF extracts evidence while a topic DNN identifies signals."),
            (3, "Read it in plain language", "Get a concise hierarchy, economic story and glossary."),
            (4, "Connect to real life", "Review evidence-backed possible impacts through your profile."),
        ]:
            st.markdown(f'<div class="e-step"><span class="e-step-n">{n:02d}</span>'
                        f'<div><b>{e(title)}</b><p>{e(detail)}</p></div></div>', unsafe_allow_html=True)
    with right:
        st.markdown("### Your research, your perspective")
        panel("Human-centered economics", "Designed for students, educators and curious readers; the purpose is clearer understanding, not automated financial advice.", "✧")
        panel("Feedback-informed presentation", "A multi-armed bandit experiments with explanation style; economic facts remain tied to the source.", "↗")
    result = st.session_state.get("analysis_result")
    if result:
        banner("Your last article analysis is ready. Continue exploring its themes, personal impacts and source evidence.")
        if st.button("Open your economic insights →", type="primary"):
            nav_to("Economic Insights")


def article_studio(profile: ReaderProfile, pipeline: EconomicsNewsPipeline, neural_enabled: bool) -> None:
    page_heading("01 / Article studio", "Make economics news make sense", "Bring a complicated article. EconLens will create a structured analysis in plain language.")
    modes = ["Example article", "Paste article text", "Public news URL", "Upload article file"]
    mode = st.radio("Choose input type", modes, horizontal=True, key="article_mode")
    article = ""
    metadata = ArticleMetadata()
    if mode == "Example article":
        article = sample_article()
        metadata = ArticleMetadata(title="Fictional inflation and jobs demonstration", source="EconLens synthetic teaching article")
        banner("Demo mode uses a fictional teaching article, not real news. All findings are illustrative.")
        with st.expander("Preview the sample economics article"):
            st.write(article)
    elif mode == "Paste article text":
        title = st.text_input("Article headline", value="Untitled economics news")
        source = st.text_input("Publisher or source", value="User-provided article")
        article = st.text_area("Article text", height=300, placeholder="Paste your economic news article here...")
        metadata = ArticleMetadata(title=title, source=source)
    elif mode == "Public news URL":
        url = st.text_input("Public URL", placeholder="https://example.com/economics-news-story")
        metadata = ArticleMetadata(title="Web article", source="Public URL", url=url.strip())
        st.caption("The public-webpage extractor does not bypass paywalls, sign-ins or access controls.")
    else:
        uploaded = st.file_uploader("Upload TXT, Markdown or HTML", type=["txt", "md", "html", "htm"])
        if uploaded is not None:
            article = uploaded.getvalue().decode("utf-8", errors="replace")
            if uploaded.name.lower().endswith((".html", ".htm")):
                from bs4 import BeautifulSoup
                article = BeautifulSoup(article, "html.parser").get_text(" ")
            metadata = ArticleMetadata(title=uploaded.name, source="Uploaded text file")
    if article:
        st.caption(f"Loaded: approximately {len(article.split()):,} words · {len(article):,} characters")
    with st.container(border=True):
        st.markdown("**Analysis pipeline**")
        st.caption("Extract source evidence → identify economic topics → simplify terminology → form a grounded story → describe possible personal impacts → evaluate readability")
        start = st.button("✦ Analyze economics article", type="primary", use_container_width=True)
    if start:
        try:
            if mode == "Public news URL":
                if not metadata.url:
                    raise ValueError("Enter a public economics article URL first.")
                with st.spinner("Reading the public article..."):
                    fetched = extract_from_url(metadata.url)
                article = fetched["text"]
                metadata = ArticleMetadata(title=fetched["title"], source=fetched["source"], url=fetched["url"])
            with st.spinner("Running TF-IDF, economics DNN, explainability and profile insights..."):
                result = pipeline.analyze(article, profile=profile, metadata=metadata, use_neural=neural_enabled)
            st.session_state.analysis_result = result
            st.success("Article analyzed! The result is now available in all the insights pages.")
        except Exception as exc:
            st.error(f"Could not analyze the article: {exc}")
    if st.session_state.get("analysis_result"):
        c1, c2 = st.columns(2)
        with c1:
            if st.button("View economic insights →", use_container_width=True):
                nav_to("Economic Insights")
        with c2:
            if st.button("Explore personal impacts →", use_container_width=True):
                nav_to("Personal Impact")
        banner(st.session_state.analysis_result["hierarchy"]["Level 1 - 15-second takeaway"])
        report_downloads(st.session_state.analysis_result)


def economic_insights() -> None:
    page_heading("02 / Story & explanation", "The economic story, simplified", "Start with the big picture, then drill down into themes, drivers and economic concepts.")
    result = require_result()
    if not result:
        return
    hierarchy = result["hierarchy"]
    banner(hierarchy["Level 1 - 15-second takeaway"])
    tab1, tab2, tab3 = st.tabs(["Learning hierarchy", "Economic story", "Topics & outlook"])
    with tab1:
        st.markdown("#### Level 2 · Main developments")
        for item in hierarchy["Level 2 - Main developments"]:
            st.markdown(f"- {item}")
        st.markdown("#### Level 3 · Main economic themes")
        st.markdown(html_table(hierarchy["Level 3 - Main economic themes"]), unsafe_allow_html=True)
        st.markdown("#### Level 4 · Causes and evidence")
        for item in hierarchy["Level 4 - Causes and evidence"]["possible_drivers_stated_in_article"]:
            st.markdown(f"- {item}")
        st.markdown("#### Level 5 · Who might be affected")
        for item in hierarchy["Level 5 - People and next chapter"]["what_the_article_says_may_happen_next"]:
            st.markdown(f"- {item}")
    with tab2:
        for title, story in result["story"].items():
            st.markdown(f"#### {title}")
            st.write(story)
        neural = result.get("neural") or {}
        if neural.get("story"):
            st.markdown("#### Optional FLAN-T5-generated version")
            st.write(neural["story"])
            st.caption(neural.get("grounding_note", ""))
    with tab3:
        if result.get("topic_scores"):
            st.markdown(topic_bars(result["topic_scores"]), unsafe_allow_html=True)
        st.markdown("#### Evidence behind the summary")
        for item in result["source_summary"]:
            st.markdown(f"- {item}")
    st.markdown("#### Export your analysis")
    report_downloads(result)


def personal_impact() -> None:
    page_heading("03 / Personal impact", "What could this mean for your life?", "Possible impact pathways depend on your chosen profile and what the article actually reports.")
    result = require_result()
    if not result:
        return
    banner("These are plausible educational interpretations, not guarantees or tailored financial advice. Read the article evidence before making decisions.")
    impacts = result.get("personal_impacts", [])
    if not impacts:
        st.info("No strong enough profile-related impacts were found in this article.")
    for item in impacts:
        confidence = max(0.0, min(1.0, float(item["confidence"])))
        with st.expander(f"{item['area']}  ·  Signal confidence {confidence:.0%}", expanded=True):
            st.markdown(f"**Possible real-life effect:** {item['possible_impact']}")
            st.markdown(f"**Economic reasoning:** {item['why']}")
            st.markdown(f"**Practical follow-up:** {item['practical_check']}")
            st.markdown(f"**Evidence in article:** {item['article_evidence']}")
            st.progress(confidence)
    st.caption("To update the reader's circumstances for a new analysis, adjust 'Reader profile' in the sidebar and analyze the article again.")


def word_forecast(pipeline: EconomicsNewsPipeline) -> None:
    page_heading("04 / NLP playground", "Word forecasting lab", "Explore n-gram next-word suggestions drawn from patterns in the article itself.")
    result = require_result()
    if not result:
        return
    banner("This word forecast predicts likely following words. It does not predict future financial markets, government decisions, or economic events.")
    prompts = list(result.get("forecast_examples") or ["interest rates"])
    suggested = st.selectbox("Suggested phrase from the article", prompts)
    phrase = st.text_input("Enter a phrase or test the suggestion", value=suggested, key="forecast_prefix")
    if st.button("Predict next words", type="primary"):
        suggestions = pipeline.word_forecaster.predict(phrase, top_k=8)
        if suggestions:
            st.markdown(html_table(suggestions), unsafe_allow_html=True)
        else:
            st.info("No well-supported next words were found for this prefix.")
        st.markdown("**Autocomplete demonstration**")
        st.write(pipeline.word_forecaster.autocomplete(phrase, additional_words=8))
    st.markdown("### The models behind the lab")
    c1, c2 = st.columns(2)
    with c1:
        panel("Statistical word patterns", "Transparent 4-gram forecasting looks at recent tokens and suggests likely continuations.", "↗")
    with c2:
        panel("Economic topic recognition", "A neural classifier groups article sentences into economic themes; it does not reason like a human expert.", "▦")
    st.caption(f"Current economic topic model: {pipeline.topic_model.architecture}")


def evidence_quality(pipeline: EconomicsNewsPipeline) -> None:
    page_heading("05 / Trust & evidence", "Transparency before conclusions", "Review source sentences, glossary definitions, readability and safeguards.")
    result = require_result()
    if not result:
        return
    tabs = st.tabs(["Source evidence", "Economics glossary", "Readability & checks", "Optional neural rewrite"])
    with tabs[0]:
        for sentence in result["source_summary"]:
            st.markdown(f"- {sentence}")
        st.markdown("#### Recognized key phrases")
        if result.get("key_phrases"):
            st.markdown(html_table(result["key_phrases"]), unsafe_allow_html=True)
    with tabs[1]:
        terms = result.get("terms") or []
        if terms:
            df = pd.DataFrame(terms)
            cols = [col for col in ["term", "count", "plain_definition", "why_it_matters", "evidence"] if col in df]
            st.markdown(html_table(df[cols]), unsafe_allow_html=True)
        else:
            st.info("No predefined economics glossary terms were detected.")
    with tabs[2]:
        st.markdown("#### Readability comparison")
        st.markdown(html_table(result["readability"]), unsafe_allow_html=True)
        st.markdown("#### Quality notes")
        for message in result.get("quality_flags", []):
            st.markdown(f"- {message}")
        with st.expander("Technical background"):
            st.write(f"Economics topic DNN architecture: {pipeline.topic_model.architecture}")
            st.write(f"Model optimization iterations: {pipeline.topic_model.training_iterations}")
            st.write("Feedback component: epsilon-greedy multi-armed bandit focused on explanation presentation, not on rewriting facts.")
    with tabs[3]:
        data = result.get("neural")
        if data:
            if data.get("error"):
                st.warning(data["error"])
            else:
                st.write(data.get("plain_summary", "No neural summary was generated."))
                if data.get("unsupported_numbers_detected"):
                    st.warning("Number-like claims to verify: " + ", ".join(data["unsupported_numbers_detected"]))
                st.caption(data.get("grounding_note", ""))
        else:
            st.info("Neural rewriting was not enabled. The base pipeline is available without additional downloads or API keys.")
    report_downloads(result)


def feedback_page(pipeline: EconomicsNewsPipeline) -> None:
    page_heading("06 / Human-in-the-loop", "Help EconLens explain better", "Rate the experience and explore how an online-learning bandit adjusts format preference.")
    banner("In this MVP, feedback preferences live in the current browser session only; they do not change source facts or form a shared learning database.")
    with st.form("feedback_form", border=True):
        style = st.selectbox("Explanation style", FeedbackBandit.STYLES)
        overall = st.slider("Overall experience", 1, 5, 4)
        clarity = st.slider("Clarity of explanation", 1, 5, 4)
        usefulness = st.slider("Personal usefulness", 1, 5, 4)
        comment = st.text_area("Suggestions for Rishabh (optional)")
        submitted = st.form_submit_button("Submit feedback", type="primary", use_container_width=True)
    if submitted:
        record = pipeline.feedback.update(style, overall, clarity, usefulness, comment)
        st.success(f"Feedback applied to this session's preference learner · reward {record['reward']:.3f}.")
    st.markdown("### Presentation-style feedback learner")
    st.markdown(html_table(pipeline.feedback.status()), unsafe_allow_html=True)
    st.markdown(f"**Current suggested presentation:** {pipeline.feedback.recommend(epsilon=0.0)}")
    st.caption("This is an educational RL/bandit demonstration. Persistent cross-user learning would require a separate consented data-storage design.")


def about() -> None:
    page_heading("07 / Project overview", "Built for a more economics-literate world", "The MVP combines economic NLP, an approachable interface, and practical context for everyday readers.")
    c1, c2 = st.columns(2)
    with c1:
        panel("Creator: Rishabh Shah", "Senior student · Economics news simplifier, human-readable storytelling, and research prototype.", "◈")
    with c2:
        panel("Advisor: Dr. Qingyang Xiao", "AI/ML, research methodology and product-development mentoring.", "◎")
    st.markdown("### End-to-end analysis workflow")
    process = [
        ("INPUT", "Text, URL or uploaded article; clean and extract public text"),
        ("NLP", "TF-IDF, extractive summary, key phrases and economics glossary"),
        ("ML / DNN", "Neural economic topic classifier trained on reference examples"),
        ("EXPLANATION", "Five-tier hierarchy, economic storyline and evidence signals"),
        ("PERSONALIZATION", "Profile-sensitive potential everyday-life impacts and practical checks"),
        ("FORECASTING", "Article-trained n-gram next-word forecasting demonstration"),
        ("FEEDBACK", "Multi-armed bandit for preferred presentation and readability checks"),
        ("EXPORT", "Download analysis results in Markdown and machine-readable JSON"),
    ]
    for index, (title, detail) in enumerate(process, 1):
        st.markdown(f'<div class="e-step"><span class="e-step-n">{index:02d}</span>'
                    f'<div><b>{e(title)}</b><p>{e(detail)}</p></div></div>', unsafe_allow_html=True)
    st.markdown("### Responsible use")
    st.write("This prototype is for education, not personalized financial, legal, tax or investment advice. It may miss context and should be checked against original sources. The optional FLAN-T5 model is not needed for default hosting.")
    st.link_button("Open the live EconLens app", "https://econolens-ai-economics-news.streamlit.app/")
    st.link_button("Visit the source repository on GitHub", "https://github.com/qxiao2ub/EconoLens-AI-Economics-News-App")


def main() -> None:
    app_styles()
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "Overview"
    if "_next_page" in st.session_state:
        st.session_state.nav_page = st.session_state.pop("_next_page")
    with st.sidebar:
        st.markdown('<div class="e-sidebar-brand">◈ EconLens <span>AI</span></div>'
                    '<div class="e-sidebar-kicker">ECONOMIC INTELLIGENCE FOR EVERYONE</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="e-mini-label">WORKSPACES</div>', unsafe_allow_html=True)
        page = st.radio("Navigate", PAGES, key="nav_page", label_visibility="collapsed")
        st.divider()
        st.markdown("**Customize your reader profile**")
        with st.expander("Reader profile settings", expanded=(page == "Article Studio")):
            country = st.text_input("Country or region", "United States")
            age_group = st.selectbox("Age group", ["Under 18", "18-24", "25-34", "35-49", "50-64", "65+"], index=1)
            role = st.selectbox("Current role", ["Student", "Employed", "Job seeker", "Business owner", "Retired", "Other"])
            income = st.selectbox("Income situation", ["Lower income", "Middle income", "Higher income", "Prefer not to say"], index=1)
            housing = st.selectbox("Housing status", ["Renter", "Homeowner", "Planning to buy", "Living with family", "Other"])
            debt = st.selectbox("Debt exposure", ["No debt", "Some student or consumer debt", "Mortgage debt", "High variable-rate debt", "Prefer not to say"], index=1)
            sensitivity = st.selectbox("Budget sensitivity", ["Low", "Moderate", "High"], index=1)
            interests = st.text_input("Topics you care about", "everyday prices, jobs, rent, student loans")
            neural_enabled = st.checkbox("Optional FLAN-T5 rewrite", value=False,
                help="Requires optional requirements-neural.txt packages; disabled by default for fast Streamlit hosting.")
        st.divider()
        st.caption(f"Author · {STUDENT_NAME}")
        st.caption(f"Advisor · {ADVISOR_NAME}")

    engine = None
    if page in {"Article Studio", "Word Forecast Lab", "Evidence & Quality", "Feedback Studio"}:
        if "engine" not in st.session_state:
            st.session_state.engine = EconomicsNewsPipeline(feedback_path=None)
        engine = st.session_state.engine

    profile = ReaderProfile.from_interests_text(
        interests, country=country, age_group=age_group, role=role,
        income_situation=income, housing_status=housing, debt_exposure=debt,
        budget_sensitivity=sensitivity,
    )
    st.markdown(
        '<div class="e-topline"><div><span class="e-logo-badge">◈</span><span class="e-logo">'
        'EconLens AI</span></div></div>', unsafe_allow_html=True,
    )
    if page == "Overview":
        dashboard()
    elif page == "Article Studio":
        article_studio(profile, engine, neural_enabled)
    elif page == "Economic Insights":
        economic_insights()
    elif page == "Personal Impact":
        personal_impact()
    elif page == "Word Forecast Lab":
        word_forecast(engine)
    elif page == "Evidence & Quality":
        evidence_quality(engine)
    elif page == "Feedback Studio":
        feedback_page(engine)
    else:
        about()
    st.markdown(
        f'<div class="e-footer"><b>{APP_NAME}</b> · Created by <b>{e(STUDENT_NAME)}</b> · '
        f'Advised by <b>{e(ADVISOR_NAME)}</b> · Open-source educational MVP · MIT License<br>'
        'Verify important economic claims against original sources; this is not financial advice.</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
