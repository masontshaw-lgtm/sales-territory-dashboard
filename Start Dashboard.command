#!/bin/zsh
# Start from this file's folder, even when opened from Finder.
cd -- "${0:A:h}"
if [[ ! -x .venv/bin/python ]]; then
  print 'First complete the environment setup in README.md.'
  read '?Press Enter to close.'
  exit 1
fi
print 'Starting your sample dashboard. Keep this Terminal window open.'
print 'To stop the dashboard, press Control+C.'
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false --server.port 8501
