"""
dashboard.py — Streamlit dashboard with recruiter branding
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from pipeline import run_pipeline, load_meta

st.set_page_config(page_title="Manu's Job Search Agent", page_icon="🔍", layout="wide")

CSV_PATH = "./data/jobs.csv"

st.markdown("""
<style>
.big-title { font-size: 2.8rem; font-weight: 900; color: #17252A; letter-spacing: -1px; }
.tag { background: #2B7A78; color: #DEF2F1; padding: 2px 8px; border-radius: 12px; font-size: 0.72rem; margin: 2px; display: inline-block; }
.recruiter-box { background: linear-gradient(135deg, #17252A, #2B7A78); border-radius: 12px; padding: 20px; color: white; margin-bottom: 20px; border-left: 5px solid #3AAFA9; }
.metric-num { font-size: 1.4rem; font-weight: 800; color: #3AAFA9; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_jobs():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame()


def show_recruiter_message(df):
    total_jobs = len(df) if not df.empty else 0
    total_keywords = 60
    total_categories = df["category"].nunique() if not df.empty and "category" in df.columns else 9

    st.markdown(f"""
<div class="recruiter-box">
<p>Hello Recruiter! 👋</p>
<p>I'm <strong>Manu Sharma</strong>.<br>
If you're reading this, I'm sure my resume caught your eye.<br>
Thank you for taking the time to review my job application.</p>

<p>And this is exactly what I bring to the table —<br>
Along with data analysis, I can present it in a way that's easy to understand.<br>
I know how to engineer AI Agents the way they can benefit the best.</p>

<p>I believe in numbers, results and most importantly — presenting them neatly.</p>
<p><strong>So here they are:</strong></p>

<p>
🔍 <span class="metric-num">{total_jobs}+</span> jobs tracked<br>
🌐 <span class="metric-num">3</span> sources scraped via REST APIs<br>
⏰ Refreshes every <span class="metric-num">2</span> hours via Task Scheduler<br>
🧠 <span class="metric-num">{total_keywords}+</span> NLP keywords across <span class="metric-num">{total_categories}</span> categories<br>
📊 Fully automated ETL pipeline in Python
</p>

<p>Honestly I am the best match —<br>
if you're looking for someone who has the motivation to try new approaches<br>
and tech everyday to work around with data and engineer it<br>
the way it can best drive the team's effort to give business solutions.</p>

<p>— <strong>Manu Sharma</strong></p>
</div>
""", unsafe_allow_html=True)


def main():
    st.markdown('<div class="big-title">🔍 Autonomous Job Search Agent</div>', unsafe_allow_html=True)
    st.caption("Multi-source Data job tracker — RemoteOK · Adzuna · The Muse · NLP Classification · 2hr ETL Pipeline")

    df = load_jobs()

    # Auto-run pipeline if no data
    if df.empty:
        st.warning("No data yet. Running pipeline...")
        with st.spinner("Scraping all sources..."):
            run_pipeline()
        st.cache_data.clear()
        df = load_jobs()

    # ── Sidebar ──
    st.sidebar.markdown("## 🔍 Filters")

    if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
        with st.spinner("Running pipeline..."):
            stats = run_pipeline()
        st.sidebar.success(f"✅ {stats.get('new_jobs_added', 0)} new jobs added!")
        st.cache_data.clear()
        st.rerun()

    meta = load_meta()
    if meta.get("last_run"):
        st.sidebar.caption(f"Last refresh: {meta['last_run']}")

    st.sidebar.divider()

    # Source filter
    source_opts = ["All"] + sorted(df["source"].dropna().unique().tolist()) if not df.empty else ["All"]
    sel_source = st.sidebar.selectbox("Source", source_opts)

    categories = ["All"] + sorted(df["category"].dropna().unique().tolist()) if not df.empty else ["All"]
    sel_cat = st.sidebar.selectbox("Category", categories)

    seniority_opts = ["All"] + sorted(df["seniority"].dropna().unique().tolist()) if not df.empty else ["All"]
    sel_sen = st.sidebar.selectbox("Seniority", seniority_opts)

    job_type_opts = ["All"] + sorted(df["job_type"].dropna().unique().tolist()) if not df.empty and "job_type" in df.columns else ["All"]
    sel_job_type = st.sidebar.selectbox("Job Type", job_type_opts)

    location_opts = ["All"] + sorted(df["location_type"].dropna().unique().tolist()) if not df.empty and "location_type" in df.columns else ["All"]
    sel_location = st.sidebar.selectbox("Location Type", location_opts)

    keyword = st.sidebar.text_input("Search", placeholder="e.g. pytorch, sql...")
    min_rel = st.sidebar.slider("Min relevance", 0.0, 1.0, 0.0, 0.1)
    salary_only = st.sidebar.checkbox("Salary listings only")

    # ── Apply filters ──
    filtered = df.copy() if not df.empty else df

    if not filtered.empty:
        if sel_source != "All":
            filtered = filtered[filtered["source"] == sel_source]
        if sel_cat != "All":
            filtered = filtered[filtered["category"] == sel_cat]
        if sel_sen != "All":
            filtered = filtered[filtered["seniority"] == sel_sen]
        if "job_type" in filtered.columns and sel_job_type != "All":
            filtered = filtered[filtered["job_type"] == sel_job_type]
        if "location_type" in filtered.columns and sel_location != "All":
            filtered = filtered[filtered["location_type"] == sel_location]
        if keyword:
            kw = keyword.lower()
            filtered = filtered[
                filtered["title"].str.lower().str.contains(kw, na=False) |
                filtered["tags"].str.lower().str.contains(kw, na=False) |
                filtered["description"].str.lower().str.contains(kw, na=False)
            ]
        if min_rel > 0:
            filtered = filtered[filtered["relevance_score"] >= min_rel]
        if salary_only:
            filtered = filtered[filtered["salary"] != "Not specified"]

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs(["👋 About", "📋 Listings", "📊 Analytics", "📥 Export"])

    with tab1:
        show_recruiter_message(df)

    with tab2:
        # Metrics
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Jobs", len(df))
        c2.metric("Filtered", len(filtered))
        c3.metric("Companies", filtered["company"].nunique() if not filtered.empty else 0)
        c4.metric("With Salary", len(filtered[filtered["salary"] != "Not specified"]) if not filtered.empty else 0)
        c5.metric("Sources", filtered["source"].nunique() if not filtered.empty and "source" in filtered.columns else 0)

        st.divider()

        if filtered.empty:
            st.info("No jobs match your filters.")
        else:
            st.markdown(f"**{len(filtered)} jobs found**")
            for _, job in filtered.iterrows():
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{job.get('title', '')}** — {job.get('company', '')}")
                        # Source badge
                        st.caption(f"📡 {job.get('source', 'Unknown')} · 📅 {job.get('date_posted', 'N/A')}")
                        tags = str(job.get("tags", ""))
                        if tags and tags != "nan":
                            tag_html = " ".join([f'<span class="tag">{t.strip()}</span>' for t in tags.split(",")[:6] if t.strip()])
                            st.markdown(tag_html, unsafe_allow_html=True)
                        desc = str(job.get("description", ""))
                        if desc and desc != "nan":
                            st.caption(desc[:200] + "...")
                    with col2:
                        st.markdown(f"**{job.get('category', '')}**")
                        st.caption(job.get('seniority', ''))
                        st.caption(f"🏢 {job.get('job_type', 'Full-Time')}")
                        st.caption(f"📍 {job.get('location_type', 'Remote')}")
                        st.caption(f"💰 {job.get('salary', 'N/A')}")
                        st.caption(f"⭐ {float(job.get('relevance_score', 0)):.0%}")
                        if job.get("url"):
                            st.markdown(f"[Apply →]({job['url']})")
                    st.divider()

    with tab3:
        if not filtered.empty:
            col1, col2 = st.columns(2)
            with col1:
                cat_counts = filtered["category"].value_counts().reset_index()
                cat_counts.columns = ["Category", "Count"]
                fig = px.bar(cat_counts, x="Category", y="Count", title="Jobs by Category",
                           color="Count", color_continuous_scale="Viridis")
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=300)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                sen_counts = filtered["seniority"].value_counts().reset_index()
                sen_counts.columns = ["Seniority", "Count"]
                fig2 = px.pie(sen_counts, values="Count", names="Seniority", title="Seniority Distribution")
                fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=300)
                st.plotly_chart(fig2, use_container_width=True)

            # Source breakdown
            if "source" in filtered.columns:
                src_counts = filtered["source"].value_counts().reset_index()
                src_counts.columns = ["Source", "Count"]
                fig3 = px.bar(src_counts, x="Source", y="Count", title="Jobs by Source",
                            color="Count", color_continuous_scale="Plasma")
                fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=300)
                st.plotly_chart(fig3, use_container_width=True)

            st.markdown("### Top Companies")
            top = filtered["company"].value_counts().head(10).reset_index()
            top.columns = ["Company", "Listings"]
            st.dataframe(top, use_container_width=True, hide_index=True)

    with tab4:
        if not filtered.empty:
            st.download_button(
                "⬇️ Download as CSV",
                data=filtered.to_csv(index=False),
                file_name=f"ds_jobs_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.dataframe(filtered, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
