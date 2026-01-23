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

# --- THEME SYSTEM ---
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = "Dark 🌙"

col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    theme_mode = st.radio("Theme", ["Dark 🌙", "Light ☀️"], horizontal=True, key="theme_toggle", label_visibility="collapsed")
    st.session_state.theme_mode = theme_mode

# Dark Mode CSS
DARK_CSS = """
<style>
    /* Global Dark Theme */
    .stApp { background-color: #1a1a2e !important; }
    section[data-testid="stSidebar"] { display: none; }
    
    /* Text Color - White */
    h1, h2, h3, h4, h5, h6, p, span, label, div { 
        color: #ffffff !important; 
        font-family: 'Roboto', sans-serif; 
    }
    
    /* Header */
    header[data-testid="stHeader"] { background-color: #1a1a2e !important; }
    
    /* Data Editors / Tables - Dark Blue */
    div[data-testid="stDataEditor"], div[data-testid="stDataFrame"] {
        background-color: #16213e !important;
        color: white !important;
    }
    
    /* Force table text to be white */
    div[class*="stDataFrame"] div[class*="dvn-scroller"] {
        color: white !important;
    }
</style>
"""

# Light Mode CSS
LIGHT_CSS = """
<style>
    /* Global Light Theme */
    .stApp { background-color: #ffffff !important; }
    section[data-testid="stSidebar"] { display: none; }
    
    /* Text Color - Dark */
    h1, h2, h3, h4, h5, h6, p, span, label, div { 
        color: #000000 !important; 
        font-family: 'Roboto', sans-serif; 
    }
    
    /* Header */
    header[data-testid="stHeader"] { background-color: #ffffff !important; }
    
    /* Data Editors / Tables - White */
    div[data-testid="stDataEditor"], div[data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        color: black !important;
    }
</style>
"""

if "Dark" in theme_mode:
    st.markdown(DARK_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

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

# --- TAB NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "⚙️ Budget Config", "📜 Transaction Log"])

# ========== TAB 1: DASHBOARD ==========
with tab1:
    st.header("📊 Financial Dashboard")
    
    # DATE SELECTOR
    st.markdown("### 📅 Select Date")
    col_date1, col_date2, col_date3 = st.columns([2, 1, 3])
    with col_date1:
        selected_date = st.date_input("Transaction Date", value=st.session_state.selected_date, key="dashboard_date")
        st.session_state.selected_date = selected_date
    with col_date2:
        st.markdown(f"**{selected_date.strftime('%B %d, %Y')}**")
    
    st.markdown("---")
    
    # Build tables for each category
    df_income = build_category_table("Income", selected_date)
    df_bills = build_category_table("Bills", selected_date)
    df_expenses = build_category_table("Expenses", selected_date)
    df_savings = build_category_table("Savings", selected_date)
    df_debt = build_category_table("Debt", selected_date)
    
    # Calculate totals
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
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("💰 Total Income", f"${total_income_actual:,.2f}", delta=f"Budget: ${total_income_budget:,.2f}")
    with col_s2:
        st.metric("💸 Total Expenses", f"${total_spending_actual:,.2f}", delta=f"Budget: ${total_spending_budget:,.2f}")
    with col_s3:
        st.metric("💎 Total Savings", f"${total_savings_actual:,.2f}")
    with col_s4:
        color = "🟢" if left_to_budget >= 0 else "🔴"
        st.metric(f"{color} Left to Budget", f"${left_to_budget:,.2f}")
    
    st.markdown("---")
    
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
            use_container_width=True
        )
        
        if st.button("💾 Save Income", key="save_income"):
            for _, row in edited_income.iterrows():
                # Update budget in config
                budget_mask = (st.session_state.df_budget_config['Category'] == row['Category']) & \
                              (st.session_state.df_budget_config['Type'] == 'Income')
                if budget_mask.any():
                    st.session_state.df_budget_config.loc[budget_mask, 'Budget'] = row['Budget']
                # Update or insert transaction
                mask = (st.session_state.df_transactions['Date'] == str(selected_date)) & \
                       (st.session_state.df_transactions['Category'] == row['Category']) & \
                       (st.session_state.df_transactions['Type'] == 'Income')
                if mask.any():
                    st.session_state.df_transactions.loc[mask, 'Actual'] = row['Actual']
                else:
                    new_row = pd.DataFrame([{"Date": str(selected_date), "Category": row['Category'], "Type": "Income", "Actual": row['Actual']}])
                    st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, new_row], ignore_index=True)
            save_df(st.session_state.df_budget_config, 'budget_config.csv')
            save_df(st.session_state.df_transactions, 'transactions.csv')
            st.success("Income saved!")
            st.rerun()
        
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
            use_container_width=True
        )
        
        if st.button("💾 Save Bills", key="save_bills"):
            for _, row in edited_bills.iterrows():
                # Update budget in config
                budget_mask = (st.session_state.df_budget_config['Category'] == row['Category']) & \
                              (st.session_state.df_budget_config['Type'] == 'Bills')
                if budget_mask.any():
                    st.session_state.df_budget_config.loc[budget_mask, 'Budget'] = row['Budget']
                # Update or insert transaction
                mask = (st.session_state.df_transactions['Date'] == str(selected_date)) & \
                       (st.session_state.df_transactions['Category'] == row['Category']) & \
                       (st.session_state.df_transactions['Type'] == 'Bills')
                if mask.any():
                    st.session_state.df_transactions.loc[mask, 'Actual'] = row['Actual']
                else:
                    new_row = pd.DataFrame([{"Date": str(selected_date), "Category": row['Category'], "Type": "Bills", "Actual": row['Actual']}])
                    st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, new_row], ignore_index=True)
            save_df(st.session_state.df_budget_config, 'budget_config.csv')
            save_df(st.session_state.df_transactions, 'transactions.csv')
            st.success("Bills saved!")
            st.rerun()
        
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
            use_container_width=True
        )
        
        if st.button("💾 Save Expenses", key="save_expenses"):
            for _, row in edited_expenses.iterrows():
                # Update budget in config
                budget_mask = (st.session_state.df_budget_config['Category'] == row['Category']) & \
                              (st.session_state.df_budget_config['Type'] == 'Expenses')
                if budget_mask.any():
                    st.session_state.df_budget_config.loc[budget_mask, 'Budget'] = row['Budget']
                # Update or insert transaction
                mask = (st.session_state.df_transactions['Date'] == str(selected_date)) & \
                       (st.session_state.df_transactions['Category'] == row['Category']) & \
                       (st.session_state.df_transactions['Type'] == 'Expenses')
                if mask.any():
                    st.session_state.df_transactions.loc[mask, 'Actual'] = row['Actual']
                else:
                    new_row = pd.DataFrame([{"Date": str(selected_date), "Category": row['Category'], "Type": "Expenses", "Actual": row['Actual']}])
                    st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, new_row], ignore_index=True)
            save_df(st.session_state.df_budget_config, 'budget_config.csv')
            save_df(st.session_state.df_transactions, 'transactions.csv')
            st.success("Expenses saved!")
            st.rerun()
    
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
            use_container_width=True
        )
        
        if st.button("💾 Save Savings", key="save_savings"):
            for _, row in edited_savings.iterrows():
                # Update budget in config
                budget_mask = (st.session_state.df_budget_config['Category'] == row['Category']) & \
                              (st.session_state.df_budget_config['Type'] == 'Savings')
                if budget_mask.any():
                    st.session_state.df_budget_config.loc[budget_mask, 'Budget'] = row['Budget']
                # Update or insert transaction
                mask = (st.session_state.df_transactions['Date'] == str(selected_date)) & \
                       (st.session_state.df_transactions['Category'] == row['Category']) & \
                       (st.session_state.df_transactions['Type'] == 'Savings')
                if mask.any():
                    st.session_state.df_transactions.loc[mask, 'Actual'] = row['Actual']
                else:
                    new_row = pd.DataFrame([{"Date": str(selected_date), "Category": row['Category'], "Type": "Savings", "Actual": row['Actual']}])
                    st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, new_row], ignore_index=True)
            save_df(st.session_state.df_budget_config, 'budget_config.csv')
            save_df(st.session_state.df_transactions, 'transactions.csv')
            st.success("Savings saved!")
            st.rerun()
        
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
            use_container_width=True
        )
        
        if st.button("💾 Save Debt", key="save_debt"):
            for _, row in edited_debt.iterrows():
                # Update budget in config
                budget_mask = (st.session_state.df_budget_config['Category'] == row['Category']) & \
                              (st.session_state.df_budget_config['Type'] == 'Debt')
                if budget_mask.any():
                    st.session_state.df_budget_config.loc[budget_mask, 'Budget'] = row['Budget']
                # Update or insert transaction
                mask = (st.session_state.df_transactions['Date'] == str(selected_date)) & \
                       (st.session_state.df_transactions['Category'] == row['Category']) & \
                       (st.session_state.df_transactions['Type'] == 'Debt')
                if mask.any():
                    st.session_state.df_transactions.loc[mask, 'Actual'] = row['Actual']
                else:
                    new_row = pd.DataFrame([{"Date": str(selected_date), "Category": row['Category'], "Type": "Debt", "Actual": row['Actual']}])
                    st.session_state.df_transactions = pd.concat([st.session_state.df_transactions, new_row], ignore_index=True)
            save_df(st.session_state.df_budget_config, 'budget_config.csv')
            save_df(st.session_state.df_transactions, 'transactions.csv')
            st.success("Debt saved!")
            st.rerun()

# ========== TAB 2: BUDGET CONFIG ==========
with tab2:
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

# ========== TAB 3: TRANSACTION LOG ==========
with tab3:
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
