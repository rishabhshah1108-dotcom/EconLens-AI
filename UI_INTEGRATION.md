# Visual UI integration notes

The supplied `commcalc-source.zip` is a **commission payout management** SaaS interface, not an EconLens AI interface. Its React/TanStack routes and Supabase calls are not used, since they require a different backend and do not implement the economics pipeline. The design was ported and adapted into Streamlit rather than embedding an unrelated nonworking frontend.

## Source → adapted EconLens mapping

| Supplied UI element | Implemented in EconLens Streamlit |
| --- | --- |
| `src/styles.css` colors #002333, #159A9C, #DEEFE7, #F6F8FA | `.streamlit/config.toml` and dashboard CSS |
| `src/assets/hero-bg.jpg` | `assets/hero-bg.jpg` in the economics home-page hero |
| `src/routes/index.tsx` landing hero, cards, process steps | `Overview` page with hero, real feature cards and workflow |
| `src/components/layout/AppLayout.tsx` left navigation | Shared Streamlit sidebar with eight economics workspaces |
| CommCalc deals, commission rates, sales reps, quotas | **Not copied**: those business-domain workflows are not part of economics news analysis |

The complete original economics pipeline from `econolens_core.py` remains intact. All economic functionality is accessible in the redesigned navigation. The visitor counter was removed in the previous requested revision. The design is mobile-friendly and retains a safe top offset below Streamlit's toolbar so header content is not hidden.

**Author:** Rishabh Shah  
**Advisor:** Dr. Qingyang Xiao

## Frontend render stability patch (October 2026)

All `st.dataframe` displays have been converted to responsive escaped HTML tables, and the topic `st.bar_chart` is rendered as an accessible CSS-only horizontal bar visualization. These components no longer request Streamlit DataFrame or ArrowVegaLiteChart dynamic JavaScript bundles. See `BUGFIX_NOTES.md`.
