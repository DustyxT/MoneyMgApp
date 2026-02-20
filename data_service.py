"""
Data Service for Flet Native App
Wraps the existing backend data_service for direct use in the desktop app.
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid
import json

import sys

# Path to data files
# If frozen (exe), use the executable's directory. If script, use the script's directory.
if getattr(sys, 'frozen', False):
    DATA_DIR = Path(sys.executable).parent
else:
    DATA_DIR = Path(__file__).parent

BUDGET_FILE = DATA_DIR / "budget_config.csv"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"
PROFILE_FILE = DATA_DIR / "profile.json"

# Default budget configuration
DEFAULT_BUDGET = [
    {"Category": "Part-time Job", "Type": "Income", "Budget": 800},
    {"Category": "Allowance", "Type": "Income", "Budget": 500},
    {"Category": "Scholarships", "Type": "Income", "Budget": 0},
    {"Category": "Other Income", "Type": "Income", "Budget": 0},
    {"Category": "Rent", "Type": "Bills", "Budget": 800},
    {"Category": "Utilities", "Type": "Bills", "Budget": 100},
    {"Category": "Phone/Internet", "Type": "Bills", "Budget": 50},
    {"Category": "Insurance", "Type": "Bills", "Budget": 100},
    {"Category": "Groceries", "Type": "Expenses", "Budget": 300},
    {"Category": "Transport", "Type": "Expenses", "Budget": 150},
    {"Category": "Dining Out", "Type": "Expenses", "Budget": 100},
    {"Category": "Entertainment", "Type": "Expenses", "Budget": 80},
    {"Category": "Shopping", "Type": "Expenses", "Budget": 100},
    {"Category": "Health", "Type": "Expenses", "Budget": 50},
    {"Category": "Education", "Type": "Expenses", "Budget": 50},
    {"Category": "Emergency Fund", "Type": "Savings", "Budget": 100},
    {"Category": "Travel Fund", "Type": "Savings", "Budget": 50},
    {"Category": "Future Goals", "Type": "Savings", "Budget": 50},
    {"Category": "Credit Card", "Type": "Debt", "Budget": 0},
    {"Category": "Student Loan", "Type": "Debt", "Budget": 0},
    {"Category": "Other Debt", "Type": "Debt", "Budget": 0},
    {"Category": "Stock Market", "Type": "Investments", "Budget": 0},
    {"Category": "Cryptocurrency", "Type": "Investments", "Budget": 0},
    {"Category": "ETFs/Index Funds", "Type": "Investments", "Budget": 0},
    {"Category": "Micro-investing", "Type": "Investments", "Budget": 0},
]


def load_budget_config() -> pd.DataFrame:
    """Load budget configuration from CSV or create default."""
    try:
        if BUDGET_FILE.exists() and BUDGET_FILE.stat().st_size > 0:
            return pd.read_csv(BUDGET_FILE)
    except Exception:
        pass
    df = pd.DataFrame(DEFAULT_BUDGET)
    df.to_csv(BUDGET_FILE, index=False)
    return df


def save_budget_config(df: pd.DataFrame):
    """Save budget configuration to CSV."""
    df.to_csv(BUDGET_FILE, index=False)


def load_transactions() -> pd.DataFrame:
    """Load transactions from CSV or create empty DataFrame."""
    try:
        if TRANSACTIONS_FILE.exists() and TRANSACTIONS_FILE.stat().st_size > 0:
            df = pd.read_csv(TRANSACTIONS_FILE)
            if "id" not in df.columns:
                df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
                save_transactions(df)
            return df
    except Exception:
        pass
    df = pd.DataFrame(columns=["id", "Date", "Category", "Type", "Actual", "Note"])
    df.to_csv(TRANSACTIONS_FILE, index=False)
    return df


def save_transactions(df: pd.DataFrame):
    """Save transactions to CSV."""
    # Ensure Date is saved as YYYY-MM-DD string
    if "Date" in df.columns:
        # Convert to datetime first to handle mixed types
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        # Format as string
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        
    df.to_csv(TRANSACTIONS_FILE, index=False)


def add_transaction(date: str, category: str, cat_type: str, amount: float, note: str = "") -> str:
    """Add a new transaction and return its ID."""
    df = load_transactions()
    new_id = str(uuid.uuid4())
    
    new_row = pd.DataFrame([{
        "id": new_id,
        "Date": date,
        "Category": category,
        "Type": cat_type,
        "Actual": amount,
        "Note": note
    }])
    
    df = pd.concat([df, new_row], ignore_index=True)
    save_transactions(df)
    return new_id


def delete_transaction(transaction_id: str) -> bool:
    """Delete a transaction by ID."""
    df = load_transactions()
    if "id" not in df.columns:
        return False
    
    initial_len = len(df)
    df = df[df["id"] != transaction_id]
    
    if len(df) < initial_len:
        save_transactions(df)
        return True
    return False


# ===== RECURRING TRANSACTIONS =====
RECURRING_FILE = DATA_DIR / "recurring_transactions.csv"

def load_recurring_transactions() -> pd.DataFrame:
    """Load recurring transactions from CSV."""
    try:
        if RECURRING_FILE.exists() and RECURRING_FILE.stat().st_size > 0:
            return pd.read_csv(RECURRING_FILE)
    except Exception:
        pass
    return pd.DataFrame(columns=["id", "Category", "Type", "Amount", "Recurrence", "Note", "CreatedDate", "TargetMonth"])

def save_recurring_transactions(df: pd.DataFrame):
    """Save recurring transactions to CSV."""
    df.to_csv(RECURRING_FILE, index=False)

def add_recurring_transaction(category: str, cat_type: str, amount: float, recurrence: str, note: str = "", target_month: str = "") -> str:
    """Add a new recurring transaction. Recurrence: 'permanent' or 'monthly'.
    For 'monthly', target_month should be 'YYYY-MM' format."""
    df = load_recurring_transactions()
    new_id = str(uuid.uuid4())
    new_row = pd.DataFrame([{
        "id": new_id,
        "Category": category,
        "Type": cat_type,
        "Amount": amount,
        "Recurrence": recurrence,
        "Note": note,
        "CreatedDate": datetime.now().strftime("%Y-%m-%d"),
        "TargetMonth": target_month if recurrence == "monthly" else "",
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    save_recurring_transactions(df)
    return new_id

def delete_recurring_transaction(rec_id: str) -> bool:
    """Delete a recurring transaction by ID."""
    df = load_recurring_transactions()
    if "id" not in df.columns:
        return False
    initial_len = len(df)
    df = df[df["id"] != rec_id]
    if len(df) < initial_len:
        save_recurring_transactions(df)
        return True
    return False


def get_week_dates(date: datetime) -> tuple:
    """Get Monday-Sunday week range for a given date."""
    # Find the Monday of the current week
    # weekday(): Monday is 0, Sunday is 6
    days_since_monday = date.weekday() 
    start_date = date - timedelta(days=days_since_monday)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=6)
    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start_date, end_date


WEEKLY_BUDGETS_FILE = DATA_DIR / "weekly_budgets.csv"

def load_weekly_budgets() -> pd.DataFrame:
    """Load weekly budget overrides."""
    try:
        if WEEKLY_BUDGETS_FILE.exists() and WEEKLY_BUDGETS_FILE.stat().st_size > 0:
            return pd.read_csv(WEEKLY_BUDGETS_FILE)
    except Exception:
        pass
    return pd.DataFrame(columns=["WeekStart", "Category", "Amount"])

def save_weekly_budgets(df: pd.DataFrame):
    """Save weekly budget overrides."""
    df.to_csv(WEEKLY_BUDGETS_FILE, index=False)

def set_weekly_budget_override(week_start: str, category: str, amount: float):
    """Set a specific budget amount for a specific week."""
    df = load_weekly_budgets()
    
    # Check if override exists
    if len(df) > 0:
        mask = (df["WeekStart"] == week_start) & (df["Category"] == category)
        if mask.any():
            idx = df[mask].index[0]
            df.at[idx, "Amount"] = amount
            save_weekly_budgets(df)
            return

    # Create new override
    new_row = pd.DataFrame([{
        "WeekStart": week_start,
        "Category": category,
        "Amount": amount
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    save_weekly_budgets(df)


def get_weekly_data(start_date: str, end_date: str) -> Dict[str, Any]:
    """Get all data for a specific week."""
    transactions = load_transactions()
    budget = load_budget_config()
    
    # Filter transactions by date range
    if len(transactions) > 0 and "Date" in transactions.columns:
        transactions["Date"] = pd.to_datetime(transactions["Date"], errors="coerce")
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        week_trans = transactions[(transactions["Date"] >= start) & (transactions["Date"] <= end)]
    else:
        week_trans = pd.DataFrame(columns=["id", "Date", "Category", "Type", "Actual", "Note"])
    
    # Inject recurring transactions
    recurring = load_recurring_transactions()
    if len(recurring) > 0:
        start_dt = pd.to_datetime(start_date)
        recurring_rows = []
        for _, rec in recurring.iterrows():
            created = pd.to_datetime(rec.get("CreatedDate", "2000-01-01"), errors="coerce")
            # Only include if created on or before this week's end
            if created > pd.to_datetime(end_date):
                continue
            
            include = False
            if rec["Recurrence"] == "permanent":
                include = True
            elif rec["Recurrence"] == "monthly":
                # Only include if this week overlaps with the target month
                target = str(rec.get("TargetMonth", ""))
                if target and len(target) >= 7:
                    target_year = int(target[:4])
                    target_mon = int(target[5:7])
                    start_dt_parsed = pd.to_datetime(start_date)
                    end_dt_parsed = pd.to_datetime(end_date)
                    # Week overlaps the target month if start or end is in that month
                    if ((start_dt_parsed.year == target_year and start_dt_parsed.month == target_mon) or
                        (end_dt_parsed.year == target_year and end_dt_parsed.month == target_mon)):
                        include = True
            
            if include:
                # Check if there's already a manual transaction for this category this week
                existing = week_trans[
                    (week_trans["Category"] == rec["Category"]) & 
                    (week_trans["Type"] == rec["Type"])
                ]
                if len(existing) == 0:
                    recurring_rows.append({
                        "id": f"recurring_{rec['id']}",
                        "Date": start_date,
                        "Category": rec["Category"],
                        "Type": rec["Type"],
                        "Actual": rec["Amount"],
                        "Note": f"🔄 {rec['Recurrence'].title()}"
                    })
        
        if recurring_rows:
            rec_df = pd.DataFrame(recurring_rows)
            week_trans = pd.concat([week_trans, rec_df], ignore_index=True)
    
    # Calculate totals by type
    income_total = week_trans[week_trans["Type"] == "Income"]["Actual"].sum() if len(week_trans) > 0 else 0
    expenses_total = week_trans[week_trans["Type"].isin(["Expenses", "Bills"])]["Actual"].sum() if len(week_trans) > 0 else 0
    savings_total = week_trans[week_trans["Type"] == "Savings"]["Actual"].sum() if len(week_trans) > 0 else 0
    investments_total = week_trans[week_trans["Type"] == "Investments"]["Actual"].sum() if len(week_trans) > 0 else 0
    
    weekly_overrides = load_weekly_budgets()
    
    # Build category summaries
    def get_category_data(cat_type: str) -> List[Dict]:
        budget_cats = budget[budget["Type"] == cat_type]
        
        result = []
        budget_cat_names = set()
        
        for _, row in budget_cats.iterrows():
            cat = row["Category"]
            budget_cat_names.add(cat)
            
            # Check for weekly override first
            override_amount = None
            if len(weekly_overrides) > 0:
                mask = (weekly_overrides["WeekStart"] == start_date) & (weekly_overrides["Category"] == cat)
                if mask.any():
                    override_amount = weekly_overrides[mask].iloc[0]["Amount"]
            
            if override_amount is not None:
                weekly_budget = override_amount
            else:
                weekly_budget = row["Budget"] / 4.33  # Monthly to weekly
                
            actual = week_trans[week_trans["Category"] == cat]["Actual"].sum() if len(week_trans) > 0 else 0
            result.append({
                "category": cat,
                "budget": round(weekly_budget, 2),
                "actual": round(actual, 2),
            })
        
        # Also include custom transaction categories not in budget config
        if len(week_trans) > 0:
            type_trans = week_trans[week_trans["Type"] == cat_type]
            for cat in type_trans["Category"].unique():
                if cat not in budget_cat_names:
                    actual = type_trans[type_trans["Category"] == cat]["Actual"].sum()
                    result.append({
                        "category": cat,
                        "budget": 0,  # No budget for custom categories
                        "actual": round(actual, 2),
                    })
        
        return result
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "totals": {
            "income": round(income_total, 2),
            "expenses": round(expenses_total, 2),
            "savings": round(savings_total, 2),
            "investments": round(investments_total, 2),
            "balance": round(income_total - expenses_total - savings_total - investments_total, 2),
        },
        "income": get_category_data("Income"),
        "expenses": get_category_data("Expenses"),
        "bills": get_category_data("Bills"),
        "savings": get_category_data("Savings"),
        "investments": get_category_data("Investments"),
        "transactions": week_trans.to_dict("records") if len(week_trans) > 0 else [],
    }


def load_profile() -> Dict[str, Any]:
    """Load user profile."""
    try:
        if PROFILE_FILE.exists():
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {"name": "User", "picture": None}


def save_profile(data: Dict[str, Any]):
    """Save user profile."""
    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f)
        
        
def update_actual_value(start_date: str, end_date: str, category: str, 
                          data_type: str, amount: float):
    """
    Update the transaction value for a category in the date range.
    Strategy: Remove existing transactions for this category in the week 
    and replace with a single transaction of the specified amount.
    This ensures the 'Actual' value in Dashboard matches exactly what user typed.
    """
    df = load_transactions()
    budget = load_budget_config()
    
    # Determine the actual Type from budget config
    cat_row = budget[budget["Category"] == category]
    if len(cat_row) > 0:
        actual_type = cat_row.iloc[0]["Type"]
    else:
        actual_type = data_type
    
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    mid_date = start + (end - start) / 2
    
    if len(df) > 0 and "Date" in df.columns:
        # Standardize date for comparison
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        
        # Identifty transactions to remove
        mask_to_remove = (df["Date"] >= start) & (df["Date"] <= end) & (df["Category"] == category)
        
        if mask_to_remove.any():
            # Remove them
            df = df[~mask_to_remove]
            save_transactions(df)
            
    # Add the single new transaction
    add_transaction(
        mid_date.strftime("%Y-%m-%d"),
        category,
        actual_type,
        amount,
        "Updated from dashboard"
    )

def delete_week_transactions(start_date: str, end_date: str) -> bool:
    """Delete all transactions within a specific week."""
    df = load_transactions()
    if len(df) == 0 or "Date" not in df.columns:
        return False
        
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    
    # Filter to KEEP transactions OUTSIDE the range
    initial_len = len(df)
    mask_to_keep = ~((df["Date"] >= start) & (df["Date"] <= end))
    df = df[mask_to_keep]
    
    if len(df) < initial_len:
        save_transactions(df)
        return True
    return False

def update_budget_value(category: str, amount: float):
    """Update budget amount for a category in the budget config."""
    df = load_budget_config()
    
    if len(df) > 0:
        mask = df["Category"] == category
        if mask.any():
            # Update all matches to be safe, though should be unique
            df.loc[mask, "Budget"] = amount
            save_budget_config(df)
            return True
            
    return False


def get_history_weeks() -> List[tuple]:
    """
    Get all unique weeks that have transactions, sorted descending.
    Always includes the current week.
    """
    df = load_transactions()
    
    # Start with current week
    current_start, _ = get_week_dates(datetime.now())
    # Normalize to midnight for consistent comparison
    current_start = current_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Store unique start dates
    unique_weeks = {current_start}
    
    if len(df) > 0 and "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        
        for date in df["Date"]:
            start, _ = get_week_dates(date)
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            unique_weeks.add(start)
    
    # Convert back to list of (start, end) tuples
    week_list = []
    for start in unique_weeks:
        end = start + timedelta(days=6)
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        week_list.append((start, end))
        
    # Sort by start date, descending (newest first)
    return sorted(week_list, key=lambda x: x[0], reverse=True)

