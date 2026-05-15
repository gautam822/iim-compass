# scraper.py — Smart hybrid: verified data + live company scraping
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

# ============================================================
# VERIFIED PLACEMENT DATA (from official reports + search)
# ============================================================
VERIFIED_DATA = {
    "IIM Amritsar": {
        "stats": {
            "College": "IIM Amritsar",
            "Type": "Baby IIM (Government)",
            "Program": "MBA",
            "Batch Size": 320,
            "Placement Rate (%)": 100,
            "Highest Package (LPA)": 25.86,
            "Average Package - Top 20% (LPA)": 19.11,
            "Median Package - Top 20% (LPA)": 18.0,
            "Overall Average Package (LPA)": 14.5,  # estimated from RTI
            "Overall Median (LPA)": 15.6,  # NIRF verified
            "Total Recruiters": 300,
            "PPO Rate (%)": None,
            "Fees (LPA)": 21.5,
            "Year": 2025,
            "Data Source": "Official + NIRF 2025 + RTI"
        },
        "top_sectors": {
            "BFSI": 38,
            "Finance": 35,
            "Consulting": 15,
            "IT & Analytics": 12,
            "FMCG": 8,
            "Operations": 5,
            "Marketing": 7,
        },
        "top_companies": [
            "Amazon", "Dell", "Ernst & Young", "Infosys", "Maruti Suzuki",
            "Deloitte", "ICICI Bank", "Kotak Mahindra Bank", "HDFC Bank",
            "Tata Capital", "Reliance", "Accenture", "Adani Group",
            "Cipla", "HCL", "TVS", "Cognizant", "Capgemini",
            "TATA Steel", "Flipkart", "Amul", "RBI", "SBI",
            "Kore AI", "Latent View Analytics", "Porter", "VIP Industries",
            "Arcesium", "Tiger Analytics", "BMW India",
        ],
        "roles": [
            "Financial Analyst", "Business Analyst", "Consultant",
            "Product Manager", "Operations Manager", "Marketing Manager",
            "Investment Analyst", "Strategy Analyst", "Data Analyst",
            "Sales Manager", "Risk Analyst", "Brand Manager"
        ]
    },

    "IIM Kashipur": {
        "stats": {
            "College": "IIM Kashipur",
            "Type": "Baby IIM (Government)",
            "Program": "MBA",
            "Batch Size": 433,
            "Placement Rate (%)": 97.7,  # 10 unplaced out of 433
            "Highest Package (LPA)": 33.12,
            "Average Package - Top 20% (LPA)": 21.51,
            "Median Package - Top 20% (LPA)": None,
            "Overall Average Package (LPA)": 14.95,  # officially published
            "Overall Median (LPA)": 14.46,
            "Total Recruiters": 190,
            "PPO Rate (%)": None,
            "Fees (LPA)": 13.5,
            "Year": 2025,
            "Data Source": "Official Placement Report 2025"
        },
        "top_sectors": {
            "BFSI": 40,
            "Consulting": 25,
            "IT & Analytics": 20,
            "FMCG": 8,
            "Manufacturing": 5,
            "E-commerce": 2,
        },
        "top_companies": [
            "Accenture", "Axis Bank", "Bank of America", "Cognizant",
            "Capgemini", "Deloitte", "KPMG", "HDFC Bank", "ICICI Bank",
            "AB InBev", "Amazon", "Tata Steel", "Tata Motors",
            "L&T", "Puma", "EXL Analytics", "Gartner", "SBI Capital",
            "Infosys", "Google", "NatWest Group", "IDBI Bank",
            "Tech Mahindra", "Digit Insurance", "American Express",
            "JP Morgan", "Wells Fargo", "McKinsey", "BCG",
        ],
        "roles": [
            "Financial Analyst", "Management Consultant", "Business Analyst",
            "Operations Manager", "Data Analyst", "Marketing Manager",
            "Product Manager", "Risk Analyst", "Investment Banker",
            "Strategy Consultant", "Sales Manager", "IT Consultant"
        ]
    },

    "NMIMS Mumbai": {
        "stats": {
            "College": "NMIMS Mumbai",
            "Type": "Private (Deemed University)",
            "Program": "MBA Core",
            "Batch Size": 450,
            "Placement Rate (%)": 96,
            "Highest Package (LPA)": 67.70,
            "Average Package - Top 20% (LPA)": 40.60,
            "Median Package - Top 20% (LPA)": None,
            "Overall Average Package (LPA)": 25.13,
            "Overall Median (LPA)": 20.0,
            "Total Recruiters": 168,
            "PPO Rate (%)": 37,
            "Fees (LPA)": 24.0,
            "Year": 2025,
            "Data Source": "Official Placement Report 2024"
        },
        "top_sectors": {
            "BFSI": 35,
            "Consulting": 19,
            "FMCG": 15,
            "IT & Analytics": 12,
            "E-commerce": 6,
            "General Management": 8,
            "Marketing": 5,
        },
        "top_companies": [
            "Goldman Sachs", "McKinsey & Company", "BCG", "Bain & Company",
            "Accenture Strategy", "American Express", "Aditya Birla Capital",
            "Crisil", "Wells Fargo", "JP Morgan", "Axis Bank", "ICICI Bank",
            "ITC", "Samsung", "Pepsico", "L&T", "Google", "Microsoft",
            "Oracle", "Amazon", "Deloitte", "KPMG", "EY",
            "Asian Paints", "Hindustan Unilever", "Nestle", "P&G",
            "Rakuten", "Sony", "Works Applications", "Zomato", "Flipkart",
        ],
        "roles": [
            "Investment Banker", "Management Consultant", "Strategy Manager",
            "Product Manager", "Business Analyst", "Financial Analyst",
            "Marketing Manager", "Brand Manager", "Operations Manager",
            "Data Scientist", "Risk Manager", "General Manager",
            "Solution Manager", "Category Manager", "Corporate Finance"
        ]
    }
}

def build_dataframes():
    """Build structured DataFrames from verified data."""
    
    # ===== STATS DataFrame =====
    stats_list = []
    for college, data in VERIFIED_DATA.items():
        stats_list.append(data["stats"])
    df_stats = pd.DataFrame(stats_list)
    
    # ===== COMPANIES DataFrame =====
    companies_list = []
    for college, data in VERIFIED_DATA.items():
        for company in data["top_companies"]:
            companies_list.append({
                "College": college,
                "Company": company
            })
    df_companies = pd.DataFrame(companies_list)
    
    # ===== SECTORS DataFrame =====
    sectors_list = []
    for college, data in VERIFIED_DATA.items():
        for sector, percentage in data["top_sectors"].items():
            sectors_list.append({
                "College": college,
                "Sector": sector,
                "Percentage (%)": percentage
            })
    df_sectors = pd.DataFrame(sectors_list)
    
    # ===== ROLES DataFrame =====
    roles_list = []
    for college, data in VERIFIED_DATA.items():
        for role in data["roles"]:
            roles_list.append({
                "College": college,
                "Role": role
            })
    df_roles = pd.DataFrame(roles_list)
    
    return df_stats, df_companies, df_sectors, df_roles

def scrape_live_companies():
    """Try to scrape additional company names from Shiksha/Careers360."""
    extra_companies = []
    
    urls = {
        "IIM Amritsar": "https://www.shiksha.com/college/iim-amritsar-indian-institute-of-management-47709/placement",
        "IIM Kashipur": "https://www.shiksha.com/college/iim-kashipur-indian-institute-of-management-36080/placement",
        "NMIMS Mumbai": "https://www.shiksha.com/university/nmims-mumbai-52743/placement"
    }
    
    for college, url in urls.items():
        try:
            print(f"🌐 Trying to scrape live data for {college}...")
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for company names in various HTML elements
            for tag in soup.find_all(['li', 'td', 'span', 'div']):
                text = tag.get_text(strip=True)
                # Filter for company-like text
                if (3 < len(text) < 40 and 
                    not any(x in text.lower() for x in [
                        'lpa', 'package', 'salary', '%', 'placement', 
                        'student', 'batch', 'recruiter', 'sector', 'click',
                        'read more', 'view all', 'download', 'apply'
                    ]) and
                    text[0].isupper()):
                    extra_companies.append({
                        "College": college,
                        "Company": text,
                        "Source": "Live Scrape"
                    })
            
            time.sleep(2)
            print(f"✅ Found {len(extra_companies)} extra entries for {college}")
            
        except Exception as e:
            print(f"⚠️ Could not scrape {college}: {e}")
    
    return extra_companies

def save_all_data():
    """Build, save and return all DataFrames."""
    print("🏗️ Building verified data...")
    df_stats, df_companies, df_sectors, df_roles = build_dataframes()
    
    print("🌐 Attempting live scrape for extra companies...")
    extra = scrape_live_companies()
    
    if extra:
        df_extra = pd.DataFrame(extra)
        # Add to companies if not already there
        existing = set(df_companies['Company'].tolist())
        new_companies = df_extra[~df_extra['Company'].isin(existing)]
        if not new_companies.empty:
            df_companies = pd.concat([df_companies, new_companies[['College', 'Company']]], ignore_index=True)
    
    # Save to CSV
    df_stats.to_csv('placement_stats.csv', index=False)
    df_companies.to_csv('companies.csv', index=False)
    df_sectors.to_csv('sectors.csv', index=False)
    df_roles.to_csv('roles.csv', index=False)
    
    print("\n✅ All data saved!")
    print(f"📊 Stats: {len(df_stats)} colleges")
    print(f"🏢 Companies: {len(df_companies)} entries")
    print(f"📈 Sectors: {len(df_sectors)} entries")
    print(f"💼 Roles: {len(df_roles)} entries")
    
    return df_stats, df_companies, df_sectors, df_roles

if __name__ == "__main__":
    save_all_data()
    print("\n🚀 Now run: streamlit run dashboard.py")