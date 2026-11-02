# EconLens AI · Economics News Simplifier

**Student author:** Rishabh Shah  
**Advisor:** Dr. Qingyang Xiao  
**Project:** Economics news simplification, learning hierarchy, article storytelling and personal-impact insights  
**License:** MIT (`LICENSE`)

An AI-enabled educational MVP that turns dense economics news into structured, readable explanations and possible everyday-life impacts. The app combines the original Python NLP/DNN pipeline with a redesign inspired by the uploaded CommCalc React/TanStack dashboard.

## Run in Streamlit Community Cloud

1. **Extract the downloaded ZIP.** Open its `EconLens_AI_Streamlit` folder.
2. Upload the **contents** of that folder to a GitHub repo, for example [qxiao2ub/EconLens-AI-Economics-News-App](https://github.com/qxiao2ub/EconoLens-AI-Economics-News-App). All files need to be at the repository root, not one folder deeper.
3. In [Streamlit Community Cloud](https://share.streamlit.io/), create/deploy an app with your GitHub repository and main file `app.py`.
4. To enable optional neural generation, install dependencies in `requirements-neural.txt` in addition to the standard `requirements.txt`. The app runs without the neural packages.

### Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

## Adapted UI design

The user-provided ZIP (`commcalc-source.zip`) contains **CommCalc**, an unrelated commission-management SaaS prototype implemented with React, TanStack Start, Tailwind and Supabase. Copying its React route code into Streamlit would not run and would replace economics features with commission-management workflows.

Instead, this deployable repo brings its **navy / teal / mint palette**, dashboard card design, sidebar navigation, typography, KPI strip and **original `hero-bg.jpg` artwork** into native Streamlit components. The economics engine remains fully integrated; no second frontend server, JavaScript build, Supabase backend or Node dependency is required. See [`UI_INTEGRATION.md`](UI_INTEGRATION.md) for precise mapping. This is a Streamlit adaptation of the supplied design, not an executable copy of its TanStack/React app.


## AI pipeline and functions

- Economics article ingestion from paste, public URL or uploaded TXT/MD/HTML; bundled fictional teaching example.
- Text preprocessing and TF-IDF / maximal marginal relevance extractive evidence prioritization.
- Multilayer perceptron deep neural network for **economic topic classification**.
- Five-tier information hierarchy (quick takeaway, developments, themes, supporting evidence, implications).
- Economics vocabulary detection, plain-language definitions and grounded storytelling.
- Profile-sensitive **possible** impacts on prices, jobs, rent, mortgages and more.
- N-gram next-word **text forecasting demonstration** (not predicting the future economy).
- Optional open-source FLAN-T5-based plain-language transformation.
- An epsilon-greedy multi-armed bandit prototype for learning preferred explanation styles from session feedback.
- Readability diagnostics, numerical grounding notes, Markdown / JSON exports.

## Folder layout

```text
app.py                       # native Streamlit multipage-like interactive frontend
assets/hero-bg.jpg           # original user-supplied CommCalc UI hero artwork
econolens_core.py            # economics AI / NLP / DNN / feedback engine
safe_visuals.py              # HTML tables and CSS topic charts, without Arrow/Vega JS
sample_article.txt           # fictional economics article for repeatable tests
requirements.txt             # direct Streamlit Community Cloud dependencies
requirements-neural.txt      # optional LLM dependencies
.streamlit/config.toml       # navy / teal Streamlit theme
notebooks/                   # original research notebook
UI_INTEGRATION.md            # mapping of the user-supplied UI to EconLens
AUTHORS.md                   # attribution
LICENSE                      # MIT
.github/workflows/tests.yml  # automatic smoke tests on GitHub

```

## Security and responsible use

- Not financial, legal, tax, or investing advice. AI models can be wrong. Validate important facts against article sources and official data.
- Public URLs are fetched with safety checks in `econolens_core.py`. Public article access does not bypass paywalls.

**Live app:** https://econolens-ai-economics-news.streamlit.app/  
**Source:** https://github.com/qxiao2ub/EconoLens-AI-Economics-News-App

## October 2026 Streamlit module-loading bug fix

The deployed app previously used `st.dataframe` and `st.bar_chart`. Under some Streamlit Cloud/browser conditions, the frontend can fail to fetch dynamically loaded `DataFrame...js` or `ArrowVegaLiteChart...js` files. This causes red TypeError panels even when the Python economic analysis completed.

This version eliminates those **two specific frontend components** throughout `app.py`:

- Economic themes, next-word suggestions, economic terms, readability, evidence phrases, and feedback use responsive, HTML-escaped tables rendered via `st.markdown`.
- The topic score chart uses CSS-based horizontal bars with explicit percentages; no Altair/Vega-Lite frontend chunk is required. Scores are relative model weights, not calibrated probabilities.
- `streamlit==1.66.1` is pinned for repeatable deployments.
- Economics pipeline, profile personalization, download exports, author/advisor credits, and no-visitor-counter layout are unchanged.

**After uploading/redeploying:** In your browser press Ctrl+Shift+R (Windows) or try a private window to clear cached Streamlit JS bundles. A failure to download a dynamic JS module can still occur for other widgets due to transient network/CDN/browser conditions; changing the Python code cannot absolutely prevent all such failures. See `BUGFIX_NOTES.md` for step-by-step browser and deployment troubleshooting.
