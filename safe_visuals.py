"""CSS-only economics visualizations for reliable Streamlit Cloud rendering.

Does not use Streamlit's lazily loaded DataFrame / ArrowVegaLiteChart JS bundles.
All dynamic content is escaped before inclusion in Streamlit markdown HTML.

Student author: Rishabh Shah; Advisor: Dr. Qingyang Xiao.
"""
from __future__ import annotations

import html
import math
from typing import Mapping, Any

import pandas as pd


def html_table(data: Any, *, empty_message: str = "No rows to display.") -> str:
    """Render a readable, scrollable, *escaped* HTML table from rows or a DataFrame.

    This avoids the DataFrame frontend component entirely. It is display-only,
    retaining all columns and rows without requiring Arrow JS chunks.
    """
    if isinstance(data, pd.DataFrame):
        frame = data.copy()
    else:
        frame = pd.DataFrame(data)
    if frame.empty or len(frame.columns) == 0:
        return f'<div class="e-empty">{html.escape(empty_message, quote=True)}</div>'
    frame = frame.fillna("")
    table_markup = frame.to_html(
        index=False,
        border=0,
        classes=["e-native-table"],
        escape=True,
        na_rep="",
        justify="left",
    )
    return '<div class="e-table-container" role="region" aria-label="Data table" tabindex="0">' + table_markup + '</div>'


def topic_bars(topic_scores: Mapping[str, Any]) -> str:
    """Render topic weights as accessible, CSS-only horizontal bars.

    Width is relative to the largest score, while text shows each score's share
    of the sum of all nonnegative model scores. Neither measure is a confidence
    level or guaranteed calibrated probability.
    """
    parsed: list[tuple[str, float]] = []
    for topic, raw in topic_scores.items():
        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue
        if math.isfinite(value) and value >= 0:
            parsed.append((str(topic), value))
    parsed.sort(key=lambda item: item[1], reverse=True)
    if not parsed:
        return '<div class="e-empty">No economics topic scores are available.</div>'
    highest = max(value for _, value in parsed)
    total = sum(value for _, value in parsed)
    output = [
        '<section class="e-topic-visual" aria-label="Economic topic score comparison">',
        '<p class="e-topic-intro">Topic-model signal distribution. Longer bars indicate larger weights in this article; these are not calibrated probabilities.</p>',
    ]
    for topic, score in parsed:
        width = 100 * score / highest if highest > 0 else 0
        percent = 100 * score / total if total > 0 else 0
        label = html.escape(topic, quote=True)
        output.append(
            '<div class="e-topic-row">'
            f'<div class="e-topic-label"><span>{label}</span><strong>{percent:.1f}%</strong></div>'
            '<div class="e-topic-track" aria-hidden="true">'
            f'<div class="e-topic-bar" style="width:{width:.2f}%"></div>'
            '</div></div>'
        )
    output.append('</section>')
    return "\n".join(output)
