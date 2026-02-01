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

# Path to data files (same directory as app.py)
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


def get_week_dates(date: datetime) -> tuple:
    """Get Sunday-Saturday week range for a given date."""
    # Find the Sunday of the current week
    days_since_sunday = date.weekday() + 1  # Monday=0, so Sunday=-1 -> +1
    if days_since_sunday == 7:  # It's Sunday
        days_since_sunday = 0
    start_date = date - timedelta(days=days_since_sunday)
    end_date = start_date + timedelta(days=6)
    return start_date, end_date


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
    
    # Calculate totals by type
    income_total = week_trans[week_trans["Type"] == "Income"]["Actual"].sum() if len(week_trans) > 0 else 0
    expenses_total = week_trans[week_trans["Type"].isin(["Expenses", "Bills"])]["Actual"].sum() if len(week_trans) > 0 else 0
    savings_total = week_trans[week_trans["Type"] == "Savings"]["Actual"].sum() if len(week_trans) > 0 else 0
    
    # Build category summaries
    def get_category_data(cat_type: str) -> List[Dict]:
        budget_cats = budget[budget["Type"] == cat_type]
        result = []
        for _, row in budget_cats.iterrows():
            cat = row["Category"]
            weekly_budget = row["Budget"] / 4.33  # Monthly to weekly
            actual = week_trans[week_trans["Category"] == cat]["Actual"].sum() if len(week_trans) > 0 else 0
            result.append({
                "category": cat,
                "budget": round(weekly_budget, 2),
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
            "balance": round(income_total - expenses_total - savings_total, 2),
        },
        "income": get_category_data("Income"),
        "expenses": get_category_data("Expenses"),
        "bills": get_category_data("Bills"),
        "savings": get_category_data("Savings"),
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
