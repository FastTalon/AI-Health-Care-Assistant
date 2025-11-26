# Agentic Healthcare Assistant - Option C + WHO Indicator Search Engine

import os
import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import time
import streamlit as st
import requests
import numpy as np
import pandas as pd
from pypdf import PdfReader
from docx import Document

try:
    import openai
except ImportError:
    openai = None

# =============================
# PubMed + WHO Integration
# =============================

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
WHO_BASE = "https://ghoapi.azureedge.net/api/"

def pubmed_search(query, max_results=5):
    try:
        esearch_url = NCBI_BASE + "esearch.fcgi"
        params = {"db":"pubmed", "term":query, "retmax":max_results, "retmode":"json"}
        r = requests.get(esearch_url, params=params, timeout=15)
        data = r.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])
        if not pmids:
            return []
        esummary_url = NCBI_BASE + "esummary.fcgi"
        params = {"db":"pubmed","id":",".join(pmids),"retmode":"json"}
        r = requests.get(esummary_url, params=params, timeout=15)
        summaries = r.json().get("result", {})
        results = []
        for pmid in pmids:
            info = summaries.get(pmid, {})
            if info:
                results.append({
                    "pmid": pmid,
                    "title": info.get("title"),
                    "authors": [a.get("name") for a in info.get("authors", [])],
                    "journal": info.get("fulljournalname"),
                    "pubdate": info.get("pubdate"),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
        return results
    except Exception as e:
        return [{"error": str(e)}]

def who_search(indicator):
    try:
        r = requests.get(WHO_BASE + indicator, timeout=15)
        if r.status_code != 200:
            return {"error": f"WHO API returned status {r.status_code}. Check indicator code."}
        return r.json().get("value", [])
    except Exception as e:
        return {"error": str(e)}

# New: WHO Indicator List Fetcher
def who_list_indicators():
    try:
        url = WHO_BASE + "Indicator"
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            return []
        return r.json().get("value", [])
    except:
        return []

# =============================
# Placeholder render functions
# =============================

def render_chat_tab():
    st.write("Chat functionality from original app goes here.")

def render_appointments_tab():
    st.write("Appointments functionality from original app goes here.")

def render_files_tab():
    st.write("File search/upload functionality from original app goes here.")

def render_metrics_tab():
    st.write("LLMOps metrics go here.")

def render_debug_tab():
    st.write("Debug trace and logs go here.")

# =========================================================
# MAIN APPLICATION
# =========================================================

def main():
    st.set_page_config(page_title="Healthcare App", layout="wide")
    st.title("🏥 Agentic Healthcare Assistant - Enhanced WHO Search")

    tab_chat, tab_appts, tab_files, tab_pubmed, tab_who, tab_metrics, tab_debug = st.tabs(
        ["💬 Chat","📅 Appointments","📂 Files","🔎 PubMed","🌍 WHO Search","📊 Metrics","🛠 Debug"]
    )

    with tab_chat:
        render_chat_tab()

    with tab_appts:
        render_appointments_tab()

    with tab_files:
        render_files_tab()

    with tab_pubmed:
        st.subheader("📚 PubMed Search")
        query = st.text_input("Enter topic:")
        if st.button("Search PubMed"):
            st.json(pubmed_search(query))

    # WHO SEARCH ENGINE
    with tab_who:
        st.subheader("🌍 WHO Indicator Search Engine")

        st.markdown("### 🔎 Step 1: Search WHO Indicators by Keyword")
        keyword = st.text_input("Enter keyword (e.g., 'diabetes', 'life expectancy', 'mortality'):").lower()

        indicators = who_list_indicators()

        if keyword:
            filtered = [i for i in indicators if keyword in i.get("IndicatorName","").lower()]

            if filtered:
                st.write(f"Found {len(filtered)} matching indicators:")
                indicator_map = {f"{i['IndicatorCode']} - {i['IndicatorName']}": i['IndicatorCode'] for i in filtered}
                choice = st.selectbox("Select Indicator", list(indicator_map.keys()))
                selected_code = indicator_map.get(choice)

                st.markdown("### 📊 Step 2: Retrieve WHO Data")
                if st.button("Get WHO Data"):
                    st.json(who_search(selected_code))
            else:
                st.warning("No indicators found. Try another keyword.")
        else:
            st.info("Enter a keyword to begin WHO Indicator Search.")

    with tab_metrics:
        render_metrics_tab()

    with tab_debug:
        render_debug_tab()

if __name__ == "__main__":
    main()
