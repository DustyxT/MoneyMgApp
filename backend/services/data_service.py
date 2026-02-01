import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

# Path to data files (parent directory)
from utils import get_data_path
DATA_DIR = get_data_path()

BUDGET_FILE = DATA_DIR / "budget_config.csv"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"

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
        df = pd.read_csv(BUDGET_FILE)
        return df
    except FileNotFoundError:
        df = pd.DataFrame(DEFAULT_BUDGET)
        df.to_csv(BUDGET_FILE, index=False)
        return df


def save_budget_config(df: pd.DataFrame):
    """Save budget configuration to CSV."""
    df.to_csv(BUDGET_FILE, index=False)


def load_transactions() -> pd.DataFrame:
    """Load transactions from CSV or create empty DataFrame."""
    try:
        df = pd.read_csv(TRANSACTIONS_FILE)
        # Ensure ID column exists
        if "id" not in df.columns:
            df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
            save_transactions(df)
        return df
    except FileNotFoundError:
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
    """Delete a transaction by ID. Returns True if found and deleted."""
    df = load_transactions()
    if "id" not in df.columns:
        return False
        
    initial_len = len(df)
    df = df[df["id"] != transaction_id]
    
    if len(df) < initial_len:
        save_transactions(df)
        return True
    return False


def delete_transactions_by_week(week_start: str) -> int:
    """Delete all transactions for a given week. Returns count of deleted transactions."""
    df = load_transactions()
    if df.empty:
        return 0
    
    # Parse week_start and calculate week_end
    week_start_date = datetime.strptime(week_start, "%Y-%m-%d")
    week_end_date = week_start_date + timedelta(days=6)
    week_end = week_end_date.strftime("%Y-%m-%d")
    
    initial_len = len(df)
    df = df[(df["Date"] < week_start) | (df["Date"] > week_end)]
    deleted_count = initial_len - len(df)
    
    if deleted_count > 0:
        save_transactions(df)
    
    return deleted_count


def get_week_start(d: datetime) -> datetime:
    """Get Monday of the week containing date d."""
    return d - timedelta(days=d.weekday())


def get_week_end(d: datetime) -> datetime:
    """Get Sunday of the week containing date d."""
    return d + timedelta(days=(6 - d.weekday()))


def get_week_number(d: datetime) -> int:
    """Get ISO week number."""
    return d.isocalendar()[1]


def get_week_label(d: datetime) -> str:
    """Generate formatted week label."""
    week_start = get_week_start(d)
    week_end = get_week_end(d)
    week_num = get_week_number(d)
    return f"Week {week_num}: {week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}"


def get_weekly_data(week_start_str: str) -> List[Dict[str, Any]]:
    """Get all category data for a specific week."""
    budget_df = load_budget_config()
    transactions_df = load_transactions()
    
    # Parse the week start date for date range comparison
    week_date = datetime.strptime(week_start_str, "%Y-%m-%d")
    week_end = week_date + timedelta(days=6)  # Sunday
    week_end_str = week_end.strftime("%Y-%m-%d")
    
    weekly_data = []
    
    for _, row in budget_df.iterrows():
        category = row["Category"]
        cat_type = row["Type"]
        weekly_budget_value = float(row["Budget"])  # Now stored as weekly directly
        
        # Check if budget has date range columns and if week falls within range
        budget_applies = True
        if "Start Date" in row and "End Date" in row:
            try:
                start_date = datetime.strptime(str(row["Start Date"]), "%Y-%m-%d")
                end_date = datetime.strptime(str(row["End Date"]), "%Y-%m-%d")
                # Check if the week start date falls within the budget's date range
                budget_applies = start_date <= week_date <= end_date
            except (ValueError, TypeError):
                # If dates are invalid, apply budget anyway
                budget_applies = True
        
        # Skip categories that don't apply to this week
        if not budget_applies:
            continue
        
        weekly_budget = round(weekly_budget_value, 2)
        
        # Get actual for this week - use date range (Mon-Sun)
        mask = (
            (transactions_df["Date"] >= week_start_str) & 
            (transactions_df["Date"] <= week_end_str) &
            (transactions_df["Category"] == category) & 
            (transactions_df["Type"] == cat_type)
        )
        actual = float(transactions_df.loc[mask, "Actual"].sum()) if mask.any() else 0.0
        
        weekly_data.append({
            "category": category,
            "type": cat_type,
            "budget": weekly_budget,
            "actual": actual,
            "difference": round(weekly_budget - actual, 2) if cat_type != "Income" else round(actual - weekly_budget, 2)
        })
    
    # Add uncategorized transactions (not matching any budget category)
    if not transactions_df.empty:
        budget_categories = set(zip(budget_df["Category"], budget_df["Type"]))
        
        # Filter transactions for this week
        week_end = week_date + timedelta(days=6)
        week_end_str = week_end.strftime("%Y-%m-%d")
        week_mask = (transactions_df["Date"] >= week_start_str) & (transactions_df["Date"] <= week_end_str)
        week_transactions = transactions_df[week_mask]
        
        # Find transactions with categories not in budget config
        if not week_transactions.empty:
            uncategorized = week_transactions[~week_transactions.apply(
                lambda row: (row["Category"], row["Type"]) in budget_categories, axis=1
            )]
            
            # Group by category and type to show each unique category
            if not uncategorized.empty:
                grouped = uncategorized.groupby(["Category", "Type"])["Actual"].sum()
                for (category, cat_type), total in grouped.items():
                    weekly_data.append({
                        "category": category,
                        "type": cat_type,
                        "budget": 0.0,
                        "actual": float(total),
                        "difference": -float(total) if cat_type != "Income" else float(total)
                    })
    
    return weekly_data


def save_weekly_transactions(week_start_str: str, data: List[Dict[str, Any]]):
    """Save transactions for a specific week."""
    transactions_df = load_transactions()
    budget_df = load_budget_config()
    
    for item in data:
        category = item["category"]
        cat_type = item["type"]
        actual = item["actual"]
        weekly_budget = item["budget"]
        
        # Save weekly budget directly (no conversion needed)
        budget_mask = (budget_df["Category"] == category) & (budget_df["Type"] == cat_type)
        if budget_mask.any():
            budget_df.loc[budget_mask, "Budget"] = weekly_budget
        
        # Update or create transaction
        txn_mask = (
            (transactions_df["Date"] == week_start_str) & 
            (transactions_df["Category"] == category) & 
            (transactions_df["Type"] == cat_type)
        )
        
        if txn_mask.any():
            transactions_df.loc[txn_mask, "Actual"] = actual
        elif actual != 0:
            new_row = pd.DataFrame([{
                "Date": week_start_str,
                "Category": category,
                "Type": cat_type,
                "Actual": actual
            }])
            transactions_df = pd.concat([transactions_df, new_row], ignore_index=True)
    
    save_budget_config(budget_df)
    save_transactions(transactions_df)


def get_saved_weeks() -> List[str]:
    """Get list of week start dates that have any transaction data."""
    df = load_transactions()
    if df.empty:
        return []
        
    # Get unique dates and sort them
    dates = df["Date"].unique().tolist()
    
    # Sort descending (newest first)
    dates.sort(reverse=True)
    
    return dates


def get_summary_metrics(start_date: str, end_date: str) -> Dict[str, float]:
    """Get summary metrics for a date range."""
    df = load_transactions()
    if df.empty:
        return {
            "total_income": 0,
            "total_bills": 0,
            "total_expenses": 0,
            "total_savings": 0,
            "total_debt": 0,
            "net_balance": 0
        }
    
    df["Date"] = pd.to_datetime(df["Date"])
    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    filtered = df[mask]
    
    income = float(filtered[filtered["Type"] == "Income"]["Actual"].sum())
    bills = float(filtered[filtered["Type"] == "Bills"]["Actual"].sum())
    expenses = float(filtered[filtered["Type"] == "Expenses"]["Actual"].sum())
    savings = float(filtered[filtered["Type"] == "Savings"]["Actual"].sum())
    debt = float(filtered[filtered["Type"] == "Debt"]["Actual"].sum())
    
    return {
        "total_income": income,
        "total_bills": bills,
        "total_expenses": expenses,
        "total_savings": savings,
        "total_debt": debt,
        "net_balance": income - bills - expenses - savings - debt
    }


def get_chart_data(start_date: str, end_date: str, group_by: str = "week") -> List[Dict[str, Any]]:
    """Get chart data grouped by week or month."""
    df = load_transactions()
    if df.empty:
        return []
    
    df["Date"] = pd.to_datetime(df["Date"])
    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    filtered = df[mask].copy()
    
    if filtered.empty:
        return []
    
    if group_by == "month":
        filtered["Period"] = filtered["Date"].dt.to_period("M").astype(str)
    else:
        filtered["Period"] = filtered["Date"].apply(lambda d: f"Wk {get_week_number(d)}")
    
    result = []
    for period in filtered["Period"].unique():
        period_data = filtered[filtered["Period"] == period]
        result.append({
            "period": period,
            "income": float(period_data[period_data["Type"] == "Income"]["Actual"].sum()),
            "bills": float(period_data[period_data["Type"] == "Bills"]["Actual"].sum()),
            "expenses": float(period_data[period_data["Type"] == "Expenses"]["Actual"].sum()),
            "savings": float(period_data[period_data["Type"] == "Savings"]["Actual"].sum()),
        })
    
    return sorted(result, key=lambda x: x["period"])


def get_spending_by_category(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Get spending breakdown by category."""
    df = load_transactions()
    if df.empty:
        return []
    
    df["Date"] = pd.to_datetime(df["Date"])
    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    filtered = df[mask]
    
    spending = filtered[filtered["Type"].isin(["Bills", "Expenses"])]
    if spending.empty:
        return []
    
    grouped = spending.groupby("Category")["Actual"].sum().reset_index()
    grouped = grouped[grouped["Actual"] > 0]
    
    return [{"category": row["Category"], "amount": float(row["Actual"])} 
            for _, row in grouped.iterrows()]


def get_budget_vs_actual(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Get budget vs actual comparison."""
    budget_df = load_budget_config()
    transactions_df = load_transactions()
    
    if transactions_df.empty:
        return []
    
    transactions_df["Date"] = pd.to_datetime(transactions_df["Date"])
    mask = (transactions_df["Date"] >= start_date) & (transactions_df["Date"] <= end_date)
    filtered = transactions_df[mask]
    
    actual_by_cat = filtered.groupby(["Category", "Type"])["Actual"].sum().reset_index()
    
    result = []
    for _, row in budget_df.iterrows():
        if row["Type"] in ["Bills", "Expenses"]:
            # Check date range validity
            budget_applies = True
            if "Start Date" in row and "End Date" in row:
                try:
                    cat_start = datetime.strptime(str(row["Start Date"]), "%Y-%m-%d")
                    cat_end = datetime.strptime(str(row["End Date"]), "%Y-%m-%d")
                    
                    # Convert query string dates to datetime for comparison
                    query_start = datetime.strptime(start_date, "%Y-%m-%d")
                    query_end = datetime.strptime(end_date, "%Y-%m-%d")
                    
                    # Check for overlap: (StartA <= EndB) and (EndA >= StartB)
                    budget_applies = (cat_start <= query_end) and (cat_end >= query_start)
                except (ValueError, TypeError):
                    budget_applies = True # Default to apply if dates invalid/empty
            
            if not budget_applies:
                continue

            actual_match = actual_by_cat[
                (actual_by_cat["Category"] == row["Category"]) & 
                (actual_by_cat["Type"] == row["Type"])
            ]
            actual = float(actual_match["Actual"].iloc[0]) if not actual_match.empty else 0
            
            result.append({
                "category": row["Category"],
                "budget": float(row["Budget"]),
                "actual": actual
            })
    
    return result
