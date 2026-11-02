"""Regression tests for two Streamlit frontend module-loading issues."""
from __future__ import annotations

import ast
import math
import unittest
from pathlib import Path

import pandas as pd

from safe_visuals import html_table, topic_bars
from econolens_core import EconomicsNewsPipeline, ReaderProfile

ROOT = Path(__file__).resolve().parents[1]


class SafeVisualTests(unittest.TestCase):
    def test_table_escapes_user_article_content(self):
        rows = [{"topic": '<script>alert("x")</script>', "score": 0.17}]
        rendered = html_table(rows)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertNotIn('<script>', rendered)
        self.assertIn('e-native-table', rendered)
        self.assertIn('0.17', rendered)

    def test_empty_html_table(self):
        self.assertIn('No rows', html_table([]))

    def test_data_frame_tables_include_all_columns(self):
        frame = pd.DataFrame([{"term": "interest rate", "definition": "cost of borrowing", "count": 2}])
        rendered = html_table(frame)
        self.assertIn('definition', rendered)
        self.assertIn('interest rate', rendered)
        self.assertIn('count', rendered)

    def test_topic_bars_display_and_escape(self):
        rendered = topic_bars({'<img src=x onerror=alert(1)>': 0.75, 'Housing': 0.25})
        self.assertIn('&lt;img', rendered)
        self.assertNotIn('<img', rendered)
        self.assertIn('75.0%', rendered)
        self.assertIn('25.0%', rendered)
        self.assertIn('width:100.00%', rendered)
        self.assertIn('width:33.33%', rendered)
        self.assertNotIn('<script', rendered)

    def test_zero_invalid_values(self):
        self.assertIn('0.0%', topic_bars({'Jobs': 0.0, 'Housing': 0.0, 'invalid': math.inf}))
        self.assertIn('No economics topic scores', topic_bars({'bad': -1.0}))

    def test_no_dataframe_or_altair_chart_calls_anywhere_in_production_app(self):
        tree = ast.parse((ROOT / 'app.py').read_text(encoding='utf8'))
        prohibited = {'dataframe', 'data_editor', 'table', 'bar_chart', 'altair_chart', 'vega_lite_chart'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'st':
                    self.assertNotIn(node.func.attr, prohibited)

    def test_real_pipeline_results_render(self):
        engine = EconomicsNewsPipeline(feedback_path=None)
        result = engine.analyze(
            (ROOT / 'sample_article.txt').read_text(encoding='utf8'),
            profile=ReaderProfile(), use_neural=False,
        )
        hierarchy = result['hierarchy']
        theme_table = html_table(hierarchy['Level 3 - Main economic themes'])
        self.assertIn('Inflation and prices', theme_table)
        self.assertIn('e-native-table', theme_table)
        self.assertIn('topic', theme_table)
        graph = topic_bars(result['topic_scores'])
        self.assertIn('e-topic-track', graph)
        self.assertIn('Inflation and prices', graph)
        for key in ['key_phrases', 'terms', 'readability']:
            self.assertIn('e-native-table', html_table(result[key]))
        self.assertIn('e-native-table', html_table(engine.feedback.status()))


if __name__ == '__main__':
    unittest.main()
