from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class Transaction(BaseModel):
    id: Optional[str] = None
    date: str
    category: str
    type: str
    actual: float
    note: Optional[str] = None

class TransactionUpdate(BaseModel):
    transactions: List[Transaction]
    week_start: str

class BudgetItem(BaseModel):
    category: str
    type: str
    budget: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class BudgetUpdate(BaseModel):
    items: List[BudgetItem]

class WeeklyData(BaseModel):
    category: str
    type: str
    budget: float
    actual: float
    difference: float

class SummaryMetrics(BaseModel):
    total_income: float
    total_bills: float
    total_expenses: float
    total_savings: float
    total_debt: float
    net_balance: float

class ChartDataPoint(BaseModel):
    period: str
    income: float = 0
    expenses: float = 0
    bills: float = 0
    savings: float = 0

class CategorySpending(BaseModel):
    category: str
    amount: float
