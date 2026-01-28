from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from models.schemas import WeeklyData, TransactionUpdate, Transaction
from services.data_service import (
    get_weekly_data, save_weekly_transactions, get_week_start, 
    get_week_label, load_transactions, add_transaction, delete_transaction
)
import io
import uuid

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("/weekly/{week_start}")
def get_transactions_for_week(week_start: str) -> dict:
    """Get all transaction data for a specific week."""
    try:
        data = get_weekly_data(week_start)
        week_date = datetime.strptime(week_start, "%Y-%m-%d")
        return {
            "week_start": week_start,
            "week_label": get_week_label(week_date),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current-week")
def get_current_week() -> dict:
    """Get the current week's start date."""
    today = datetime.now()
    week_start = get_week_start(today)
    return {
        "week_start": week_start.strftime("%Y-%m-%d"),
        "week_label": get_week_label(today)
    }


@router.get("/all")
def get_all_transactions(
    type_filter: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> dict:
    """Get all transactions with optional filtering."""
    try:
        df = load_transactions()
        if df.empty:
            return {"transactions": [], "count": 0}
        
        # Apply filters
        if start_date:
            df = df[df["Date"] >= start_date]
        if end_date:
            df = df[df["Date"] <= end_date]
        if type_filter:
            df = df[df["Type"] == type_filter]
        
        # Sort by date descending
        df = df.sort_values("Date", ascending=False)
        
        transactions = []
        for _, row in df.iterrows():
            txn = {
                "date": row["Date"],
                "category": row["Category"],
                "type": row["Type"],
                "actual": float(row["Actual"]),
            }
            # Add optional fields if they exist
            if "ID" in row and pd.notna(row["ID"]):
                txn["id"] = str(row["ID"])
            if "Note" in row and pd.notna(row["Note"]):
                txn["note"] = str(row["Note"])
            
            transactions.append(txn)
        
        return {"transactions": transactions, "count": len(transactions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
def create_transaction(transaction: Transaction) -> dict:
    """Add a new transaction."""
    try:
        # Convert Pydantic model to dict
        txn_data = {
            "Date": transaction.date,
            "Category": transaction.category,
            "Type": transaction.type,
            "Actual": transaction.actual,
            "Note": transaction.note
        }
        
        new_txn = add_transaction(txn_data)
        
        return {
            "success": True, 
            "message": "Transaction added successfully", 
            "transaction": new_txn
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{transaction_id}")
def remove_transaction(transaction_id: str) -> dict:
    """Delete a transaction by ID."""
    try:
        success = delete_transaction(transaction_id)
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        return {"success": True, "message": "Transaction deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
def export_transactions():
    """Export all transactions as CSV."""
    try:
        df = load_transactions()
        csv_content = df.to_csv(index=False)
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=transactions.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weekly")
def save_transactions_for_week(update: TransactionUpdate) -> dict:
    """Save all transactions for a specific week."""
    try:
        data = [
            {
                "category": t.category,
                "type": t.type,
                "budget": 0,  
                "actual": t.actual
            }
            for t in update.transactions
        ]
        save_weekly_transactions(update.week_start, data)
        return {"success": True, "message": f"Saved transactions for {update.week_start}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/weekly/{week_start}")
def update_weekly_transactions(week_start: str, data: List[WeeklyData]) -> dict:
    """Update transactions for a specific week."""
    try:
        items = [
            {
                "category": d.category,
                "type": d.type,
                "budget": d.budget,
                "actual": d.actual
            }
            for d in data
        ]
        save_weekly_transactions(week_start, items)
        return {"success": True, "message": f"Updated transactions for {week_start}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/weeks")
def get_transaction_history_weeks() -> dict:
    """Get list of weeks that have transaction data."""
    try:
        weeks = []
        saved_weeks = load_transactions()["Date"].unique().tolist()
        
        # Sort descending
        saved_weeks.sort(reverse=True)
        
        for week_start in saved_weeks:
            week_date = datetime.strptime(week_start, "%Y-%m-%d")
            label = get_week_label(week_date)
            weeks.append({
                "week_start": week_start,
                "label": label
            })
            
        return {"weeks": weeks, "count": len(weeks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
