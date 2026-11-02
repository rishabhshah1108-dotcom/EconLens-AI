# EconLens AI: DataFrame and Arrow/Vega module errors (Oct 2026)

## The two screenshots

1. Under Economic Insights > Learning hierarchy > Level 3, the red error named `DataFrame.*.js` (frontend chunk).
2. Under Economic Insights > Topics & outlook, the red error named `ArrowVegaLiteChart.*.js`.

These are client-side JavaScript bundle download/import failures. They are **not** failures of economic theme classification, data content, or the article analyzer itself. Streamlit's `st.bar_chart` uses Altair/Vega-Lite internally, so it was the relevant component in screenshot 2. Such issues are also associated with stale browser assets, version mismatches after redeployment, network interruptions, and sometimes rate limiting.

## Code changes

- Replaced `st.dataframe` with the custom pure-Python `html_table()` function in `safe_visuals.py`, which formats HTML-escaped DataFrame tables.
- Replaced `st.bar_chart` with `topic_bars()` in `safe_visuals.py`, producing styled responsive horizontal CSS bars.
- These replacement views have no frontend JavaScript dependency on Streamlit's DataFrame or ArrowVegaLiteChart components.
- Removed all other native Streamlit dataframe displays for consistency.
- Pinned Streamlit version in requirements and added visualization checks.

## Deployment steps

1. Extract ZIP and **upload the contents** of the `EconLens_AI_Streamlit` folder into the root of `qxiao2ub/EconoLens-AI-Economics-News-App` on GitHub. Do not upload a nested `EconLens_AI_Streamlit` directory as the GitHub root.
2. In Streamlit Community Cloud, select the current repository and `app.py` entrypoint. Deploy or reboot the app after code changes.
3. Hard-refresh the app: Windows Chrome/Edge: `Ctrl + Shift + R`; alternatively open an Incognito/InPrivate window.
4. Visit **Article Studio**, click **Analyze economics article**, then navigate to **Economic Insights > Learning hierarchy** and **Topics & outlook**. The economic themes table and topic bars should appear without the two named component errors.
5. Also test **Word Forecast Lab**, **Evidence & Quality** and **Feedback Studio**, which now use HTML tables as well.

## If a module-load error remains

- Open the website in a private browser window and try a different network/browser.
- Clear the site data for the `.streamlit.app` domain.
- Confirm the latest GitHub commit is actually deployed and `requirements.txt` was picked up. Reboot the Streamlit app from Manage app if necessary.
- Check browser Developer Tools > Network for failed `.js` requests (4xx/5xx or blocked). If the error still references `DataFrame.*.js` or `ArrowVegaLiteChart.*.js`, verify no older code is running.
- Other Streamlit widgets may still require dynamically loaded modules. Browser/network/Cloud asset-delivery errors cannot be eliminated with Python code alone.

**Author:** Rishabh Shah  
**Advisor:** Dr. Qingyang Xiao
