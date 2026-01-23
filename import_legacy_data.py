import pandas as pd
import csv
import re
from datetime import datetime

# Define standard columns
INCOME_COLS = ["Date", "Source Name", "Type", "Expected Amount (AUD)", "Actual Amount (AUD)"]
BILLS_COLS = ["Bill Name", "Due Date (Day of Month)", "Budget Amount (AUD)", "Actual Amount (AUD)", "Status"]
EXPENSES_COLS = ["Date", "Category", "Description", "Amount (AUD)", "Payment Method"]
SAVINGS_COLS = ['Goal Name', 'Target Amount (AUD)', 'Current Saved (AUD)', 'Deadline']

def clean_curr(val):
    if pd.isna(val) or val == '':
        return 0.0
    val = str(val).replace('$', '').replace(',', '').strip()
    try:
        return float(val)
    except ValueError:
        return 0.0

def parse_january_csv():
    print("Reading January.csv...")
    # Read ignoring header to locate blocks manually
    try:
        df_raw = pd.read_csv('January.csv', header=None)
    except FileNotFoundError:
        print("January.csv not found.")
        return

    # Helper to find header coordinates
    def find_header(keyword, row_limit=50):
        for r in range(min(len(df_raw), row_limit)):
            for c in range(len(df_raw.columns)):
                val = str(df_raw.iloc[r, c]).strip().upper()
                if keyword in val:
                    return r, c
        return None, None

    # --- 1. INCOME PARSING ---
    # Look for "INCOME NAME"
    ir, ic = find_header("INCOME NAME")
    income_data = []
    if ir is not None:
        print(f"Found Income at Row {ir}, Col {ic}")
        # Expected Headers: INCOME NAME, PAYDAY, EXPECTED, ACTUAL
        # Mapped to: Source Name, Date, Expected, Actual
        # Iterate until empty row
        empty_count = 0
        for r in range(ir+1, min(ir+20, len(df_raw))):
            name = df_raw.iloc[r, ic]
            if pd.isna(name) or str(name).strip() == '':
                empty_count += 1
                if empty_count > 3: break
                continue
            
            empty_count = 0  # Reset on valid data
            if str(name).upper() == 'TOTAL':
                break
            
            date_val = df_raw.iloc[r, ic+1] # Payday
            exp_val = clean_curr(df_raw.iloc[r, ic+2])
            act_val = clean_curr(df_raw.iloc[r, ic+3])
            
            # Simple date parsing or default
            if pd.isna(date_val):
                date_str = "2026-01-01"
            else:
                # Try simple format Jan-11 -> 2026-01-11
                try:
                   dt = datetime.strptime(str(date_val) + "-2026", "%b-%d-%Y")
                   date_str = dt.strftime("%Y-%m-%d")
                except:
                   date_str = str(date_val)
            
            # Determining Type (heuristic)
            inc_type = "Other"
            if "Paycheck" in str(name): inc_type = "Part-time Job"
            elif "Support" in str(name): inc_type = "Parental Support"
            
            income_data.append({
                "Date": date_str,
                "Source Name": name,
                "Type": inc_type,
                "Expected Amount (AUD)": exp_val,
                "Actual Amount (AUD)": act_val
            })

    # --- 2. BILLS PARSING ---
    # Look for "BILLS NAME"
    br, bc = find_header("BILLS NAME")
    bills_data = []
    if br is not None:
        print(f"Found Bills at Row {br}, Col {bc}")
        # Headers: BILLS NAME, (skip), DUE, (skip), BUDGET, ACTUAL
        # Note: offsets based on CSV snippet
        # BILLS NAME (col bc), DUE (bc+2), BUDGET (bc+4), ACTUAL (bc+5)
        for r in range(br+1, len(df_raw)):
            name = df_raw.iloc[r, bc]
            if pd.isna(name) or str(name).strip() == '':
                break
            
            # The CSV seems to have a checkbox column before bills name?
            # Snippet: ,TRUE,Phone,,,
            # So actual name might be at bc+1 if "BILLS NAME" matches the label row but data has shift?
            # Let's trust the relative position from the header cell
            
            # Wait, snippet:
            # Row 19: ,BILLS NAME,,DUE,,BUDGET,ACTUAL...
            # Row 20: ,TRUE,Phone,,, $100...
            # If "BILLS NAME" is at col 1.
            # "Phone" is at col 2.
            # So name is at col bc ? No, "BILLS NAME" header is at col 1. "TRUE" is at col 1. "Phone" is at col 2.
            # It seems the data rows are shifted or there is a boolean column.
            # Let's check the value. If it is TRUE/FALSE, take next col.
            
            val_col_name = df_raw.iloc[r, bc]
            val_potential_name = df_raw.iloc[r, bc+1]
            
            if str(val_col_name).upper() in ['TRUE', 'FALSE']:
                 final_name = val_potential_name
                 # If name shifted, others might be too?
                 # Header: BILLS NAME (1), DUE (3), BUDGET (5), ACTUAL (6)
                 # Data: TRUE(1), PHONE(2), <empty>(3), <empty>(4), 100(5), 0(6)
                 # It seems matching headers is safer.
                 # Let's assume standard offsets from header for budget/actual
                 budget = clean_curr(df_raw.iloc[r, bc+4])
                 actual = clean_curr(df_raw.iloc[r, bc+5])
                 due = 15 # Default
            else:
                 final_name = val_col_name
                 budget = clean_curr(df_raw.iloc[r, bc+4])
                 actual = clean_curr(df_raw.iloc[r, bc+5])
                 due = 15

            bills_data.append({
                "Bill Name": final_name,
                "Due Date (Day of Month)": due,
                "Budget Amount (AUD)": budget,
                "Actual Amount (AUD)": actual,
                "Status": "Paid" if actual >= budget else "Pending"
            })

    # --- 3. EXPENSES PARSING ---
    # Look for "EXPENSES NAME"
    er, ec = find_header("EXPENSES NAME")
    expenses_data = []
    if er is not None:
        print(f"Found Expenses at Row {er}, Col {ec}")
        # Headers: EXPENSES NAME, (skip), BUDGET, ACTUAL
        # Snippet: EXPENSES NAME,,BUDGET,ACTUAL
        for r in range(er+1, len(df_raw)):
            cat_name = df_raw.iloc[r, ec]
            if pd.isna(cat_name) or str(cat_name).strip() == '':
                break
            
            budget = clean_curr(df_raw.iloc[r, ec+2])
            actual = clean_curr(df_raw.iloc[r, ec+3])
            
            # Create an expense entry for the "Actual" amount
            if actual > 0:
                expenses_data.append({
                    "Date": "2026-01-01", # Default date
                    "Category": cat_name,
                    "Description": "Imported from Excel",
                    "Amount (AUD)": actual,
                    "Payment Method": "Card"
                })

    # --- 4. SAVINGS PARSING ---
    sr, sc = find_header("SAVINGS NAME")
    savings_data = []
    has_remittance = False
    if sr is not None:
        print(f"Found Savings at Row {sr}, Col {sc}")
        # Headers: SAVINGS NAME, (skip), BUDGET, ACTUAL
        for r in range(sr+1, len(df_raw)):
            goal = df_raw.iloc[r, sc]
            if pd.isna(goal) or str(goal).strip() == '':
                break
            
            target = clean_curr(df_raw.iloc[r, sc+2])
            saved = clean_curr(df_raw.iloc[r, sc+3])
            
            if "Family" in str(goal) or "Remittance" in str(goal):
                has_remittance = True
            
            savings_data.append({
                "Goal Name": goal,
                "Target Amount (AUD)": target if target > 0 else 1000.0,
                "Current Saved (AUD)": saved,
                "Deadline": "2026-12-31"
            })

    if not has_remittance:
        print("Adding Family Remittance goal...")
        savings_data.append({
            "Goal Name": "Family Remittance",
            "Target Amount (AUD)": 5000.0,
            "Current Saved (AUD)": 0.0,
            "Deadline": "2026-12-31" 
        })

    # --- WRITE CSVs ---
    if income_data:
        pd.DataFrame(income_data).to_csv("income.csv", index=False)
        print("Wrote income.csv")
    
    if bills_data:
        pd.DataFrame(bills_data).to_csv("bills.csv", index=False)
        print("Wrote bills.csv")
    
    if expenses_data:
        pd.DataFrame(expenses_data).to_csv("expenses.csv", index=False)
        print("Wrote expenses.csv")

    if savings_data:
        pd.DataFrame(savings_data).to_csv("savings.csv", index=False)
        print("Wrote savings.csv")

if __name__ == "__main__":
    parse_january_csv()
