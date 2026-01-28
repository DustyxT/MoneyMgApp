import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import io
import zipfile
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Student Finance Commander",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constants
LKR_RATE = 200
CURRENCY_SYMBOL = "$"

# --- ENHANCED DARK MODE CSS ---
PREMIUM_DARK_CSS = """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Dark Theme with Gradient */
    .stApp { 
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Hide Sidebar */
    section[data-testid="stSidebar"] { display: none; }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 { 
        color: #ffffff !important; 
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    
    h1 { 
        background: linear-gradient(90deg, #00d4ff, #7c3aed, #f472b6) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
    
    p, span, label, div { 
        color: #e0e0e0 !important; 
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Header */
    header[data-testid="stHeader"] { 
        background: linear-gradient(90deg, #0f0f1a, #1a1a2e) !important;
        border-bottom: 1px solid rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Glassmorphism Cards for Metrics */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.2) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
    }
    
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }
    
    /* Data Editors / Tables - Glassmorphism */
    div[data-testid="stDataEditor"], div[data-testid="stDataFrame"] {
        background: rgba(22, 33, 62, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    /* Table cells */
    div[class*="stDataFrame"] div[class*="dvn-scroller"] {
        color: #e0e0e0 !important;
    }
    
    /* Buttons - Gradient Style */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
        background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%) !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4) !important;
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%) !important;
    }
    
    /* Calendar Buttons */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        padding: 8px 12px !important;
        font-size: 0.85rem !important;
    }
    
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        background: rgba(99, 102, 241, 0.3) !important;
        border-color: #6366f1 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border-radius: 16px !important;
        padding: 8px !important;
        gap: 8px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #94a3b8 !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        padding: 12px 24px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
    }
    
    /* Date Input */
    div[data-testid="stDateInput"] input {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* Select boxes */
    div[data-baseweb="select"] > div {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Radio buttons */
    div[data-testid="stRadio"] label {
        background: rgba(30, 41, 59, 0.5) !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        margin-right: 8px !important;
    }
    
    /* Progress bars */
    div[data-testid="stProgress"] > div {
        background: rgba(30, 41, 59, 0.5) !important;
        border-radius: 8px !important;
    }
    
    div[data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, #10b981, #059669) !important;
        border-radius: 8px !important;
    }
    
    /* Horizontal lines */
    hr {
        border-color: rgba(99, 102, 241, 0.2) !important;
        margin: 24px 0 !important;
    }
    
    /* Info/Warning/Success boxes */
    div[data-testid="stAlert"] {
        background: rgba(30, 41, 59, 0.8) !important;
        border-radius: 12px !important;
        border-left: 4px solid #6366f1 !important;
    }
    
    /* Expanders */
    details {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 12px !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 4px;
    }
    
    /* Caption text */
    .stCaption, figcaption {
        color: #64748b !important;
        font-size: 0.85rem !important;
    }
    
    /* Download button */
    div[data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3) !important;
    }
</style>
"""

# Apply Premium Dark Theme
st.markdown(PREMIUM_DARK_CSS, unsafe_allow_html=True)

st.title("🎓 STUDENT FINANCE COMMANDER")

# --- DATA FUNCTIONS ---
def load_or_create_df(filename, columns, default_data=None):
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)
        if default_data:
            df = pd.DataFrame(default_data)
        return df

def save_df(df, filename):
    df.to_csv(filename, index=False)

# --- DATA INITIALIZATION ---
if 'initialized' not in st.session_state:
    # Budget Config (default budgets for date ranges)
    st.session_state.df_budget_config = load_or_create_df('budget_config.csv',
        ["Category", "Type", "Budget", "Start Date", "End Date"],
        [
            # Income defaults
            {"Category": "Part Time Job", "Type": "Income", "Budget": 2400.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Other Income", "Type": "Income", "Budget": 500.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            # Bills defaults
            {"Category": "Phone", "Type": "Bills", "Budget": 100.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Internet", "Type": "Bills", "Budget": 80.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Gas", "Type": "Bills", "Budget": 100.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Water", "Type": "Bills", "Budget": 50.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            # Expenses defaults
            {"Category": "Rent", "Type": "Expenses", "Budget": 1000.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Groceries", "Type": "Expenses", "Budget": 500.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Gym", "Type": "Expenses", "Budget": 50.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Insurance", "Type": "Expenses", "Budget": 200.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Utilities", "Type": "Expenses", "Budget": 300.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Eat Out", "Type": "Expenses", "Budget": 300.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Subscriptions", "Type": "Expenses", "Budget": 50.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Phone Bill", "Type": "Expenses", "Budget": 200.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Gifts", "Type": "Expenses", "Budget": 200.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Fuel", "Type": "Expenses", "Budget": 200.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Shopping", "Type": "Expenses", "Budget": 400.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Internet Bill", "Type": "Expenses", "Budget": 80.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            # Savings defaults
            {"Category": "Home Deposit", "Type": "Savings", "Budget": 1000.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Emergency", "Type": "Savings", "Budget": 200.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Family Remittance", "Type": "Savings", "Budget": 5000.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            # Debt defaults
            {"Category": "Car Loan", "Type": "Debt", "Budget": 170.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
            {"Category": "Credit", "Type": "Debt", "Budget": 500.0, "Start Date": "2026-01-01", "End Date": "2026-12-31"},
        ])
    
    # Transaction log (actual values by date)
    st.session_state.df_transactions = load_or_create_df('transactions.csv',
        ["Date", "Category", "Type", "Actual"],
        [])
    
    st.session_state.selected_date = datetime.now().date()
    st.session_state.initialized = True

# --- HELPER: Get budget for a category on a specific date ---
def get_budget_for_date(category, cat_type, target_date):
    config = st.session_state.df_budget_config
    matches = config[(config['Category'] == category) & (config['Type'] == cat_type)]
    for _, row in matches.iterrows():
        start = datetime.strptime(str(row['Start Date']), "%Y-%m-%d").date()
        end = datetime.strptime(str(row['End Date']), "%Y-%m-%d").date()
        if start <= target_date <= end:
            return row['Budget']
    return 0.0

# --- HELPER: Get actual for a category on a specific date ---
def get_actual_for_date(category, cat_type, target_date):
    txns = st.session_state.df_transactions
    matches = txns[(txns['Category'] == category) & (txns['Type'] == cat_type) & (txns['Date'] == str(target_date))]
    if not matches.empty:
        return matches['Actual'].sum()
    return 0.0

# --- HELPER: Build table for a category type ---
def build_category_table(cat_type, target_date):
    config = st.session_state.df_budget_config
    categories = config[config['Type'] == cat_type]['Category'].unique()
    
    rows = []
    for cat in categories:
        budget = get_budget_for_date(cat, cat_type, target_date)
        actual = get_actual_for_date(cat, cat_type, target_date)
        rows.append({
            "Category": cat,
            "Budget": budget,
            "Actual": actual,
            "Difference": budget - actual
        })
    
    return pd.DataFrame(rows)

# --- WEEK HELPER FUNCTIONS ---
def get_week_start(d):
    """Return Monday of the week containing date d."""
    if isinstance(d, datetime):
        d = d.date()
    return d - timedelta(days=d.weekday())

def get_week_end(d):
    """Return Sunday of the week containing date d."""
    return get_week_start(d) + timedelta(days=6)

def get_week_number(d):
    """Return ISO week number."""
    if isinstance(d, datetime):
        d = d.date()
    return d.isocalendar()[1]

def get_week_label(d):
    """Return formatted week label like 'Week 4: Jan 20 – Jan 26'."""
    start = get_week_start(d)
    end = get_week_end(d)
    week_num = get_week_number(d)
    return f"Week {week_num}: {start.strftime('%b %d')} – {end.strftime('%b %d, %Y')}"

def get_actual_for_week(category, cat_type, week_start):
    """Get actual spending for a category during a specific week."""
    txns = st.session_state.df_transactions
    week_end = week_start + timedelta(days=6)
    
    if txns.empty:
        return 0.0
    
    # Convert Date column to date objects for comparison
    txns_copy = txns.copy()
    txns_copy['DateObj'] = pd.to_datetime(txns_copy['Date']).dt.date
    
    matches = txns_copy[
        (txns_copy['Category'] == category) & 
        (txns_copy['Type'] == cat_type) & 
        (txns_copy['DateObj'] >= week_start) & 
        (txns_copy['DateObj'] <= week_end)
    ]
    
    if not matches.empty:
        return matches['Actual'].sum()
    return 0.0

def build_category_table_weekly(cat_type, week_start):
    """Build table for a category type aggregated for a week."""
    config = st.session_state.df_budget_config
    categories = config[config['Type'] == cat_type]['Category'].unique()
    
    rows = []
    for cat in categories:
        # Get monthly budget and convert to weekly (÷ 4.33)
        monthly_budget = get_budget_for_date(cat, cat_type, week_start)
        weekly_budget = monthly_budget / 4.33
        actual = get_actual_for_week(cat, cat_type, week_start)
        rows.append({
            "Category": cat,
            "Budget": round(weekly_budget, 2),
            "Actual": actual,
            "Difference": round(weekly_budget - actual, 2)
        })
    
    return pd.DataFrame(rows)

# --- REACTIVE DRAFT STATE MANAGEMENT ---
def load_draft_data(week_start):
    """Load weekly data from source into session state drafts."""
    st.session_state.draft_data = {
        'Income': build_category_table_weekly("Income", week_start),
        'Bills': build_category_table_weekly("Bills", week_start),
        'Expenses': build_category_table_weekly("Expenses", week_start),
        'Savings': build_category_table_weekly("Savings", week_start),
        'Debt': build_category_table_weekly("Debt", week_start)
    }
    st.session_state.current_week_start = week_start

def recast_column_types(df):
    """Ensure numeric columns are float to prevent type errors during editing."""
    numeric_cols = ['Budget', 'Actual', 'Difference']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(float)
    return df

def recalc_callback(cat_type):
    """Callback to update draft data from editor changes."""
    editor_key = f"{cat_type.lower()}_editor"
    if editor_key in st.session_state:
        changes = st.session_state[editor_key].get("edited_rows", {})
        df = st.session_state.draft_data[cat_type]
        
        # Apply changes
        for idx, col_changes in changes.items():
            for col, value in col_changes.items():
                df.at[idx, col] = value
        
        # Recalculate Difference
        df = recast_column_types(df)
        df["Difference"] = df["Budget"] - df["Actual"]
        st.session_state.draft_data[cat_type] = df

# Initialize draft state if needed
if 'draft_data' not in st.session_state:
    st.session_state.draft_data = {}
    st.session_state.current_week_start = None

# --- TAB NAVIGATION ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📈 Statistics", "⚙️ Budget Config", "📜 Transaction Log"])

# ========== TAB 1: DASHBOARD ==========
with tab1:
    st.header("📊 Weekly Financial Dashboard")
    
    # Initialize selected week to current week if not set
    if 'selected_week_start' not in st.session_state:
        st.session_state.selected_week_start = get_week_start(datetime.now().date())
    
    selected_week_start = st.session_state.selected_week_start
    selected_week_end = get_week_end(selected_week_start)
    
    # WEEKLY CALENDAR UI
    st.markdown("### 📅 Select Week")
    
    # Week navigation row
    col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns([1, 1, 3, 1, 1])
    
    with col_nav1:
        if st.button("⏮️ Prev Month", use_container_width=True):
            st.session_state.selected_week_start = selected_week_start - timedelta(days=28)
            st.rerun()
    
    with col_nav2:
        if st.button("◀️ Prev Week", use_container_width=True):
            st.session_state.selected_week_start = selected_week_start - timedelta(days=7)
            st.rerun()
    
    with col_nav3:
        # Display current week info
        week_label = get_week_label(selected_week_start)
        st.markdown(f"### 🗓️ {week_label}")
    
    with col_nav4:
        if st.button("Next Week ▶️", use_container_width=True):
            st.session_state.selected_week_start = selected_week_start + timedelta(days=7)
            st.rerun()
    
    with col_nav5:
        if st.button("Next Month ⏭️", use_container_width=True):
            st.session_state.selected_week_start = selected_week_start + timedelta(days=28)
            st.rerun()
    
    # Jump to current week button
    col_jump1, col_jump2, col_jump3 = st.columns([1, 2, 1])
    with col_jump2:
        current_week = get_week_start(datetime.now().date())
        if selected_week_start != current_week:
            if st.button("📍 Jump to Current Week", use_container_width=True):
                st.session_state.selected_week_start = current_week
                st.rerun()
    
    # Visual Calendar Grid
    st.markdown("---")
    
    # Get the month to display (use middle of selected week)
    display_month = selected_week_start + timedelta(days=3)
    month_start = date(display_month.year, display_month.month, 1)
    
    # Find first Monday before or on month start
    first_display_date = month_start - timedelta(days=month_start.weekday())
    
    # Month header
    st.markdown(f"#### {display_month.strftime('%B %Y')}")
    
    # Day headers
    day_cols = st.columns(7)
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, name in enumerate(day_names):
        day_cols[i].markdown(f"**{name}**")
    
    # Calendar grid (6 weeks max)
    current_date = first_display_date
    today = datetime.now().date()
    
    for week_row in range(6):
        week_cols = st.columns(7)
        row_week_start = get_week_start(current_date)
        
        for day_col in range(7):
            with week_cols[day_col]:
                day_num = current_date.day
                is_current_month = current_date.month == display_month.month
                is_selected_week = row_week_start == selected_week_start
                is_today = current_date == today
                
                # Style the button based on state
                if is_selected_week:
                    if is_today:
                        btn_label = f"🔵 **{day_num}**"
                    else:
                        btn_label = f"🟢 {day_num}"
                elif is_today:
                    btn_label = f"📍 {day_num}"
                elif not is_current_month:
                    btn_label = f"_{day_num}_"
                else:
                    btn_label = str(day_num)
                
                if st.button(btn_label, key=f"cal_{current_date}", use_container_width=True):
                    st.session_state.selected_week_start = row_week_start
                    st.rerun()
            
            current_date += timedelta(days=1)
        
        # Stop if we've gone past the month
        if current_date.month != display_month.month and current_date.day > 7:
            break
    
    # Legend
    st.caption("🟢 Selected Week | 📍 Today | Click any day to select that week")
    
    st.markdown("---")
    
    # Initialize or update draft data if week changed
    if st.session_state.current_week_start != selected_week_start:
        load_draft_data(selected_week_start)
    
    # Use draft data for display and totals
    df_income = st.session_state.draft_data['Income']
    df_bills = st.session_state.draft_data['Bills']
    df_expenses = st.session_state.draft_data['Expenses']
    df_savings = st.session_state.draft_data['Savings']
    df_debt = st.session_state.draft_data['Debt']
    
    # Calculate totals from DRAFT data (auto-updates on edit interactions)
    total_income_budget = df_income["Budget"].sum()
    total_income_actual = df_income["Actual"].sum()
    total_bills_budget = df_bills["Budget"].sum()
    total_bills_actual = df_bills["Actual"].sum()
    total_expenses_budget = df_expenses["Budget"].sum()
    total_expenses_actual = df_expenses["Actual"].sum()
    total_savings_budget = df_savings["Budget"].sum()
    total_savings_actual = df_savings["Actual"].sum()
    total_debt_budget = df_debt["Budget"].sum()
    total_debt_actual = df_debt["Actual"].sum()
    
    total_spending_budget = total_bills_budget + total_expenses_budget
    total_spending_actual = total_bills_actual + total_expenses_actual
    left_to_budget = total_income_actual - total_spending_actual - total_savings_actual - total_debt_actual
    
    # TOP SUMMARY
    st.markdown(f"### 💰 Weekly Summary: {selected_week_start.strftime('%b %d')} – {selected_week_end.strftime('%b %d, %Y')}")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("💰 Weekly Income", f"${total_income_actual:,.2f}", delta=f"Budget: ${total_income_budget:,.2f}")
    with col_s2:
        st.metric("💸 Weekly Expenses", f"${total_spending_actual:,.2f}", delta=f"Budget: ${total_spending_budget:,.2f}")
    with col_s3:
        st.metric("💎 Weekly Savings", f"${total_savings_actual:,.2f}")
    with col_s4:
        color = "🟢" if left_to_budget >= 0 else "🔴"
        st.metric(f"{color} Left to Budget", f"${left_to_budget:,.2f}")
    
    st.markdown("---")
    
    # SINGLE SAVE ALL BUTTON
    if st.button("💾 SAVE WEEKLY TRANSACTIONS", type="primary", use_container_width=True):
        # Helper function to save category data for the week
        def save_category_data(edited_df, cat_type):
            for _, row in edited_df.iterrows():
                # Update budget in config (convert weekly back to monthly for storage)
                budget_mask = (st.session_state.df_budget_config['Category'] == row['Category']) & \
                              (st.session_state.df_budget_config['Type'] == cat_type)
                if budget_mask.any():
                    # Store as monthly budget (weekly * 4.33)
                    st.session_state.df_budget_config.loc[budget_mask, 'Budget'] = round(row['Budget'] * 4.33, 2)
                # Update or insert transaction (use week start date as the date)
                mask = (st.session_state.df_transactions['Date'] == str(selected_week_start)) & \
                       (st.session_state.df_transactions['Category'] == row['Category']) & \
                       (st.session_state.df_transactions['Type'] == cat_type)
                if mask.any():
                    st.session_state.df_transactions.loc[mask, 'Actual'] = row['Actual']
                else:
                    if row['Actual'] != 0:  # Only save non-zero values
                        new_row = pd.DataFrame([{"Date": str(selected_week_start), "Category": row['Category'], "Type": cat_type, "Actual": row['Actual']}])
                        st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, new_row], ignore_index=True)
        
        # Save all categories (will be populated after editors are created)
        st.session_state.pending_save = True
    
    # SPREADSHEET VIEW
    col_main1, col_main2 = st.columns(2)
    
    with col_main1:
        # INCOME
        st.markdown("### 💰 INCOME")
        edited_income = st.data_editor(
            df_income,
            column_config={
                "Category": st.column_config.TextColumn("Income Source", disabled=True),
                "Budget": st.column_config.NumberColumn("Expected ($)", format="$%.2f"),
                "Actual": st.column_config.NumberColumn("Actual ($)", format="$%.2f"),
                "Difference": st.column_config.NumberColumn("Diff ($)", format="$%.2f", disabled=True),
            },
            hide_index=True,
            key="income_editor",
            on_change=recalc_callback,
            args=("Income",),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # BILLS
        st.markdown("### 🧾 BILLS")
        edited_bills = st.data_editor(
            df_bills,
            column_config={
                "Category": st.column_config.TextColumn("Bill Name", disabled=True),
                "Budget": st.column_config.NumberColumn("Budget ($)", format="$%.2f"),
                "Actual": st.column_config.NumberColumn("Actual ($)", format="$%.2f"),
                "Difference": st.column_config.NumberColumn("Diff ($)", format="$%.2f", disabled=True),
            },
            hide_index=True,
            key="bills_editor",
            on_change=recalc_callback,
            args=("Bills",),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # EXPENSES
        st.markdown("### 💸 EXPENSES")
        edited_expenses = st.data_editor(
            df_expenses,
            column_config={
                "Category": st.column_config.TextColumn("Expense Name", disabled=True),
                "Budget": st.column_config.NumberColumn("Budget ($)", format="$%.2f"),
                "Actual": st.column_config.NumberColumn("Actual ($)", format="$%.2f"),
                "Difference": st.column_config.NumberColumn("Diff ($)", format="$%.2f", disabled=True),
            },
            hide_index=True,
            key="expenses_editor",
            on_change=recalc_callback,
            args=("Expenses",),
            use_container_width=True
        )
    
    with col_main2:
        # SAVINGS
        st.markdown("### 💎 SAVINGS")
        edited_savings = st.data_editor(
            df_savings,
            column_config={
                "Category": st.column_config.TextColumn("Savings Goal", disabled=True),
                "Budget": st.column_config.NumberColumn("Target ($)", format="$%.2f"),
                "Actual": st.column_config.NumberColumn("Saved ($)", format="$%.2f"),
                "Difference": st.column_config.NumberColumn("Diff ($)", format="$%.2f", disabled=True),
            },
            hide_index=True,
            key="savings_editor",
            on_change=recalc_callback,
            args=("Savings",),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # DEBT
        st.markdown("### 📉 DEBT")
        edited_debt = st.data_editor(
            df_debt,
            column_config={
                "Category": st.column_config.TextColumn("Debt Name", disabled=True),
                "Budget": st.column_config.NumberColumn("Payment ($)", format="$%.2f"),
                "Actual": st.column_config.NumberColumn("Paid ($)", format="$%.2f"),
                "Difference": st.column_config.NumberColumn("Diff ($)", format="$%.2f", disabled=True),
            },
            hide_index=True,
            key="debt_editor",
            on_change=recalc_callback,
            args=("Debt",),
            use_container_width=True
        )
    
    # Process save if button was clicked
    if st.session_state.get('pending_save', False):
        # Save all categories - convert weekly budgets back to monthly for storage
        for _, row in edited_income.iterrows():
            budget_mask = (st.session_state.df_budget_config['Category'] == row['Category']) & (st.session_state.df_budget_config['Type'] == 'Income')
            if budget_mask.any():
                st.session_state.df_budget_config.loc[budget_mask, 'Budget'] = round(row['Budget'] * 4.33, 2)
            mask = (st.session_state.df_transactions['Date'] == str(selected_week_start)) & (st.session_state.df_transactions['Category'] == row['Category']) & (st.session_state.df_transactions['Type'] == 'Income')
            if mask.any():
                st.session_state.df_transactions.loc[mask, 'Actual'] = row['Actual']
            elif row['Actual'] != 0:
                new_row = pd.DataFrame([{"Date": str(selected_week_start), "Category": row['Category'], "Type": "Income", "Actual": row['Actual']}])
                st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, new_row], ignore_index=True)
        
        for _, row in edited_bills.iterrows():
            budget_mask = (st.session_state.df_budget_config['Category'] == row['Category']) & (st.session_state.df_budget_config['Type'] == 'Bills')
            if budget_mask.any():
                st.session_state.df_budget_config.loc[budget_mask, 'Budget'] = round(row['Budget'] * 4.33, 2)
            mask = (st.session_state.df_transactions['Date'] == str(selected_week_start)) & (st.session_state.df_transactions['Category'] == row['Category']) & (st.session_state.df_transactions['Type'] == 'Bills')
            if mask.any():
                st.session_state.df_transactions.loc[mask, 'Actual'] = row['Actual']
            elif row['Actual'] != 0:
                new_row = pd.DataFrame([{"Date": str(selected_week_start), "Category": row['Category'], "Type": "Bills", "Actual": row['Actual']}])
                st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, new_row], ignore_index=True)
        
        for _, row in edited_expenses.iterrows():
            budget_mask = (st.session_state.df_budget_config['Category'] == row['Category']) & (st.session_state.df_budget_config['Type'] == 'Expenses')
            if budget_mask.any():
                st.session_state.df_budget_config.loc[budget_mask, 'Budget'] = round(row['Budget'] * 4.33, 2)
            mask = (st.session_state.df_transactions['Date'] == str(selected_week_start)) & (st.session_state.df_transactions['Category'] == row['Category']) & (st.session_state.df_transactions['Type'] == 'Expenses')
            if mask.any():
                st.session_state.df_transactions.loc[mask, 'Actual'] = row['Actual']
            elif row['Actual'] != 0:
                new_row = pd.DataFrame([{"Date": str(selected_week_start), "Category": row['Category'], "Type": "Expenses", "Actual": row['Actual']}])
                st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, new_row], ignore_index=True)
        
        for _, row in edited_savings.iterrows():
            budget_mask = (st.session_state.df_budget_config['Category'] == row['Category']) & (st.session_state.df_budget_config['Type'] == 'Savings')
            if budget_mask.any():
                st.session_state.df_budget_config.loc[budget_mask, 'Budget'] = round(row['Budget'] * 4.33, 2)
            mask = (st.session_state.df_transactions['Date'] == str(selected_week_start)) & (st.session_state.df_transactions['Category'] == row['Category']) & (st.session_state.df_transactions['Type'] == 'Savings')
            if mask.any():
                st.session_state.df_transactions.loc[mask, 'Actual'] = row['Actual']
            elif row['Actual'] != 0:
                new_row = pd.DataFrame([{"Date": str(selected_week_start), "Category": row['Category'], "Type": "Savings", "Actual": row['Actual']}])
                st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, new_row], ignore_index=True)
        
        for _, row in edited_debt.iterrows():
            budget_mask = (st.session_state.df_budget_config['Category'] == row['Category']) & (st.session_state.df_budget_config['Type'] == 'Debt')
            if budget_mask.any():
                st.session_state.df_budget_config.loc[budget_mask, 'Budget'] = round(row['Budget'] * 4.33, 2)
            mask = (st.session_state.df_transactions['Date'] == str(selected_week_start)) & (st.session_state.df_transactions['Category'] == row['Category']) & (st.session_state.df_transactions['Type'] == 'Debt')
            if mask.any():
                st.session_state.df_transactions.loc[mask, 'Actual'] = row['Actual']
            elif row['Actual'] != 0:
                new_row = pd.DataFrame([{"Date": str(selected_week_start), "Category": row['Category'], "Type": "Debt", "Actual": row['Actual']}])
                st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, new_row], ignore_index=True)
        
        save_df(st.session_state.df_budget_config, 'budget_config.csv')
        save_df(st.session_state.df_transactions, 'transactions.csv')
        st.session_state.pending_save = False
        week_label = get_week_label(selected_week_start)
        st.success(f"✅ All transactions saved for {week_label}!")
        st.rerun()


# ========== TAB 2: STATISTICS ==========
with tab2:
    st.header("📈 Financial Statistics")
    
    if st.session_state.df_transactions.empty:
        st.info("📝 No transactions recorded yet. Add transactions in the Dashboard to see statistics.")
    else:
        # Prepare transaction data
        df_txns = st.session_state.df_transactions.copy()
        df_txns['Date'] = pd.to_datetime(df_txns['Date'])
        df_txns['Month'] = df_txns['Date'].dt.to_period('M').astype(str)
        df_txns['Week'] = df_txns['Date'].dt.isocalendar().week
        
        # View Mode Selector
        st.markdown("### 🔍 View Mode")
        view_mode = st.radio("Select View", ["📅 Weekly", "📆 Monthly"], horizontal=True, key="view_mode")
        
        st.markdown("### 📅 Date Range Filter")
        
        # Quick select buttons
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        with col_q1:
            if st.button("This Month", use_container_width=True):
                today = datetime.now()
                st.session_state.stats_start_val = date(today.year, today.month, 1)
                st.session_state.stats_end_val = today.date()
                st.rerun()
        with col_q2:
            if st.button("Last Month", use_container_width=True):
                today = datetime.now()
                first_day_this_month = date(today.year, today.month, 1)
                last_month_end = first_day_this_month - timedelta(days=1)
                last_month_start = date(last_month_end.year, last_month_end.month, 1)
                st.session_state.stats_start_val = last_month_start
                st.session_state.stats_end_val = last_month_end
                st.rerun()
        with col_q3:
            if st.button("Last 3 Months", use_container_width=True):
                today = datetime.now()
                st.session_state.stats_start_val = (today - timedelta(days=90)).date()
                st.session_state.stats_end_val = today.date()
                st.rerun()
        with col_q4:
            if st.button("This Year", use_container_width=True):
                today = datetime.now()
                st.session_state.stats_start_val = date(today.year, 1, 1)
                st.session_state.stats_end_val = today.date()
                st.rerun()
        
        # Date range inputs
        col_f1, col_f2 = st.columns(2)
        default_start = st.session_state.get('stats_start_val', df_txns['Date'].min().date())
        default_end = st.session_state.get('stats_end_val', df_txns['Date'].max().date())
        with col_f1:
            stats_start = st.date_input("From", value=default_start, key="stats_start")
        with col_f2:
            stats_end = st.date_input("To", value=default_end, key="stats_end")
        
        # Filter data
        mask = (df_txns['Date'].dt.date >= stats_start) & (df_txns['Date'].dt.date <= stats_end)
        df_filtered = df_txns[mask]
        
        if df_filtered.empty:
            st.warning("No transactions in selected date range.")
        else:
            st.markdown("---")
            
            # Summary Metrics
            st.markdown("### 💰 Summary")
            total_income = df_filtered[df_filtered['Type'] == 'Income']['Actual'].sum()
            total_expenses = df_filtered[df_filtered['Type'].isin(['Bills', 'Expenses'])]['Actual'].sum()
            total_savings = df_filtered[df_filtered['Type'] == 'Savings']['Actual'].sum()
            total_debt = df_filtered[df_filtered['Type'] == 'Debt']['Actual'].sum()
            net_balance = total_income - total_expenses - total_savings - total_debt
            
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            with col_m1:
                st.metric("💵 Income", f"${total_income:,.2f}")
            with col_m2:
                st.metric("💸 Expenses", f"${total_expenses:,.2f}")
            with col_m3:
                st.metric("💎 Savings", f"${total_savings:,.2f}")
            with col_m4:
                st.metric("📉 Debt Paid", f"${total_debt:,.2f}")
            with col_m5:
                color = "🟢" if net_balance >= 0 else "🔴"
                st.metric(f"{color} Net Balance", f"${net_balance:,.2f}")
            
            st.markdown("---")
            
            # Charts Row 1
            col_c1, col_c2 = st.columns(2)
            
            with col_c1:
                if "Monthly" in view_mode:
                    st.markdown("### 📊 Income vs Expenses by Month")
                    # Group by month
                    income_by_month = df_filtered[df_filtered['Type'] == 'Income'].groupby('Month')['Actual'].sum().reset_index()
                    income_by_month.columns = ['Period', 'Income']
                    
                    expenses_by_month = df_filtered[df_filtered['Type'].isin(['Bills', 'Expenses'])].groupby('Month')['Actual'].sum().reset_index()
                    expenses_by_month.columns = ['Period', 'Expenses']
                    
                    # Merge
                    period_data = pd.merge(income_by_month, expenses_by_month, on='Period', how='outer').fillna(0)
                    period_data = period_data.sort_values('Period')
                else:
                    st.markdown("### 📊 Income vs Expenses by Week")
                    # Group by week - create week label
                    df_filtered_copy = df_filtered.copy()
                    df_filtered_copy['WeekLabel'] = df_filtered_copy['Date'].apply(lambda d: f"Wk {get_week_number(d)}")
                    
                    income_by_week = df_filtered_copy[df_filtered_copy['Type'] == 'Income'].groupby('WeekLabel')['Actual'].sum().reset_index()
                    income_by_week.columns = ['Period', 'Income']
                    
                    expenses_by_week = df_filtered_copy[df_filtered_copy['Type'].isin(['Bills', 'Expenses'])].groupby('WeekLabel')['Actual'].sum().reset_index()
                    expenses_by_week.columns = ['Period', 'Expenses']
                    
                    # Merge
                    period_data = pd.merge(income_by_week, expenses_by_week, on='Period', how='outer').fillna(0)
                    period_data = period_data.sort_values('Period')
                
                if not period_data.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=period_data['Period'], 
                        y=period_data['Income'], 
                        name='💰 Income', 
                        marker=dict(
                            color='#10b981',
                            line=dict(color='#059669', width=1)
                        )
                    ))
                    fig.add_trace(go.Bar(
                        x=period_data['Period'], 
                        y=period_data['Expenses'], 
                        name='💸 Expenses', 
                        marker=dict(
                            color='#f43f5e',
                            line=dict(color='#e11d48', width=1)
                        )
                    ))
                    fig.update_layout(
                        barmode='group',
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color='#e0e0e0', family='Inter'),
                        legend=dict(
                            orientation="h", 
                            yanchor="bottom", 
                            y=1.02, 
                            xanchor="right", 
                            x=1,
                            bgcolor='rgba(30,41,59,0.8)',
                            bordercolor='rgba(99,102,241,0.3)',
                            borderwidth=1
                        ),
                        xaxis=dict(
                            showgrid=False,
                            tickfont=dict(color='#94a3b8')
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(99,102,241,0.1)',
                            tickfont=dict(color='#94a3b8'),
                            tickprefix='$'
                        ),
                        margin=dict(l=10, r=10, t=30, b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data to display chart")
            
            with col_c2:
                st.markdown("### 🥧 Spending by Category")
                spending = df_filtered[df_filtered['Type'].isin(['Bills', 'Expenses'])]
                if not spending.empty:
                    spending_by_cat = spending.groupby('Category')['Actual'].sum().reset_index()
                    spending_by_cat = spending_by_cat[spending_by_cat['Actual'] > 0]
                    
                    if not spending_by_cat.empty:
                        # Premium color palette
                        colors = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#14b8a6']
                        fig = px.pie(
                            spending_by_cat, 
                            values='Actual', 
                            names='Category', 
                            hole=0.5,
                            color_discrete_sequence=colors
                        )
                        fig.update_traces(
                            textposition='outside',
                            textinfo='label+percent',
                            textfont=dict(color='#e0e0e0', size=11),
                            marker=dict(line=dict(color='#1a1a2e', width=2))
                        )
                        fig.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(color='#e0e0e0', family='Inter'),
                            legend=dict(
                                bgcolor='rgba(30,41,59,0.8)',
                                bordercolor='rgba(99,102,241,0.3)',
                                borderwidth=1,
                                font=dict(color='#94a3b8')
                            ),
                            margin=dict(l=10, r=10, t=30, b=10),
                            annotations=[dict(
                                text='Spending',
                                x=0.5, y=0.5,
                                font=dict(size=14, color='#94a3b8'),
                                showarrow=False
                            )]
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No spending data to display")
                else:
                    st.info("No spending data to display")
            
            st.markdown("---")
            
            # Charts Row 2
            col_c3, col_c4 = st.columns(2)
            
            with col_c3:
                st.markdown("### 📊 Budget vs Actual")
                # Get budget data
                budget_data = st.session_state.df_budget_config.copy()
                actual_by_cat = df_filtered.groupby(['Category', 'Type'])['Actual'].sum().reset_index()
                
                # Merge budget and actual
                comparison = pd.merge(budget_data[['Category', 'Type', 'Budget']], actual_by_cat, 
                                      on=['Category', 'Type'], how='left').fillna(0)
                comparison = comparison[comparison['Type'].isin(['Bills', 'Expenses'])]
                
                if not comparison.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        name='📋 Budget', 
                        x=comparison['Category'], 
                        y=comparison['Budget'], 
                        marker=dict(color='#6366f1', line=dict(color='#4f46e5', width=1))
                    ))
                    fig.add_trace(go.Bar(
                        name='💳 Actual', 
                        x=comparison['Category'], 
                        y=comparison['Actual'], 
                        marker=dict(color='#22c55e', line=dict(color='#16a34a', width=1))
                    ))
                    fig.update_layout(
                        barmode='group',
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color='#e0e0e0', family='Inter'),
                        xaxis=dict(tickangle=-45, tickfont=dict(color='#94a3b8')),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(99,102,241,0.1)',
                            tickfont=dict(color='#94a3b8'),
                            tickprefix='$'
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1,
                            bgcolor='rgba(30,41,59,0.8)',
                            bordercolor='rgba(99,102,241,0.3)',
                            borderwidth=1
                        ),
                        margin=dict(l=10, r=10, t=30, b=80)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No budget comparison data")
            
            with col_c4:
                st.markdown("### 💎 Savings Progress")
                savings_data = df_filtered[df_filtered['Type'] == 'Savings']
                if not savings_data.empty:
                    savings_by_goal = savings_data.groupby('Category')['Actual'].sum().reset_index()
                    
                    # Get budget targets
                    savings_budget = st.session_state.df_budget_config[st.session_state.df_budget_config['Type'] == 'Savings'][['Category', 'Budget']]
                    savings_progress = pd.merge(savings_budget, savings_by_goal, on='Category', how='left').fillna(0)
                    # Avoid division by zero - set progress to 0 if budget is 0, otherwise calculate normally
                    savings_progress['Progress %'] = savings_progress.apply(
                        lambda r: 0.0 if r['Budget'] == 0 else min((r['Actual'] / r['Budget'] * 100), 100.0), axis=1
                    )
                    
                    for _, row in savings_progress.iterrows():
                        st.markdown(f"**{row['Category']}**")
                        st.progress(min(row['Progress %'] / 100, 1.0))
                        st.caption(f"${row['Actual']:,.2f} / ${row['Budget']:,.2f} ({row['Progress %']:.1f}%)")
                else:
                    st.info("No savings data to display")
            
            st.markdown("---")
            
            # Monthly Trend
            st.markdown("### 📅 Monthly Trend")
            monthly_data = df_filtered.groupby(['Month', 'Type'])['Actual'].sum().reset_index()
            monthly_pivot = monthly_data.pivot(index='Month', columns='Type', values='Actual').fillna(0).reset_index()
            
            if not monthly_pivot.empty:
                fig = go.Figure()
                colors = {'Income': '#10b981', 'Bills': '#f59e0b', 'Expenses': '#f43f5e', 'Savings': '#8b5cf6', 'Debt': '#64748b'}
                
                if 'Income' in monthly_pivot.columns:
                    fig.add_trace(go.Bar(name='💰 Income', x=monthly_pivot['Month'], y=monthly_pivot['Income'], 
                                         marker=dict(color=colors['Income'], line=dict(color='#059669', width=1))))
                if 'Bills' in monthly_pivot.columns:
                    fig.add_trace(go.Bar(name='🧾 Bills', x=monthly_pivot['Month'], y=monthly_pivot['Bills'], 
                                         marker=dict(color=colors['Bills'], line=dict(color='#d97706', width=1))))
                if 'Expenses' in monthly_pivot.columns:
                    fig.add_trace(go.Bar(name='💸 Expenses', x=monthly_pivot['Month'], y=monthly_pivot['Expenses'], 
                                         marker=dict(color=colors['Expenses'], line=dict(color='#e11d48', width=1))))
                if 'Savings' in monthly_pivot.columns:
                    fig.add_trace(go.Bar(name='💎 Savings', x=monthly_pivot['Month'], y=monthly_pivot['Savings'], 
                                         marker=dict(color=colors['Savings'], line=dict(color='#7c3aed', width=1))))
                
                fig.update_layout(
                    barmode='group',
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color='#e0e0e0', family='Inter'),
                    xaxis=dict(tickfont=dict(color='#94a3b8')),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(99,102,241,0.1)',
                        tickfont=dict(color='#94a3b8'),
                        tickprefix='$'
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        bgcolor='rgba(30,41,59,0.8)',
                        bordercolor='rgba(99,102,241,0.3)',
                        borderwidth=1
                    ),
                    margin=dict(l=10, r=10, t=50, b=10)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Top Spending Categories
            st.markdown("### 🏆 Top Spending Categories")
            top_spending = spending.groupby('Category')['Actual'].sum().sort_values(ascending=False).head(5).reset_index()
            if not top_spending.empty:
                fig = go.Figure(go.Bar(
                    x=top_spending['Actual'],
                    y=top_spending['Category'],
                    orientation='h',
                    marker=dict(
                        color=top_spending['Actual'],
                        colorscale=[[0, '#6366f1'], [0.5, '#a855f7'], [1, '#f43f5e']],
                        line=dict(color='rgba(0,0,0,0.3)', width=1)
                    ),
                    text=[f'${v:,.0f}' for v in top_spending['Actual']],
                    textposition='outside',
                    textfont=dict(color='#e0e0e0')
                ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color='#e0e0e0', family='Inter'),
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(99,102,241,0.1)',
                        tickfont=dict(color='#94a3b8'),
                        tickprefix='$'
                    ),
                    yaxis=dict(tickfont=dict(color='#94a3b8')),
                    showlegend=False,
                    margin=dict(l=10, r=60, t=10, b=10)
                )
                st.plotly_chart(fig, use_container_width=True)

# ========== TAB 3: BUDGET CONFIG ==========
with tab3:
    st.header("⚙️ Budget Configuration")
    st.markdown("Set default budget/expected values for specific date ranges. These will show as the 'Budget' column in the Dashboard.")
    
    st.markdown("---")
    
    # Date range selector
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        cfg_start = st.date_input("Start Date", value=date(2026, 1, 1), key="cfg_start")
    with col_cfg2:
        cfg_end = st.date_input("End Date", value=date(2026, 12, 31), key="cfg_end")
    
    st.markdown("### Edit Budget Defaults")
    st.info("Edit the 'Budget' column to set expected values. Changes will apply to the selected date range.")
    
    # Editable budget config table
    edited_config = st.data_editor(
        st.session_state.df_budget_config,
        column_config={
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Type": st.column_config.SelectboxColumn("Type", options=["Income", "Bills", "Expenses", "Savings", "Debt"], width="small"),
            "Budget": st.column_config.NumberColumn("Budget ($)", format="$%.2f"),
            "Start Date": st.column_config.TextColumn("Start Date"),
            "End Date": st.column_config.TextColumn("End Date"),
        },
        hide_index=True,
        num_rows="dynamic",
        key="budget_config_editor",
        use_container_width=True
    )
    
    col_save1, col_save2 = st.columns(2)
    with col_save1:
        if st.button("💾 Save Budget Configuration", type="primary"):
            st.session_state.df_budget_config = edited_config
            save_df(st.session_state.df_budget_config, 'budget_config.csv')
            st.success("Budget configuration saved! Dashboard will now use these values.")
            st.rerun()
    
    with col_save2:
        if st.button("🔄 Apply Date Range to All"):
            st.session_state.df_budget_config['Start Date'] = str(cfg_start)
            st.session_state.df_budget_config['End Date'] = str(cfg_end)
            save_df(st.session_state.df_budget_config, 'budget_config.csv')
            st.success(f"Applied date range {cfg_start} to {cfg_end} to all categories!")
            st.rerun()

# ========== TAB 4: TRANSACTION LOG ==========
with tab4:
    st.header("📜 Transaction Log")
    st.markdown("View all saved transactions by date.")
    
    if not st.session_state.df_transactions.empty:
        # Get unique dates
        unique_dates = st.session_state.df_transactions['Date'].unique()
        
        st.markdown(f"**{len(unique_dates)} dates with transactions**")
        
        # Summary by date
        date_summary = []
        for d in sorted(unique_dates, reverse=True):
            txns = st.session_state.df_transactions[st.session_state.df_transactions['Date'] == d]
            total_income = txns[txns['Type'] == 'Income']['Actual'].sum()
            total_expenses = txns[txns['Type'].isin(['Bills', 'Expenses'])]['Actual'].sum()
            date_summary.append({
                "Date": d,
                "Total Income": total_income,
                "Total Expenses": total_expenses,
                "Net": total_income - total_expenses
            })
        
        df_summary = pd.DataFrame(date_summary)
        st.dataframe(df_summary, use_container_width=True)
        
        st.markdown("---")
        
        # Select date to view/edit
        selected_log_date = st.selectbox("Select date to view details", unique_dates)
        
        if selected_log_date:
            st.markdown(f"### Transactions for {selected_log_date}")
            date_txns = st.session_state.df_transactions[st.session_state.df_transactions['Date'] == selected_log_date]
            
            edited_txns = st.data_editor(date_txns, num_rows="dynamic", key="log_editor", use_container_width=True)
            
            col_log1, col_log2 = st.columns(2)
            with col_log1:
                if st.button("💾 Save Changes"):
                    # Update transactions
                    st.session_state.df_transactions = st.session_state.df_transactions[st.session_state.df_transactions['Date'] != selected_log_date]
                    st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, edited_txns], ignore_index=True)
                    save_df(st.session_state.df_transactions, 'transactions.csv')
                    st.success("Transactions updated!")
                    st.rerun()
            
            with col_log2:
                if st.button("🗑️ Delete All for This Date", type="secondary"):
                    st.session_state.df_transactions = st.session_state.df_transactions[st.session_state.df_transactions['Date'] != selected_log_date]
                    save_df(st.session_state.df_transactions, 'transactions.csv')
                    st.success(f"Deleted all transactions for {selected_log_date}")
                    st.rerun()
    else:
        st.info("No transactions logged yet. Go to Dashboard, select a date, enter values, and save.")

# --- EXPORT ---
st.markdown("---")
st.markdown("## 📤 Export Data")

zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
    zip_file.writestr("budget_config.csv", st.session_state.df_budget_config.to_csv(index=False))
    zip_file.writestr("transactions.csv", st.session_state.df_transactions.to_csv(index=False))

st.download_button(
    label="Download Complete Data (ZIP)",
    data=zip_buffer.getvalue(),
    file_name="finance_data_export.zip",
    mime="application/zip"
)
