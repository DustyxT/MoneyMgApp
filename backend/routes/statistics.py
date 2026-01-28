from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from services.data_service import (
    get_summary_metrics, 
    get_chart_data, 
    get_spending_by_category,
    get_budget_vs_actual
)

router = APIRouter(prefix="/api/stats", tags=["statistics"])


@router.get("/summary")
def get_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> dict:
    """Get summary metrics for a date range."""
    try:
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        metrics = get_summary_metrics(start_date, end_date)
        return {
            "start_date": start_date,
            "end_date": end_date,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chart-data")
def get_chart(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    group_by: str = Query("week", pattern="^(week|month)$")
) -> dict:
    """Get chart data grouped by week or month."""
    try:
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        data = get_chart_data(start_date, end_date, group_by)
        return {
            "start_date": start_date,
            "end_date": end_date,
            "group_by": group_by,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/spending-by-category")
def get_spending(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> dict:
    """Get spending breakdown by category."""
    try:
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        data = get_spending_by_category(start_date, end_date)
        return {
            "start_date": start_date,
            "end_date": end_date,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget-vs-actual")
def get_comparison(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
) -> dict:
    """Get budget vs actual comparison."""
    try:
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        data = get_budget_vs_actual(start_date, end_date)
        return {
            "start_date": start_date,
            "end_date": end_date,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
