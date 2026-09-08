"""A sample-only sales dashboard. Run with: python -m streamlit run app.py."""
from datetime import date
from io import StringIO
from pathlib import Path

import pandas as pd
import streamlit as st

SAMPLE = Path(__file__).with_name("sample_data.csv")
STATUSES = ["New", "Contacted", "Appointment", "Proposal", "Closed Won", "Closed Lost"]
COLUMNS = ["lead_id", "lead_name", "territory", "lead_source", "status", "created_date",
           "appointment_date", "closed_date", "next_follow_up", "revenue"]
DATES = ["created_date", "appointment_date", "closed_date", "next_follow_up"]


def load_data(source):
    """Validate the entire file before showing any totals; never save uploads."""
    try:
        frame = pd.read_csv(source, dtype=str, keep_default_na=False)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as error:
        raise ValueError("Use a UTF-8 CSV with the sample file's column headers.") from error
    if set(frame.columns) != set(COLUMNS):
        raise ValueError("Columns must match sample_data.csv exactly: " + ", ".join(COLUMNS))
    if frame.empty or len(frame) > 10000:
        raise ValueError("Provide between 1 and 10,000 fictional leads.")
    frame = frame[COLUMNS].apply(lambda column: column.str.strip())
    for column in COLUMNS[:6]:
        if frame[column].eq("").any():
            raise ValueError(f"{column} cannot be blank.")
    if frame.lead_id.duplicated().any():
        raise ValueError("Each lead_id must be unique.")
    if not frame.status.isin(STATUSES).all():
        raise ValueError("Status must be one of: " + ", ".join(STATUSES))
    for column in DATES:
        raw = frame[column]
        parsed = pd.to_datetime(raw, format="%Y-%m-%d", errors="coerce")
        if (raw.ne("") & (~raw.str.fullmatch(r"\d{4}-\d{2}-\d{2}") | parsed.isna())).any():
            raise ValueError(f"{column} must use valid YYYY-MM-DD dates or be blank.")
        frame[column] = parsed
    revenue = pd.to_numeric(frame.revenue, errors="coerce")
    if (revenue.isna() | ~revenue.between(0, 1000000000)).any():
        raise ValueError("Revenue must be a finite number from 0 to 1,000,000,000, without $ or commas.")
    frame["revenue"] = revenue
    closed = frame.status.isin(["Closed Won", "Closed Lost"])
    if (closed & frame.closed_date.isna()).any() or (~closed & frame.closed_date.notna()).any():
        raise ValueError("Closed leads need closed_date; open leads must leave it blank.")
    if (frame.status.eq("Appointment") & frame.appointment_date.isna()).any():
        raise ValueError("Appointment status needs appointment_date.")
    if (frame.status.ne("Closed Won") & frame.revenue.ne(0)).any():
        raise ValueError("Only Closed Won leads may have revenue; use 0 for other statuses.")
    for column in DATES[1:]:
        if (frame[column] < frame.created_date).any():
            raise ValueError(f"{column} cannot be before created_date.")
    return frame


def add_flags(frame, report_date):
    """Flag open leads relative to the selected date, without changing the input."""
    frame = frame.copy()
    today = pd.Timestamp(report_date)
    active = ~frame.status.isin(["Closed Won", "Closed Lost"])
    frame["follow_up_flag"] = "Closed"
    frame.loc[active, "follow_up_flag"] = "Upcoming"
    frame.loc[active & frame.next_follow_up.isna(), "follow_up_flag"] = "Missing date"
    frame.loc[active & frame.next_follow_up.lt(today), "follow_up_flag"] = "Overdue — follow up"
    frame.loc[active & frame.next_follow_up.eq(today), "follow_up_flag"] = "Due today"
    return frame


def summarize(frame, report_date):
    won = frame.status.eq("Closed Won")
    lost = frame.status.eq("Closed Lost")
    decided = int(won.sum() + lost.sum())
    day = pd.Timestamp(report_date)
    return dict(leads=len(frame), appointments=int(frame.appointment_date.notna().sum()),
                won=int(won.sum()), close_rate=float(won.sum() / decided) if decided else None,
                revenue=float(frame.loc[won, "revenue"].sum()),
                new_today=int(frame.created_date.eq(day).sum()),
                appointments_today=int(frame.appointment_date.eq(day).sum()),
                won_today=int((won & frame.closed_date.eq(day)).sum()),
                revenue_today=float(frame.loc[won & frame.closed_date.eq(day), "revenue"].sum()))


def main():
    st.set_page_config(page_title="Mason's Territory Dashboard", page_icon="📊", layout="wide")
    st.title("Mason's Sales Territory Dashboard")
    st.caption("Mason’s portfolio project · Python + Streamlit · Fictional data only")
    with st.sidebar:
        st.header("Your daily view")
        st.info("Use sample or made-up data only. Never upload real customer or company records.")
        st.download_button("Download sample CSV", SAMPLE.read_bytes(), "sample_data.csv", "text/csv")
        confirmed = st.checkbox("My upload contains fictional data only")
        upload = st.file_uploader("Upload a sample CSV (max 2 MB)", type=["csv"], disabled=not confirmed)
    try:
        if confirmed and upload is not None:
            if upload.size > 2 * 1024 * 1024:
                raise ValueError("File is too large. Maximum: 2 MB.")
            frame = load_data(StringIO(upload.getvalue().decode("utf-8-sig")))
            default_date = date.today()
            label = "Uploaded fictional data"
        else:
            frame = load_data(SAMPLE)
            default_date = date(2026, 9, 7)
            label = "Built-in sample data"
    except (ValueError, UnicodeDecodeError) as error:
        st.error(f"Cannot load this CSV: {error}")
        st.stop()
    with st.sidebar:
        report_date = st.date_input("Report date", value=default_date)
        territories = st.multiselect("Territories", sorted(frame.territory.unique()), default=sorted(frame.territory.unique()))
        sources = st.multiselect("Lead sources", sorted(frame.lead_source.unique()), default=sorted(frame.lead_source.unique()))
        statuses = st.multiselect("Lead statuses", STATUSES, default=STATUSES)
        query = st.text_input("Search lead name or ID", placeholder="Example: Demo Lead 01")
        follow_only = st.checkbox("Only leads needing follow-up")
    frame = add_flags(frame, report_date)
    view = frame[frame.territory.isin(territories) & frame.lead_source.isin(sources) & frame.status.isin(statuses)]
    if query.strip():
        view = view[view.lead_name.str.contains(query.strip(), case=False, regex=False) |
                    view.lead_id.str.contains(query.strip(), case=False, regex=False)]
    if follow_only:
        view = view[view.follow_up_flag.isin(["Overdue — follow up", "Due today", "Missing date"])]
    st.caption(f"{label} · Showing {len(view)} of {len(frame)} leads · All summaries follow the filters.")
    st.caption("Report date controls daily activity and follow-up flags. Totals use current CSV statuses; this is not a historical snapshot.")
    if view.empty:
        st.info("No leads match. Clear search or select more filters.")
    metrics = summarize(view, report_date)
    columns = st.columns(5)
    for column, title, value in zip(columns, ["Leads", "Appointments recorded", "Closed won jobs", "Close rate", "Won revenue"],
                                   [metrics["leads"], metrics["appointments"], metrics["won"],
                                    f'{metrics["close_rate"]:.1%}' if metrics["close_rate"] is not None else "N/A",
                                    f'${metrics["revenue"]:,.2f}']):
        column.metric(title, value)
    st.caption("Close rate = won ÷ (won + lost). Appointments = leads with an appointment date, including past appointments. Revenue in USD.")
    st.subheader(f"Daily summary · {report_date:%B %d, %Y}")
    st.write(f'{metrics["new_today"]} new leads · {metrics["appointments_today"]} appointments · '
             f'{metrics["won_today"]} jobs won · ${metrics["revenue_today"]:,.2f} revenue closed on this date.')
    flags = view.follow_up_flag.value_counts()
    st.write(f'Follow-up: {flags.get("Overdue — follow up", 0)} overdue - follow up · {flags.get("Due today", 0)} due today · '
             f'{flags.get("Missing date", 0)} open leads missing a follow-up date.')
    left, right = st.columns(2)
    with left:
        st.subheader("Lead status summary")
        st.bar_chart(view.status.value_counts().reindex(STATUSES, fill_value=0).rename("Leads"))
    with right:
        st.subheader("Revenue by lead source")
        revenue = view[view.status.eq("Closed Won")].groupby("lead_source").revenue.sum()
        revenue = revenue.reindex(sorted(view.lead_source.unique()), fill_value=0)
        st.bar_chart(revenue.rename("Revenue (USD)"))
    st.subheader("Follow-up queue")
    due = view[view.follow_up_flag.isin(["Overdue — follow up", "Due today", "Missing date"])].sort_values("next_follow_up", na_position="last")
    if due.empty:
        st.success("No follow-ups need attention in this view.")
    else:
        st.dataframe(due[["lead_id", "lead_name", "status", "next_follow_up", "follow_up_flag"]], hide_index=True)
    st.subheader("Lead details")
    st.dataframe(view, hide_index=True)
    with st.expander("How this project works"):
        st.write("Python reads and validates the CSV. pandas filters rows and calculates totals. Streamlit turns those results into this page. Uploads are processed in memory and are not saved by this app.")


if __name__ == "__main__":
    main()
