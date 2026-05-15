# dashboard.py — IIM Placement Comparison Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="IIM Placement Dashboard",
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
        background: linear-gradient(135deg, #1f4e79, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
    .college-card {
        background: linear-gradient(135deg, #f8f9ff, #e8ecff);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #dee2ff;
        margin-bottom: 15px;
    }
    .winner-badge {
        background: linear-gradient(135deg, #ffd700, #ffaa00);
        color: #1a1a1a;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ===== COLORS =====
COLLEGE_COLORS = {
    "IIM Amritsar": "#667eea",
    "IIM Kashipur": "#f093fb",
    "NMIMS Mumbai": "#4facfe"
}

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
        st.error("⚠️ Data files not found! Please run scraper.py first.")
        st.code("python scraper.py")
        st.stop()

# ===== GEMINI AI =====
def ask_gemini(prompt):
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ AI Analysis error: {e}"

# ===== MAIN APP =====
def main():
    # Header
    st.markdown('<div class="big-title">🎓 IIM Placement Intelligence</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="subtitle">IIM Amritsar vs IIM Kashipur vs NMIMS Mumbai — Data-Driven Comparison</div>', 
                unsafe_allow_html=True)
    
    # Load data
    df_stats, df_companies, df_sectors, df_roles = load_all_data()
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/graduation-cap.png", width=60)
        st.title("⚙️ Controls")
        
        selected_colleges = st.multiselect(
            "Select Colleges",
            options=df_stats['College'].tolist(),
            default=df_stats['College'].tolist()
        )
        
        st.divider()
        st.markdown("### 📊 Data Info")
        st.info(f"""
        **Colleges:** {len(selected_colleges)} selected  
        **Data Year:** 2024-25  
        **Companies tracked:** {len(df_companies)}  
        **Source:** Official reports + NIRF
        """)
        
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Filter
    df_f = df_stats[df_stats['College'].isin(selected_colleges)]
    df_comp_f = df_companies[df_companies['College'].isin(selected_colleges)]
    df_sec_f = df_sectors[df_sectors['College'].isin(selected_colleges)]
    df_roles_f = df_roles[df_roles['College'].isin(selected_colleges)]
    
    # ===== TAB LAYOUT =====
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "💰 Packages", 
        "🏢 Companies & Roles",
        "📈 Sectors",
        "🤖 AI Analysis"
    ])
    
    # ========== TAB 1: OVERVIEW ==========
    with tab1:
        st.markdown('<div class="section-title">🏆 Quick Comparison at a Glance</div>', 
                    unsafe_allow_html=True)
        
        # Key metric cards per college
        cols = st.columns(len(selected_colleges))
        for i, (_, row) in enumerate(df_f.iterrows()):
            with cols[i]:
                college = row['College']
                color = COLLEGE_COLORS.get(college, "#667eea")
                
                # Determine winner badges
                is_highest_pkg = row['Highest Package (LPA)'] == df_f['Highest Package (LPA)'].max()
                is_best_avg = row['Overall Average Package (LPA)'] == df_f['Overall Average Package (LPA)'].max()
                is_best_roi = (row['Overall Average Package (LPA)'] / row['Fees (LPA)']) == \
                              (df_f['Overall Average Package (LPA)'] / df_f['Fees (LPA)']).max()
                
                badge = ""
                if is_best_avg:
                    badge = "🥇 Best Average"
                elif is_highest_pkg:
                    badge = "🚀 Highest Package"
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, {color}22, {color}11);
                            border: 2px solid {color}; border-radius: 15px; padding: 20px;
                            text-align: center;'>
                    <h3 style='color: {color}; margin: 0;'>{college}</h3>
                    <p style='color: #888; font-size: 0.85rem;'>{row['Type']}</p>
                    {'<span style="background:'+color+';color:white;padding:3px 10px;border-radius:20px;font-size:0.75rem;">'+badge+'</span>' if badge else ''}
                    <hr style='border-color: {color}44;'>
                    <p style='margin: 5px 0;'>💰 <b>Avg Package:</b> ₹{row['Overall Average Package (LPA)']} LPA</p>
                    <p style='margin: 5px 0;'>🏆 <b>Highest:</b> ₹{row['Highest Package (LPA)']} LPA</p>
                    <p style='margin: 5px 0;'>👥 <b>Batch:</b> {int(row['Batch Size'])} students</p>
                    <p style='margin: 5px 0;'>✅ <b>Placement:</b> {row['Placement Rate (%)']}%</p>
                    <p style='margin: 5px 0;'>🏢 <b>Recruiters:</b> {int(row['Total Recruiters'])}</p>
                    <p style='margin: 5px 0;'>💸 <b>Fees:</b> ₹{row['Fees (LPA)']} LPA</p>
                </div>
                """, unsafe_allow_html=True)
                
                # ROI metric
                roi = round(row['Overall Average Package (LPA)'] / row['Fees (LPA)'], 2)
                st.metric("📈 ROI (Avg/Fees)", f"{roi}x", 
                         delta="Good" if roi > 1 else "Low",
                         delta_color="normal")
        
        st.divider()
        
        # Full stats table
        st.markdown('<div class="section-title">📋 Complete Stats Table</div>', 
                    unsafe_allow_html=True)
        
        # Format for display
        display_cols = [
            'College', 'Type', 'Batch Size', 'Placement Rate (%)',
            'Highest Package (LPA)', 'Overall Average Package (LPA)',
            'Overall Median (LPA)', 'Total Recruiters', 'PPO Rate (%)', 'Fees (LPA)'
        ]
        st.dataframe(
            df_f[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Highest Package (LPA)": st.column_config.NumberColumn(format="₹%.2f LPA"),
                "Overall Average Package (LPA)": st.column_config.NumberColumn(format="₹%.2f LPA"),
                "Overall Median (LPA)": st.column_config.NumberColumn(format="₹%.2f LPA"),
                "Fees (LPA)": st.column_config.NumberColumn(format="₹%.1f LPA"),
                "Placement Rate (%)": st.column_config.NumberColumn(format="%.1f%%"),
            }
        )
        
        # Download button
        csv = df_f.to_csv(index=False)
        st.download_button(
            "⬇️ Download Stats (CSV)",
            csv, "placement_stats.csv", "text/csv"
        )
    
    # ========== TAB 2: PACKAGES ==========
    with tab2:
        st.markdown('<div class="section-title">💰 Package Deep Dive</div>', 
                    unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart: Multi-metric packages
            fig = go.Figure()
            
            metrics = {
                "Highest Package (LPA)": "#e74c3c",
                "Average Package - Top 20% (LPA)": "#f39c12",
                "Overall Average Package (LPA)": "#27ae60",
                "Overall Median (LPA)": "#3498db"
            }
            
            for metric, color in metrics.items():
                fig.add_trace(go.Bar(
                    name=metric.replace(" (LPA)", "").replace("Package", "Pkg"),
                    x=df_f['College'],
                    y=df_f[metric],
                    marker_color=color,
                    text=df_f[metric].apply(lambda x: f"₹{x}L" if pd.notna(x) else "N/A"),
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
            # ROI Comparison
            df_roi = df_f.copy()
            df_roi['ROI'] = (df_roi['Overall Average Package (LPA)'] / 
                            df_roi['Fees (LPA)']).round(2)
            df_roi['Payback Years'] = (df_roi['Fees (LPA)'] / 
                                      df_roi['Overall Average Package (LPA)']).round(2)
            
            fig_roi = px.bar(
                df_roi, x='College', y='ROI',
                title='Return on Investment (Average Pkg / Fees)',
                color='College',
                color_discrete_map=COLLEGE_COLORS,
                text='ROI'
            )
            fig_roi.update_traces(texttemplate='%{text}x', textposition='outside')
            fig_roi.update_layout(
                showlegend=False, height=220,
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_roi, use_container_width=True)
            
            # Payback period chart
            fig_pb = px.bar(
                df_roi, x='College', y='Payback Years',
                title='Fee Payback Period (Years)',
                color='College',
                color_discrete_map=COLLEGE_COLORS,
                text='Payback Years'
            )
            fig_pb.update_traces(
                texttemplate='%{text} yrs', textposition='outside'
            )
            fig_pb.update_layout(
                showlegend=False, height=220,
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_pb, use_container_width=True)
        
        # Scatter: Fees vs Average Package
        st.markdown('<div class="section-title">💡 Fees vs Average Package</div>', 
                    unsafe_allow_html=True)
        
        fig_scatter = px.scatter(
            df_f,
            x='Fees (LPA)', y='Overall Average Package (LPA)',
            size='Total Recruiters',
            color='College',
            color_discrete_map=COLLEGE_COLORS,
            text='College',
            title='Fees vs Average Package (bubble size = number of recruiters)',
            labels={
                'Fees (LPA)': 'Annual Fees (LPA)',
                'Overall Average Package (LPA)': 'Average Package (LPA)'
            }
        )
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # ========== TAB 3: COMPANIES & ROLES ==========
    with tab3:
        st.markdown('<div class="section-title">🏢 Companies & Job Roles</div>', 
                    unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Companies per college
            company_count = df_comp_f.groupby('College').size().reset_index(name='Companies')
            fig_comp = px.bar(
                company_count, x='College', y='Companies',
                title='Number of Recruiters per College',
                color='College', color_discrete_map=COLLEGE_COLORS,
                text='Companies'
            )
            fig_comp.update_traces(textposition='outside')
            fig_comp.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_comp, use_container_width=True)
        
        with col2:
            # Roles per college
            roles_count = df_roles_f.groupby('College').size().reset_index(name='Roles')
            fig_roles = px.bar(
                roles_count, x='College', y='Roles',
                title='Variety of Job Roles Offered',
                color='College', color_discrete_map=COLLEGE_COLORS,
                text='Roles'
            )
            fig_roles.update_traces(textposition='outside')
            fig_roles.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_roles, use_container_width=True)
        
        # College-wise company lists
        st.markdown('<div class="section-title">📋 Company Lists by College</div>', 
                    unsafe_allow_html=True)
        
        tabs_colleges = st.tabs(selected_colleges)
        for i, college in enumerate(selected_colleges):
            with tabs_colleges[i]:
                col_companies = df_comp_f[df_comp_f['College'] == college]['Company'].tolist()
                col_roles = df_roles_f[df_roles_f['College'] == college]['Role'].tolist()
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**🏢 Companies Visiting:**")
                    # Display as grid
                    company_html = " ".join([
                        f'<span style="background:#667eea22;border:1px solid #667eea44;'
                        f'padding:4px 10px;border-radius:20px;margin:3px;display:inline-block;'
                        f'font-size:0.85rem;">{c}</span>'
                        for c in col_companies
                    ])
                    st.markdown(company_html, unsafe_allow_html=True)
                
                with c2:
                    st.markdown("**💼 Roles Offered:**")
                    roles_html = " ".join([
                        f'<span style="background:#f093fb22;border:1px solid #f093fb44;'
                        f'padding:4px 10px;border-radius:20px;margin:3px;display:inline-block;'
                        f'font-size:0.85rem;">{r}</span>'
                        for r in col_roles
                    ])
                    st.markdown(roles_html, unsafe_allow_html=True)
        
        st.divider()
        
        # Common companies across all 3
        if len(selected_colleges) > 1:
            st.markdown('<div class="section-title">🤝 Companies Visiting ALL Selected Colleges</div>', 
                        unsafe_allow_html=True)
            
            sets = [
                set(df_comp_f[df_comp_f['College'] == c]['Company'].tolist())
                for c in selected_colleges
            ]
            common = sets[0]
            for s in sets[1:]:
                common = common.intersection(s)
            
            if common:
                common_html = " ".join([
                    f'<span style="background:#27ae6022;border:1px solid #27ae6044;'
                    f'padding:6px 14px;border-radius:20px;margin:4px;display:inline-block;'
                    f'font-weight:bold;">{c}</span>'
                    for c in sorted(common)
                ])
                st.markdown(common_html, unsafe_allow_html=True)
            else:
                st.info("No companies common across all selected colleges in our dataset.")
        
        # Download
        csv_comp = df_comp_f.to_csv(index=False)
        st.download_button("⬇️ Download Companies (CSV)", csv_comp, 
                          "companies.csv", "text/csv")
    
    # ========== TAB 4: SECTORS ==========
    with tab4:
        st.markdown('<div class="section-title">📈 Sector-wise Placement Distribution</div>', 
                    unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Grouped bar by sector
            fig_sec = px.bar(
                df_sec_f, x='Sector', y='Percentage (%)',
                color='College', barmode='group',
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
            # Pie charts per college
            for college in selected_colleges:
                df_pie = df_sec_f[df_sec_f['College'] == college]
                if not df_pie.empty:
                    fig_pie = px.pie(
                        df_pie, values='Percentage (%)', names='Sector',
                        title=f'{college} - Sector Split',
                        hole=0.4
                    )
                    fig_pie.update_layout(height=280, showlegend=True)
                    st.plotly_chart(fig_pie, use_container_width=True)
        
        # Heatmap
        st.markdown('<div class="section-title">🌡️ Sector Heatmap</div>', 
                    unsafe_allow_html=True)
        
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
        
        # Download sectors
        csv_sec = df_sec_f.to_csv(index=False)
        st.download_button("⬇️ Download Sectors (CSV)", csv_sec,
                          "sectors.csv", "text/csv")
    
    # ========== TAB 5: AI ANALYSIS ==========
    with tab5:
        st.markdown('<div class="section-title">🤖 AI-Powered Analysis (Gemini)</div>', 
                    unsafe_allow_html=True)
        
        # Pre-built questions
        questions = {
            "🏆 Which college has the best ROI?": 
                "Analyze the ROI (average package vs fees) for each college and rank them clearly.",
            "💰 Which is best for Finance/BFSI careers?":
                "Which college is best for someone wanting BFSI or Finance roles? Justify with data.",
            "🎯 Which is best for a fresher?":
                "Which college suits a fresh graduate better — considering fees, ROI, and placement rates?",
            "📊 Compare the risk at each college":
                "What's the risk at each college? Consider unplaced students, batch size, and salary spread.",
            "🏢 Which college gets the most prestigious companies?":
                "Compare the quality and prestige of recruiters across these colleges.",
            "🤔 Overall winner for MBA?":
                "Give an honest, data-driven verdict: which is the best MBA college among these three and why?"
        }
        
        selected_q = st.selectbox("📝 Choose a question:", list(questions.keys()))
        custom_q = st.text_input("✏️ Or type your own question:")
        
        if st.button("🤖 Ask Gemini", type="primary", use_container_width=True):
            
            # Build context from data
            context = f"""
            You are an MBA placement expert. Analyze this data:
            
            PLACEMENT STATS:
            {df_f.to_string(index=False)}
            
            SECTOR DISTRIBUTION:
            {df_sec_f.to_string(index=False)}
            
            COMPANIES:
            IIM Amritsar: {', '.join(df_comp_f[df_comp_f['College']=='IIM Amritsar']['Company'].tolist()[:15])}
            IIM Kashipur: {', '.join(df_comp_f[df_comp_f['College']=='IIM Kashipur']['Company'].tolist()[:15])}
            NMIMS Mumbai: {', '.join(df_comp_f[df_comp_f['College']=='NMIMS Mumbai']['Company'].tolist()[:15])}
            
            Question: {custom_q if custom_q else questions[selected_q]}
            
            Give a structured analysis with:
            1. Direct answer first
            2. Data evidence (use actual numbers from the data)
            3. Recommendation for different student profiles
            Keep it concise and practical.
            """
            
            with st.spinner("🧠 Gemini is analyzing the data..."):
                analysis = ask_gemini(context)
            
            st.success("✅ Analysis Ready!")
            st.markdown(analysis)
            
            # Save analysis
            with open("ai_analysis.txt", "w") as f:
                f.write(f"Question: {custom_q if custom_q else selected_q}\n\n")
                f.write(analysis)
            st.info("💾 Analysis saved to ai_analysis.txt")
        
        st.divider()
        
        # Quick stats AI won't miss
        st.markdown("**📊 Key Numbers At a Glance:**")
        
        col1, col2, col3 = st.columns(3)
        
        for i, (_, row) in enumerate(df_f.iterrows()):
            with [col1, col2, col3][i]:
                roi = round(row['Overall Average Package (LPA)'] / row['Fees (LPA)'], 2)
                st.markdown(f"""
                **{row['College']}**
                - Avg/Fees ROI: **{roi}x**
                - Top 20% get: **₹{row['Average Package - Top 20% (LPA)']} LPA**
                - Overall gets: **₹{row['Overall Average Package (LPA)']} LPA**
                """)
        
        # Excel export
        st.divider()
        st.markdown('<div class="section-title">📥 Export Everything</div>', 
                    unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            try:
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_stats.to_excel(writer, sheet_name='Placement Stats', index=False)
                    df_companies.to_excel(writer, sheet_name='Companies', index=False)
                    df_sectors.to_excel(writer, sheet_name='Sectors', index=False)
                    df_roles.to_excel(writer, sheet_name='Job Roles', index=False)
                
                st.download_button(
                    "📁 Download Complete Excel Report",
                    buffer.getvalue(),
                    "IIM_Placement_Report.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Excel export error: {e}")
        
        with col2:
            all_csv = pd.concat([
                df_stats, df_companies, df_sectors, df_roles
            ]).to_csv(index=False)
            st.download_button(
                "📊 Download All Data (CSV)",
                all_csv,
                "IIM_All_Data.csv",
                "text/csv",
                use_container_width=True
            )
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align:center;color:#aaa;font-size:0.85rem;'>
        🎓 IIM Placement Intelligence | Data: 2024-25 Official Reports + NIRF | 
        AI: Google Gemini | Built with Python + Streamlit
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()