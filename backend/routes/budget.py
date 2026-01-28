from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.schemas import BudgetItem, BudgetUpdate
from services.data_service import load_budget_config, save_budget_config
import pandas as pd

router = APIRouter(prefix="/api/budget", tags=["budget"])


@router.get("/")
def get_budget_config() -> dict:
    """Get all budget configuration."""
    try:
        df = load_budget_config()
        items = []
        for _, row in df.iterrows():
            item = {
                "category": row["Category"],
                "type": row["Type"],
                "budget": float(row["Budget"])
            }
            # Include date range if available
            if "Start Date" in df.columns:
                item["start_date"] = str(row.get("Start Date", ""))
            if "End Date" in df.columns:
                item["end_date"] = str(row.get("End Date", ""))
            items.append(item)
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/")
def update_budget_config(update: BudgetUpdate) -> dict:
    """Update budget configuration."""
    try:
        df = load_budget_config()
        
        for item in update.items:
            mask = (df["Category"] == item.category) & (df["Type"] == item.type)
            if mask.any():
                df.loc[mask, "Budget"] = item.budget
                # Update date range if provided
                if item.start_date:
                    df.loc[mask, "Start Date"] = item.start_date
                if item.end_date:
                    df.loc[mask, "End Date"] = item.end_date
        
        save_budget_config(df)
        return {"success": True, "message": "Budget configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/apply-dates")
def apply_dates_to_all(start_date: str = Query(...), end_date: str = Query(...)) -> dict:
    """Apply date range to all budget items."""
    try:
        df = load_budget_config()
        df["Start Date"] = start_date
        df["End Date"] = end_date
        save_budget_config(df)
        return {"success": True, "message": f"Applied date range {start_date} to {end_date} to all categories"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-type/{type_name}")
def get_budget_by_type(type_name: str) -> dict:
    """Get budget items by type."""
    try:
        df = load_budget_config()
        filtered = df[df["Type"] == type_name]
        items = [
            {
                "category": row["Category"],
                "type": row["Type"],
                "budget": float(row["Budget"]),
                "start_date": str(row.get("Start Date", "")),
                "end_date": str(row.get("End Date", ""))
            }
            for _, row in filtered.iterrows()
        ]
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
