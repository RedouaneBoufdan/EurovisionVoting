#!/usr/bin/env bash
set -e
python pipeline.py --votes 100000 --duration 30
streamlit run dashboard.py
