"""
Chart Service for Flet Native App
Generates chart images using Matplotlib for embedding in Flet UI.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for image generation

import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict, Any
from datetime import datetime, timedelta
import data_service as ds

# Chart styling
plt.style.use('dark_background')
CHART_COLORS = {
    "primary": "#3b82f6",
    "secondary": "#6366f1", 
    "success": "#22c55e",
    "error": "#ef4444",
    "warning": "#f59e0b",
    "background": "#171717",
    "text": "#fafafa",
    "text_secondary": "#a1a1aa",
}

# Color palette for pie charts
PIE_COLORS = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#6366f1", "#ec4899", "#14b8a6", "#f97316"]


def _fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor=CHART_COLORS["background"], dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64


def generate_income_vs_expenses_chart(start_date: str, end_date: str) -> str:
    """Generate Income vs Expenses bar chart."""
    data = ds.get_weekly_data(start_date, end_date)
    totals = data["totals"]
    
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(CHART_COLORS["background"])
    ax.set_facecolor(CHART_COLORS["background"])
    
    categories = ["Income", "Expenses", "Savings", "Investments"]
    values = [totals["income"], totals["expenses"], totals["savings"], totals.get("investments", 0)]
    colors = [CHART_COLORS["success"], CHART_COLORS["error"], CHART_COLORS["primary"], "#14b8a6"]
    
    bars = ax.bar(categories, values, color=colors, width=0.6)
    
    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                f'${val:.0f}', ha='center', va='bottom', color=CHART_COLORS["text"], fontsize=10)
    
    ax.set_ylabel("Amount ($)", color=CHART_COLORS["text_secondary"])
    ax.tick_params(colors=CHART_COLORS["text_secondary"])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(CHART_COLORS["text_secondary"])
    ax.spines['left'].set_color(CHART_COLORS["text_secondary"])
    
    plt.tight_layout()
    return _fig_to_base64(fig)


def generate_spending_by_category_chart(start_date: str, end_date: str) -> str:
    """Generate spending by category pie chart."""
    data = ds.get_weekly_data(start_date, end_date)
    expenses = data["expenses"]
    bills = data["bills"]
    
    # Combine expenses and bills
    all_spending = []
    for item in expenses + bills:
        if item["actual"] > 0:
            all_spending.append({"category": item["category"], "amount": item["actual"]})
    
    if not all_spending:
        # Return empty chart
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor(CHART_COLORS["background"])
        ax.set_facecolor(CHART_COLORS["background"])
        ax.text(0.5, 0.5, "No spending data", ha='center', va='center', 
                color=CHART_COLORS["text_secondary"], fontsize=12)
        ax.axis('off')
        return _fig_to_base64(fig)
    
    # Sort and take top 6
    all_spending.sort(key=lambda x: x["amount"], reverse=True)
    top_spending = all_spending[:6]
    if len(all_spending) > 6:
        other_amount = sum(item["amount"] for item in all_spending[6:])
        top_spending.append({"category": "Other", "amount": other_amount})
    
    labels = [item["category"] for item in top_spending]
    values = [item["amount"] for item in top_spending]
    
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(CHART_COLORS["background"])
    ax.set_facecolor(CHART_COLORS["background"])
    
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct='%1.0f%%',
        colors=PIE_COLORS[:len(values)],
        textprops={'color': CHART_COLORS["text"], 'fontsize': 8},
        pctdistance=0.75
    )
    for autotext in autotexts:
        autotext.set_color(CHART_COLORS["background"])
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    return _fig_to_base64(fig)


def generate_monthly_trend_chart(months: int = 4) -> str:
    """Generate monthly income vs expenses trend line chart."""
    today = datetime.now()
    
    month_data = []
    for i in range(months - 1, -1, -1):
        # Calculate month start/end
        target_date = today - timedelta(days=i * 30)
        month_start = target_date.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
        
        # Get data for this month
        data = ds.get_weekly_data(month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d"))
        month_data.append({
            "month": month_start.strftime("%b"),
            "income": data["totals"]["income"],
            "expenses": data["totals"]["expenses"],
        })
    
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor(CHART_COLORS["background"])
    ax.set_facecolor(CHART_COLORS["background"])
    
    months_labels = [d["month"] for d in month_data]
    incomes = [d["income"] for d in month_data]
    expenses = [d["expenses"] for d in month_data]
    
    ax.plot(months_labels, incomes, marker='o', color=CHART_COLORS["success"], label="Income", linewidth=2)
    ax.plot(months_labels, expenses, marker='o', color=CHART_COLORS["error"], label="Expenses", linewidth=2)
    
    ax.set_ylabel("Amount ($)", color=CHART_COLORS["text_secondary"])
    ax.tick_params(colors=CHART_COLORS["text_secondary"])
    ax.legend(facecolor=CHART_COLORS["background"], edgecolor=CHART_COLORS["text_secondary"])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(CHART_COLORS["text_secondary"])
    ax.spines['left'].set_color(CHART_COLORS["text_secondary"])
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    return _fig_to_base64(fig)


def generate_budget_vs_actual_chart(start_date: str, end_date: str) -> str:
    """Generate budget vs actual comparison bar chart."""
    data = ds.get_weekly_data(start_date, end_date)
    expenses = data["expenses"]
    
    # Filter categories with budget > 0
    categories_with_budget = [e for e in expenses if e["budget"] > 0][:6]
    
    if not categories_with_budget:
        fig, ax = plt.subplots(figsize=(6, 3))
        fig.patch.set_facecolor(CHART_COLORS["background"])
        ax.set_facecolor(CHART_COLORS["background"])
        ax.text(0.5, 0.5, "No budget data", ha='center', va='center', 
                color=CHART_COLORS["text_secondary"], fontsize=12)
        ax.axis('off')
        return _fig_to_base64(fig)
    
    categories = [c["category"][:10] for c in categories_with_budget]
    budgets = [c["budget"] for c in categories_with_budget]
    actuals = [c["actual"] for c in categories_with_budget]
    
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor(CHART_COLORS["background"])
    ax.set_facecolor(CHART_COLORS["background"])
    
    x = range(len(categories))
    width = 0.35
    
    ax.bar([i - width/2 for i in x], budgets, width, label='Budget', color=CHART_COLORS["primary"], alpha=0.7)
    ax.bar([i + width/2 for i in x], actuals, width, label='Actual', color=CHART_COLORS["warning"])
    
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=30, ha='right', fontsize=8)
    ax.tick_params(colors=CHART_COLORS["text_secondary"])
    ax.legend(facecolor=CHART_COLORS["background"], edgecolor=CHART_COLORS["text_secondary"])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(CHART_COLORS["text_secondary"])
    ax.spines['left'].set_color(CHART_COLORS["text_secondary"])
    
    plt.tight_layout()
    return _fig_to_base64(fig)
