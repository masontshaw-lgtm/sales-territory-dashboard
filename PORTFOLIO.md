# Sales Territory Dashboard — portfolio copy

## Short GitHub description

Python and Streamlit portfolio dashboard using fictional leads to show pipeline status, close rate, revenue by source, filters, and follow-up priorities.

## LinkedIn project entry

**Project name:** Sales Territory Dashboard

**Dates:** September 2026–present

**Project URL:** https://github.com/masontshaw-lgtm/sales-territory-dashboard

**Description:** Built an AI-assisted learning project with Python, pandas, and Streamlit to explore sales pipeline reporting using fictional data. The working v1 includes lead status summaries, close rate, revenue by source, follow-up flags, and interactive filters and search. Added CSV validation, six automated tests, setup documentation, and a Git/GitHub commit history. Runs locally; ongoing learning focuses on understanding and extending the code.

**Skills:** Python, pandas, Streamlit, Git, GitHub, Data Validation

This entry is prepared for review and has not been posted to LinkedIn.

## Explain the project in an interview

“I used a familiar sales workflow as the basis for an AI-assisted Python learning project. It reads fictional leads from a CSV, validates them, filters them with pandas, and shows metrics and follow-ups in Streamlit. Close rate is won divided by won plus lost; if there are no decided leads, it displays N/A. Git records changes locally, and GitHub holds the public source code. The current version runs locally and does not connect to a CRM or database.”

## Walk through it in five minutes

1. **Read the data:** open sample_data.csv and identify the lead ID, source, status, dates, and revenue. Each row is one invented lead.
2. **Explain validation:** load_data() rejects invalid statuses, duplicate IDs, invalid dates, and revenue on non-won leads so bad input cannot silently distort totals.
3. **Explain a calculation:** summarize() counts four wins and two losses in the sample, giving 4 / 6 = 66.7%. Won revenue totals $8,900.
4. **Explain follow-ups:** add_flags() compares open leads' next follow-up dates with the selected report date. Closed leads stay out of the queue.
5. **Demonstrate the interface:** search DEMO-001, clear the search, and turn on the follow-up-only filter. Explain that summaries change with the visible rows.
6. **Explain verification:** six tests cover sample totals, follow-up behavior, empty results, CSV handling, and interface filters. Tests are repeatable checks, not a guarantee against every possible bug.
7. **Explain version control:** use git log --oneline to show the saved checkpoints. Use git diff before a commit to review exactly what changed.

## Boundaries to state accurately

- v1 displays CSV statuses; it does not edit or persist leads inside the app.
- The report date controls daily activity and follow-up flags, not historical pipeline snapshots.
- All records are fictional. This is a personal learning project, not employer software or professional engineering experience.
- SQL, APIs, authentication, cloud deployment, and CRM integrations are future possibilities, not implemented features.
