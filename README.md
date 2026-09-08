# Sales Territory Dashboard

A Python dashboard that helps a fictional sales representative see lead progress, revenue, and follow-ups in one place. Mason’s first portfolio project connects familiar sales questions to practical software development.

**Sample data only:** every record is invented. Do not upload real ADT, employer, customer, or confidential information. This is a learning project, not an approved business system.

## What it does

- Loads 16 fictional leads automatically, or accepts a sample CSV upload.
- Summarizes lead statuses, appointments, won jobs, close rate, and revenue.
- Charts won revenue by lead source.
- Filters by territory, lead source, status, and literal name/ID search.
- Flags overdue follow-ups, follow-ups due today, and missing follow-up dates.
- Shows new leads, appointments, won jobs, and won revenue for a selected day.
- Rejects malformed data with readable errors instead of showing misleading totals.

## Run on your Mac

If the environment is already installed, double-click `Start Dashboard.command` in Finder. Keep its Terminal window open while using the dashboard. If the browser says connection refused, restart with this launcher, then reload the page. Closing Terminal or stopping the app makes the local address unavailable.

Use Python 3.10–3.13 (this project was developed with Python 3.12) and Git. Open Terminal in this project folder, then:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

The first command creates a separate package environment for this project. The second activates it. The third installs the two libraries listed in `requirements.txt`. The last starts the dashboard on your Mac.

Open http://localhost:8501 in your browser. To stop the app, press **Control+C** in Terminal. Next time, you only need to activate the environment and run the last command. If port 8501 is occupied, append `--server.port 8502` and open that port instead.

If your `python3 --version` reports 3.9, select an installed newer Python executable for the first command (for example, `python3.12`). Do not reuse a virtual environment built with an unsupported Python version.

## Try it in five minutes

1. Leave the report date at **September 7, 2026**. You should see 16 leads, 10 appointments recorded, 4 won jobs, 66.7% close rate, and $8,900 won revenue.
2. Read the daily summary: 2 new leads, 2 appointments, 2 won jobs, and $5,600 closed that day.
3. Select **Only leads needing follow-up**. Seven fictional leads need attention.
4. Clear that checkbox and search `DEMO-001`. Only one lead should remain.
5. Download the sample CSV. Make a copy outside the repository, change a fictional territory, confirm that the upload is fictional, and upload the copy.
6. Try an invalid status in your copy. Explain why validation catches it.

## How the numbers work

All totals, charts, the daily summary, and tables reflect the current filters.

| Metric | Definition |
| --- | --- |
| Leads | Number of visible rows; one row per unique lead |
| Appointments recorded | Leads with an appointment date, including past appointments |
| Closed won jobs | Leads whose current status is `Closed Won` |
| Close rate | Won / (won + lost); `N/A` if no leads are decided |
| Won revenue | Sum of revenue on `Closed Won` rows, in USD |
| Daily activity | Match created, appointment, or closed date to the report date |
| Follow-up flags | Open leads: before report date = overdue, same day = due today, blank = missing date |

The report date affects daily activity and follow-up flags only. CSV statuses represent the current pipeline, not a reconstructed historical snapshot. An appointment date records one appointment per lead; there is no appointment history or cancellation tracking. Closed leads never enter the follow-up queue.

## CSV contract

Use the exact headers in `sample_data.csv`. Every row must include all ten fields, with optional values left blank.

| Column | Rule |
| --- | --- |
| `lead_id` | Required unique fictional identifier |
| `lead_name` | Required fictional label, never a real person |
| `territory` | Required fictional territory label |
| `lead_source` | Required source label, such as Referral or Website |
| `status` | New, Contacted, Appointment, Proposal, Closed Won, or Closed Lost |
| `created_date` | Required date in YYYY-MM-DD format |
| `appointment_date` | Optional date; required for Appointment status |
| `closed_date` | Required for won/lost; blank for open leads |
| `next_follow_up` | Optional date; blank on open leads triggers Missing date |
| `revenue` | Required number from 0 to 1 billion; zero except on won leads; no currency signs or separators |

Dates must be valid and cannot precede creation. Files must be UTF-8, at most 2 MB and 10,000 rows. Extra or missing columns are rejected. Uploads are processed in memory by the local Streamlit process; the app does not write them to disk or connect to a CRM. The fictional-data checkbox is a reminder, not a detector of confidential data. Additional CSV files are excluded from Git by default.

## Project structure

```text
sales-territory-dashboard/
├── app.py                    # Validation, calculations, and dashboard UI
├── sample_data.csv           # Invented leads for a repeatable demo
├── requirements.txt          # Direct package versions
├── README.md                 # Setup, definitions, and learning guide
├── tests/test_dashboard.py   # Business rules and UI interaction checks
└── .gitignore                # Keeps environments and extra CSVs out of Git
```

`load_data()` reads and validates rows. `add_flags()` assigns follow-up labels. `summarize()` calculates business metrics. `main()` builds the page. Keeping calculations in functions lets us test them independently from the screen.

Python is the language; pandas works with tables; Streamlit builds the interface. Git stores local checkpoints. GitHub hosts a copy online for sharing and collaboration.

## Verify changes

With your environment active:

```bash
python -m unittest discover -s tests -v
```

Tests check known sample totals, follow-up boundaries, empty views, malformed uploads, and interactive searching/filtering using [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest). Automated parsing checks use in-memory CSV uploads; the browser file picker itself is a manual check using the five-minute walkthrough.

## Your first Git exercise

The repository already has local checkpoints. Initial commits use `Mason Shaw <mason-local@users.invalid>` as an explicitly local placeholder because no Git identity was configured. Before your own commit, set an identity in this repository only. Replace the email below with the exact private commit email from your GitHub email settings, if you use one.

```bash
git config user.name "Mason Shaw"
git config user.email "YOUR_GITHUB_COMMIT_EMAIL"
git log --oneline
```

Then change one fictional lead source in `sample_data.csv`, run the app and tests, and inspect your change:

```bash
git status
git diff
git add sample_data.csv
git commit -m "Update fictional lead source for dashboard practice"
git log --oneline
```

`status` lists changed files. `diff` shows the exact edits. `add` selects what goes into a checkpoint. `commit` saves it with an explanation. `log` shows the story of the project. If a test fails after you change expected data, work out why before updating its expected result.

## GitHub repository

Source code is public at [masontshaw-lgtm/sales-territory-dashboard](https://github.com/masontshaw-lgtm/sales-territory-dashboard). Git was initialized before the dashboard implementation; the history records setup, the working dashboard, the Mac launcher, and subsequent refinements.

After making and testing a local change:

```bash
git diff
git add <files-you-changed>
git commit -m "Describe the change and its purpose"
git push origin main
```

Replace `<files-you-changed>` with the specific filenames you reviewed. A commit saves a local checkpoint; a push copies committed changes to GitHub. Review files before committing and keep all data fictional. Publishing source code does not host the running app; run it locally using the instructions above.

## v1 scope and portfolio wording

Status tracking displays the current status recorded in the CSV. To change a status, edit a fictional CSV and load it again. There is no in-app lead editor, database, CRM connection, or status-change history in v1.

See [PORTFOLIO.md](PORTFOLIO.md) for a short GitHub description, a LinkedIn project entry, and a practical interview walkthrough.

## Learning milestones

1. **Python + Git now:** run the app, explain one function, make a small change, inspect the diff, and commit it yourself.
2. **GitHub next:** open an issue, make a branch, and merge a pull request for one improvement in the published repository.
3. **Basic SQL later:** store synthetic leads in SQLite and reproduce the source revenue chart with `SELECT`, `GROUP BY`, and `SUM`.
4. **APIs later:** add a local sample-data endpoint; practice HTTP, JSON, timeouts, and error handling without private credentials.
5. **HTML/CSS later:** build a small custom presentation layer and explain the styling you write.

SQL, API integration, and custom HTML/CSS are not implemented in this version. AI-assisted project creation is a starting point: hands-on changes and the ability to explain them are what make the experience yours.

A useful first explanation to practice: “The app validates a CSV, filters its rows with pandas, computes totals, and renders them in Streamlit. I can show how the close-rate calculation handles no decided leads.”
