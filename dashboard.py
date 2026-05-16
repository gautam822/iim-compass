# dashboard.py — IIM Placement Comparison Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="IIM Placement Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM STYLING =====
st.markdown("""
<style>
    .big-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1f4e79;
        text-align: center;
        padding: 10px 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 30px;
    }
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1f4e79;
        border-left: 4px solid #667eea;
        padding-left: 12px;
        margin: 25px 0 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== COLORS =====
COLLEGE_COLORS = {
    "IIM Amritsar": "#667eea",
    "IIM Kashipur": "#f093fb",
    "NMIMS Mumbai": "#4facfe"
}

# ===== API KEY =====
def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except:
        return os.getenv("GEMINI_API_KEY")

# ===== LOAD DATA =====
@st.cache_data
def load_all_data():
    try:
        stats = pd.read_csv('placement_stats.csv')
        companies = pd.read_csv('companies.csv')
        sectors = pd.read_csv('sectors.csv')
        roles = pd.read_csv('roles.csv')
        return stats, companies, sectors, roles
    except FileNotFoundError:
        st.error("Data files not found! Please run scraper.py first.")
        st.code("python scraper.py")
        st.stop()

# ===== GEMINI AI =====
def ask_gemini(prompt):
    try:
        from google import genai
        client = genai.Client(api_key=get_api_key())
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Analysis error: {e}"

# ===== MAIN APP =====
def main():

    st.markdown(
        '<meta name="google-site-verification" content="RAPwhmaA35OeaQ8ENNNRYUncbAbr2Zdsubi7HnekLVQ" />',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="big-title">🎓 IIM Placement Intelligence</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">IIM Amritsar vs IIM Kashipur vs NMIMS Mumbai — Data-Driven Comparison</div>',
        unsafe_allow_html=True
    )

    # Load data
    df_stats, df_companies, df_sectors, df_roles = load_all_data()

    # ===== SIDEBAR =====
    with st.sidebar:
        st.title("Controls")

        selected_colleges = st.multiselect(
            "Select Colleges",
            options=df_stats['College'].tolist(),
            default=df_stats['College'].tolist()
        )

        st.divider()
        st.markdown("### Data Info")
        st.info(
            f"**Colleges:** {len(selected_colleges)} selected\n\n"
            f"**Data Year:** 2024-25\n\n"
            f"**Companies tracked:** {len(df_companies)}\n\n"
            f"**Source:** Official reports + NIRF"
        )

        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Filter data
    df_f = df_stats[df_stats['College'].isin(selected_colleges)]
    df_comp_f = df_companies[df_companies['College'].isin(selected_colleges)]
    df_sec_f = df_sectors[df_sectors['College'].isin(selected_colleges)]
    df_roles_f = df_roles[df_roles['College'].isin(selected_colleges)]

    # ===== TABS =====
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "💰 Packages",
        "🏢 Companies & Roles",
        "📈 Sectors",
        "🤖 AI Analysis"
    ])

    # ========== TAB 1: OVERVIEW ==========
    with tab1:
        st.markdown(
            '<div class="section-title">🏆 Quick Comparison at a Glance</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(len(selected_colleges))

        for i, (_, row) in enumerate(df_f.iterrows()):
            with cols[i]:
                college = str(row['College'])
                color = COLLEGE_COLORS.get(college, "#667eea")

                is_best_avg = (
                    row['Overall Average Package (LPA)'] ==
                    df_f['Overall Average Package (LPA)'].max()
                )
                is_highest_pkg = (
                    row['Highest Package (LPA)'] ==
                    df_f['Highest Package (LPA)'].max()
                )

                # College name
                st.markdown(
                    f"<h3 style='color:{color};text-align:center;"
                    f"margin-bottom:5px;'>{college}</h3>",
                    unsafe_allow_html=True
                )
                st.caption(str(row['Type']))

                # Badge — pure Streamlit, no HTML
                if is_best_avg:
                    st.success("🥇 Best Average Package")
                elif is_highest_pkg:
                    st.info("🚀 Highest Package")

                st.divider()

                # Stats as metrics
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(
                        "Avg Package",
                        f"Rs {row['Overall Average Package (LPA)']} LPA"
                    )
                    st.metric(
                        "Batch Size",
                        f"{int(row['Batch Size'])} students"
                    )
                    st.metric(
                        "Recruiters",
                        f"{int(row['Total Recruiters'])}"
                    )
                with col_b:
                    st.metric(
                        "Highest Pkg",
                        f"Rs {row['Highest Package (LPA)']} LPA"
                    )
                    st.metric(
                        "Placement",
                        f"{row['Placement Rate (%)']}%"
                    )
                    st.metric(
                        "Fees",
                        f"Rs {row['Fees (LPA)']} LPA"
                    )

                st.divider()

                roi = round(
                    row['Overall Average Package (LPA)'] /
                    row['Fees (LPA)'], 2
                )
                st.metric(
                    "ROI (Avg Pkg / Fees)",
                    f"{roi}x",
                    delta="Good" if roi > 1 else "Low",
                    delta_color="normal"
                )

        st.divider()

        st.markdown(
            '<div class="section-title">📋 Complete Placement Stats</div>',
            unsafe_allow_html=True
        )

        display_cols = [
            'College', 'Type', 'Batch Size', 'Placement Rate (%)',
            'Highest Package (LPA)', 'Overall Average Package (LPA)',
            'Overall Median (LPA)', 'Total Recruiters', 'Fees (LPA)'
        ]

        st.dataframe(
            df_f[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Highest Package (LPA)": st.column_config.NumberColumn(
                    format="Rs %.2f LPA"),
                "Overall Average Package (LPA)": st.column_config.NumberColumn(
                    format="Rs %.2f LPA"),
                "Overall Median (LPA)": st.column_config.NumberColumn(
                    format="Rs %.2f LPA"),
                "Fees (LPA)": st.column_config.NumberColumn(
                    format="Rs %.1f LPA"),
                "Placement Rate (%)": st.column_config.NumberColumn(
                    format="%.1f%%"),
            }
        )

        csv = df_f.to_csv(index=False)
        st.download_button(
            "Download Stats (CSV)",
            csv, "placement_stats.csv", "text/csv"
        )

    # ========== TAB 2: PACKAGES ==========
    with tab2:
        st.markdown(
            '<div class="section-title">💰 Package Deep Dive</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            fig = go.Figure()
            metrics = {
                "Highest Package (LPA)": "#e74c3c",
                "Average Package - Top 20% (LPA)": "#f39c12",
                "Overall Average Package (LPA)": "#27ae60",
                "Overall Median (LPA)": "#3498db"
            }
            for metric, color in metrics.items():
                label = metric.replace(" (LPA)", "").replace("Package", "Pkg")
                fig.add_trace(go.Bar(
                    name=label,
                    x=df_f['College'],
                    y=df_f[metric],
                    marker_color=color,
                    text=df_f[metric].apply(
                        lambda x: f"Rs{x}L" if pd.notna(x) else "N/A"),
                    textposition='outside'
                ))
            fig.update_layout(
                title="Package Comparison (LPA)",
                barmode='group',
                yaxis_title="Package (LPA)",
                height=450,
                legend=dict(orientation="h", y=-0.25),
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            df_roi = df_f.copy()
            df_roi['ROI'] = (
                df_roi['Overall Average Package (LPA)'] /
                df_roi['Fees (LPA)']
            ).round(2)
            df_roi['Payback Years'] = (
                df_roi['Fees (LPA)'] /
                df_roi['Overall Average Package (LPA)']
            ).round(2)

            fig_roi = px.bar(
                df_roi, x='College', y='ROI',
                title='ROI — Average Package / Fees',
                color='College',
                color_discrete_map=COLLEGE_COLORS,
                text='ROI'
            )
            fig_roi.update_traces(
                texttemplate='%{text}x', textposition='outside')
            fig_roi.update_layout(
                showlegend=False, height=220,
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_roi, use_container_width=True)

            fig_pb = px.bar(
                df_roi, x='College', y='Payback Years',
                title='Fee Payback Period (Years)',
                color='College',
                color_discrete_map=COLLEGE_COLORS,
                text='Payback Years'
            )
            fig_pb.update_traces(
                texttemplate='%{text} yrs', textposition='outside')
            fig_pb.update_layout(
                showlegend=False, height=220,
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_pb, use_container_width=True)

        st.markdown(
            '<div class="section-title">💡 Fees vs Average Package</div>',
            unsafe_allow_html=True
        )
        fig_scatter = px.scatter(
            df_f,
            x='Fees (LPA)',
            y='Overall Average Package (LPA)',
            size='Total Recruiters',
            color='College',
            color_discrete_map=COLLEGE_COLORS,
            text='College',
            title='Fees vs Average Package (bubble = recruiters)',
        )
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ========== TAB 3: COMPANIES & ROLES ==========
    with tab3:
        st.markdown(
            '<div class="section-title">🏢 Companies & Job Roles</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            company_count = df_comp_f.groupby('College').size().reset_index(
                name='Companies')
            fig_comp = px.bar(
                company_count, x='College', y='Companies',
                title='Number of Recruiters per College',
                color='College',
                color_discrete_map=COLLEGE_COLORS,
                text='Companies'
            )
            fig_comp.update_traces(textposition='outside')
            fig_comp.update_layout(
                showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_comp, use_container_width=True)

        with col2:
            roles_count = df_roles_f.groupby('College').size().reset_index(
                name='Roles')
            fig_roles_chart = px.bar(
                roles_count, x='College', y='Roles',
                title='Variety of Job Roles Offered',
                color='College',
                color_discrete_map=COLLEGE_COLORS,
                text='Roles'
            )
            fig_roles_chart.update_traces(textposition='outside')
            fig_roles_chart.update_layout(
                showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_roles_chart, use_container_width=True)

        st.markdown(
            '<div class="section-title">📋 Companies & Roles by College</div>',
            unsafe_allow_html=True
        )

        if selected_colleges:
            tabs_colleges = st.tabs(selected_colleges)
            for i, college in enumerate(selected_colleges):
                with tabs_colleges[i]:
                    col_companies = df_comp_f[
                        df_comp_f['College'] == college
                    ]['Company'].tolist()
                    col_roles = df_roles_f[
                        df_roles_f['College'] == college
                    ]['Role'].tolist()

                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Companies Visiting:**")
                        for company in col_companies:
                            st.markdown(f"- {company}")
                    with c2:
                        st.markdown("**Roles Offered:**")
                        for role in col_roles:
                            st.markdown(f"- {role}")

        if len(selected_colleges) > 1:
            st.markdown(
                '<div class="section-title">🤝 Companies at ALL Colleges</div>',
                unsafe_allow_html=True
            )
            sets = [
                set(df_comp_f[
                    df_comp_f['College'] == c
                ]['Company'].tolist())
                for c in selected_colleges
            ]
            common = sets[0]
            for s in sets[1:]:
                common = common.intersection(s)
            if common:
                for company in sorted(common):
                    st.markdown(f"- {company}")
            else:
                st.info("No companies common across all selected colleges.")

        csv_comp = df_comp_f.to_csv(index=False)
        st.download_button(
            "Download Companies (CSV)",
            csv_comp, "companies.csv", "text/csv"
        )

    # ========== TAB 4: SECTORS ==========
    with tab4:
        st.markdown(
            '<div class="section-title">📈 Sector-wise Placement Distribution</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            fig_sec = px.bar(
                df_sec_f,
                x='Sector',
                y='Percentage (%)',
                color='College',
                barmode='group',
                color_discrete_map=COLLEGE_COLORS,
                title='Sector Distribution by College (%)',
            )
            fig_sec.update_layout(
                height=400,
                xaxis_tickangle=-30,
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_sec, use_container_width=True)

        with col2:
            for college in selected_colleges:
                df_pie = df_sec_f[df_sec_f['College'] == college]
                if not df_pie.empty:
                    fig_pie = px.pie(
                        df_pie,
                        values='Percentage (%)',
                        names='Sector',
                        title=f'{college} — Sector Split',
                        hole=0.4
                    )
                    fig_pie.update_layout(height=280)
                    st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown(
            '<div class="section-title">🌡️ Sector Heatmap</div>',
            unsafe_allow_html=True
        )
        df_pivot = df_sec_f.pivot_table(
            values='Percentage (%)',
            index='Sector',
            columns='College',
            fill_value=0
        )
        fig_heat = px.imshow(
            df_pivot,
            color_continuous_scale='Blues',
            title='Sector Placement % Heatmap',
            text_auto=True
        )
        fig_heat.update_layout(height=400)
        st.plotly_chart(fig_heat, use_container_width=True)

        csv_sec = df_sec_f.to_csv(index=False)
        st.download_button(
            "Download Sectors (CSV)",
            csv_sec, "sectors.csv", "text/csv"
        )

    # ========== TAB 5: AI ANALYSIS ==========
    with tab5:
        st.markdown(
            '<div class="section-title">🤖 AI-Powered Analysis (Gemini)</div>',
            unsafe_allow_html=True
        )

        questions = {
            "Which college has the best ROI?":
                "Analyze ROI (average package vs fees) and rank colleges clearly.",
            "Which is best for Finance or BFSI careers?":
                "Which college is best for BFSI or Finance roles? Justify with data.",
            "Which is best for a fresher?":
                "Which college suits a fresh graduate? Consider fees, ROI, placement rates.",
            "Compare the risk at each college":
                "What is the risk at each college? Consider unplaced students and salary spread.",
            "Which college has the most prestigious companies?":
                "Compare quality and prestige of recruiters across colleges.",
            "Overall winner for MBA?":
                "Give an honest data-driven verdict: which is the best MBA college and why?"
        }

        selected_q = st.selectbox("Choose a question:", list(questions.keys()))
        custom_q = st.text_input("Or type your own question:")

        if st.button("Ask Gemini", type="primary", use_container_width=True):
            context = f"""
You are an MBA placement expert. Analyze this data:

PLACEMENT STATS:
{df_f.to_string(index=False)}

SECTOR DISTRIBUTION:
{df_sec_f.to_string(index=False)}

COMPANIES:
IIM Amritsar: {', '.join(df_comp_f[df_comp_f['College'] == 'IIM Amritsar']['Company'].tolist()[:15])}
IIM Kashipur: {', '.join(df_comp_f[df_comp_f['College'] == 'IIM Kashipur']['Company'].tolist()[:15])}
NMIMS Mumbai: {', '.join(df_comp_f[df_comp_f['College'] == 'NMIMS Mumbai']['Company'].tolist()[:15])}

Question: {custom_q if custom_q else questions[selected_q]}

Give:
1. Direct answer first
2. Data evidence with actual numbers
3. Recommendation for different student profiles
Keep it concise and practical.
"""
            with st.spinner("Gemini is analyzing..."):
                analysis = ask_gemini(context)
            st.success("Analysis Ready!")
            st.markdown(analysis)

        st.divider()
        st.markdown("**Key Numbers At a Glance:**")
        col1, col2, col3 = st.columns(3)
        cols_list = [col1, col2, col3]

        for i, (_, row) in enumerate(df_f.iterrows()):
            if i < 3:
                with cols_list[i]:
                    roi = round(
                        row['Overall Average Package (LPA)'] /
                        row['Fees (LPA)'], 2
                    )
                    st.markdown(f"**{row['College']}**")
                    st.markdown(f"- ROI: **{roi}x**")
                    st.markdown(
                        f"- Top 20%: **Rs {row['Average Package - Top 20% (LPA)']} LPA**"
                    )
                    st.markdown(
                        f"- Overall: **Rs {row['Overall Average Package (LPA)']} LPA**"
                    )

        st.divider()
        st.markdown(
            '<div class="section-title">📥 Export Everything</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            try:
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_stats.to_excel(
                        writer, sheet_name='Placement Stats', index=False)
                    df_companies.to_excel(
                        writer, sheet_name='Companies', index=False)
                    df_sectors.to_excel(
                        writer, sheet_name='Sectors', index=False)
                    df_roles.to_excel(
                        writer, sheet_name='Job Roles', index=False)
                st.download_button(
                    "Download Complete Excel Report",
                    buffer.getvalue(),
                    "IIM_Placement_Report.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Excel export error: {e}")

        with col2:
            all_csv = df_stats.to_csv(index=False)
            st.download_button(
                "Download Stats CSV",
                all_csv,
                "IIM_All_Data.csv",
                "text/csv",
                use_container_width=True
            )

    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align:center;color:#aaa;font-size:0.85rem;'>"
        "IIM Placement Intelligence | Data: 2024-25 | "
        "AI: Google Gemini | Built with Python + Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()