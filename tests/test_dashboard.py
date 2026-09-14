"""Run with python -m unittest discover -s tests -v."""
import unittest
from unittest.mock import patch
import pandas as pd
import streamlit as st
from datetime import date
from io import StringIO
from pathlib import Path
from streamlit.testing.v1 import AppTest
from app import SAMPLE, add_flags, load_data, summarize


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.frame = load_data(SAMPLE)

    def test_sample_business_totals(self):
        result = summarize(self.frame, date(2026, 9, 7))
        self.assertEqual(result, dict(leads=16, appointments=10, won=4,
                         close_rate=4 / 6, revenue=8900.0, new_today=2,
                         appointments_today=2, won_today=2, revenue_today=5600.0))

    def test_flags_exclude_closed_and_distinguish_missing_dates(self):
        flags = add_flags(self.frame, date(2026, 9, 7)).set_index("lead_id").follow_up_flag
        self.assertEqual(flags["DEMO-001"], "Closed")
        self.assertEqual(flags["DEMO-005"], "Overdue — follow up")
        self.assertEqual(flags["DEMO-003"], "Due today")
        self.assertEqual(flags["DEMO-009"], "Due today")
        self.assertEqual(flags["DEMO-004"], "Upcoming")

    def test_no_decided_leads_or_empty_view(self):
        for frame in [self.frame.iloc[0:0], self.frame[self.frame.status.eq("New")]]:
            self.assertIsNone(summarize(frame, date.today())["close_rate"])

    def test_valid_upload_round_trip(self):
        self.assertEqual(len(load_data(StringIO(SAMPLE.read_text()))), 16)

    def test_invalid_uploads(self):
        raw = SAMPLE.read_text()
        for invalid in ["", "a,b\n1,2", raw.replace("DEMO-002", "DEMO-001"),
                        raw.replace("2026-09-07", "2026-02-30"),
                        raw.replace(",2400", ",inf"), raw.replace(",2400", ",-1"),
                        raw.replace("Closed Won", "Unknown"),
                        raw.replace("2026-09-07,,2400", ",,2400"),
                        raw.replace("2026-09-08,0", "2026-09-08,100")]:
            with self.subTest(invalid=invalid[:40]), self.assertRaises(ValueError):
                load_data(StringIO(invalid))

    def test_download_follows_search_and_disables_for_empty_results(self):
        # Capture the bytes sent to Streamlit while still rendering the real button.
        with patch("streamlit.download_button", wraps=st.download_button) as download:
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
            app.run(timeout=30)

            def exported_rows():
                self.assertFalse(app.exception)
                calls = [call for call in download.call_args_list
                         if call.args and call.args[0] == "Download filtered leads"]
                self.assertTrue(calls, "The filtered download button must be rendered")
                options = calls[-1].kwargs
                self.assertEqual(options["file_name"], "filtered_leads.csv")
                self.assertEqual(options["mime"], "text/csv")
                return pd.read_csv(StringIO(options["data"].decode("utf-8"))), options

            rows, options = exported_rows()
            self.assertEqual(rows.lead_id.tolist(), self.frame.lead_id.tolist())
            self.assertEqual(rows.columns.tolist(), self.frame.columns.tolist() + ["follow_up_flag"])
            self.assertFalse(options["disabled"])

            app.text_input[0].set_value("DEMO-001").run()
            rows, options = exported_rows()
            self.assertEqual(rows.lead_id.tolist(), ["DEMO-001"])
            self.assertEqual(rows.revenue.tolist(), [2400])
            self.assertEqual(rows.follow_up_flag.tolist(), ["Closed"])
            self.assertFalse(options["disabled"])

            app.text_input[0].set_value("no match").run()
            rows, options = exported_rows()
            self.assertTrue(rows.empty)
            self.assertTrue(options["disabled"])

            app.text_input[0].set_value("").run()
            rows, options = exported_rows()
            self.assertEqual(len(rows), 16)
            self.assertFalse(options["disabled"])

    def test_reset_restores_filters_and_preserves_report_date(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
        report_date = date(2026, 9, 10)
        app.date_input[0].set_value(report_date)
        app.multiselect[0].set_value([])
        app.multiselect[1].set_value(["Referral"])
        app.multiselect[2].set_value(["New"])
        app.text_input[0].set_value("no match")
        app.checkbox[1].set_value(True).run()
        self.assertEqual(app.metric[0].value, "0")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.multiselect[0].value, sorted(self.frame.territory.unique()))
        self.assertEqual(app.multiselect[1].value, sorted(self.frame.lead_source.unique()))
        self.assertEqual(app.multiselect[2].value, app.multiselect[2].options)
        self.assertEqual(app.text_input[0].value, "")
        self.assertFalse(app.checkbox[1].value)
        self.assertEqual(app.date_input[0].value, report_date)
        self.assertEqual(app.metric[0].value, "16")
        self.assertEqual(app.metric[4].value, "$8,900.00")
        # Repeating a reset must leave the restored view usable.
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "16")

    def test_interface_filters_and_empty_state(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "16")
        app.text_input[0].set_value("DEMO-001").run()
        self.assertEqual(app.metric[0].value, "1")
        self.assertEqual(app.metric[4].value, "$2,400.00")
        app.text_input[0].set_value("no match").run()
        self.assertEqual(app.metric[0].value, "0")
        self.assertEqual(app.metric[3].value, "N/A")
        self.assertFalse(app.exception)
        app.text_input[0].set_value("")
        app.checkbox[1].set_value(True).run()
        self.assertEqual(app.metric[0].value, "7")
        app.multiselect[0].set_value([]).run()
        self.assertEqual(app.metric[0].value, "0")
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
