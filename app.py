"""
Manage Ur Wealth - Native Desktop Application
Built with Flet (Flutter for Python)
"""

import flet as ft
from pathlib import Path
from datetime import datetime, timedelta
import data_service as ds
import chart_service as cs

# Theme Colors
COLORS = {
    "background": "#0a0a0a",
    "surface": "#171717",
    "surface_variant": "#262626",
    "primary": "#3b82f6",
    "secondary": "#6366f1",
    "success": "#22c55e",
    "error": "#ef4444",
    "warning": "#f59e0b",
    "on_surface": "#fafafa",
    "on_surface_variant": "#a1a1aa",
}


def create_metric_card(title: str, value: str, color: str, icon: str) -> ft.Container:
    """Create a metric card widget."""
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(icon, color=color, size=20),
                ft.Text(title, size=12, color=COLORS["on_surface_variant"]),
            ], spacing=8),
            ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=color),
        ], spacing=8),
        padding=20,
        bgcolor=COLORS["surface"],
        border_radius=12,
        expand=True,
    )


def create_data_table(title: str, columns: list, rows: list, color: str) -> ft.Container:
    """Create a styled data table."""
    header_row = ft.Row(
        [ft.Text(col, weight=ft.FontWeight.BOLD, color=COLORS["on_surface_variant"], size=12, expand=True) for col in columns],
        spacing=10,
    )
    
    data_rows = []
    for row in rows:
        data_rows.append(
            ft.Row(
                [ft.Text(str(cell), color=COLORS["on_surface"], size=14, expand=True) for cell in row],
                spacing=10,
            )
        )
    
    # Build table content
    table_content = [
        ft.Row([
            ft.Container(width=4, height=20, bgcolor=color, border_radius=2),
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
        ], spacing=10),
        ft.Divider(color=COLORS["surface_variant"]),
        header_row,
        ft.Divider(color=COLORS["surface_variant"]),
    ]
    
    if data_rows:
        table_content.extend(data_rows)
    else:
        table_content.append(ft.Text("No data", color=COLORS["on_surface_variant"], italic=True))
    
    return ft.Container(
        content=ft.Column(table_content, spacing=8),
        padding=20,
        bgcolor=COLORS["surface"],
        border_radius=12,
    )


def main(page: ft.Page):
    """Main application entry point."""
    
    # Page configuration
    page.title = "Manage Ur Wealth"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLORS["background"]
    page.padding = 0
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 900
    page.window.min_height = 600
    
    # Custom theme
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=COLORS["primary"],
            secondary=COLORS["secondary"],
            surface=COLORS["surface"],
            error=COLORS["error"],
            on_primary="#ffffff",
            on_secondary="#ffffff",
            on_surface=COLORS["on_surface"],
        ),
    )
    
    # Current state
    current_date = datetime.now()
    week_start, week_end = ds.get_week_dates(current_date)
    
    # Week picker label
    week_label = ft.Text(
        f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
        size=16,
        weight=ft.FontWeight.BOLD,
        color=COLORS["on_surface"],
    )
    
    # Content container reference
    content_container = ft.Ref[ft.Container]()
    
    def navigate_week(delta: int):
        """Navigate to previous/next week."""
        nonlocal week_start, week_end
        week_start += timedelta(days=7 * delta)
        week_end += timedelta(days=7 * delta)
        week_label.value = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
        refresh_dashboard()
    
    def refresh_dashboard():
        """Refresh dashboard data."""
        data = ds.get_weekly_data(
            week_start.strftime("%Y-%m-%d"),
            week_end.strftime("%Y-%m-%d")
        )
        
        # Update metric cards
        totals = data["totals"]
        metrics_row.controls = [
            create_metric_card("Income", f"${totals['income']:,.2f}", COLORS["success"], ft.Icons.TRENDING_UP),
            create_metric_card("Expenses", f"${totals['expenses']:,.2f}", COLORS["error"], ft.Icons.TRENDING_DOWN),
            create_metric_card("Savings", f"${totals['savings']:,.2f}", COLORS["primary"], ft.Icons.SAVINGS),
            create_metric_card("Balance", f"${totals['balance']:,.2f}", 
                              COLORS["success"] if totals['balance'] >= 0 else COLORS["error"], 
                              ft.Icons.ACCOUNT_BALANCE_WALLET),
        ]
        
        # Update tables
        income_table.content = create_data_table(
            "Income",
            ["Category", "Budget", "Actual"],
            [[r["category"], f"${r['budget']:.2f}", f"${r['actual']:.2f}"] for r in data["income"]],
            COLORS["success"]
        ).content
        
        expenses_table.content = create_data_table(
            "Expenses",
            ["Category", "Budget", "Actual"],
            [[r["category"], f"${r['budget']:.2f}", f"${r['actual']:.2f}"] for r in data["expenses"]],
            COLORS["error"]
        ).content
        
        bills_table.content = create_data_table(
            "Bills",
            ["Category", "Budget", "Actual"],
            [[r["category"], f"${r['budget']:.2f}", f"${r['actual']:.2f}"] for r in data["bills"]],
            COLORS["warning"]
        ).content
        
        savings_table.content = create_data_table(
            "Savings",
            ["Category", "Budget", "Actual"],
            [[r["category"], f"${r['budget']:.2f}", f"${r['actual']:.2f}"] for r in data["savings"]],
            COLORS["primary"]
        ).content
        
        page.update()
    
    # ===== DASHBOARD VIEW =====
    def create_dashboard_view():
        nonlocal metrics_row, income_table, expenses_table, bills_table, savings_table
        
        # Week navigation
        week_nav = ft.Row([
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=lambda _: navigate_week(-1),
                icon_color=COLORS["on_surface"],
            ),
            ft.Container(
                content=week_label,
                bgcolor=COLORS["surface"],
                padding=ft.Padding(left=20, top=10, right=20, bottom=10),
                border_radius=8,
            ),
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                on_click=lambda _: navigate_week(1),
                icon_color=COLORS["on_surface"],
            ),
            ft.IconButton(
                icon=ft.Icons.TODAY,
                tooltip="Go to current week",
                on_click=lambda _: go_to_today(),
                icon_color=COLORS["primary"],
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        def go_to_today():
            nonlocal week_start, week_end
            week_start, week_end = ds.get_week_dates(datetime.now())
            week_label.value = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
            refresh_dashboard()
        
        # Metric cards row
        data = ds.get_weekly_data(
            week_start.strftime("%Y-%m-%d"),
            week_end.strftime("%Y-%m-%d")
        )
        totals = data["totals"]
        
        metrics_row = ft.Row([
            create_metric_card("Income", f"${totals['income']:,.2f}", COLORS["success"], ft.Icons.TRENDING_UP),
            create_metric_card("Expenses", f"${totals['expenses']:,.2f}", COLORS["error"], ft.Icons.TRENDING_DOWN),
            create_metric_card("Savings", f"${totals['savings']:,.2f}", COLORS["primary"], ft.Icons.SAVINGS),
            create_metric_card("Balance", f"${totals['balance']:,.2f}", 
                              COLORS["success"] if totals['balance'] >= 0 else COLORS["error"], 
                              ft.Icons.ACCOUNT_BALANCE_WALLET),
        ], spacing=20)
        
        # Data tables
        income_table = create_data_table(
            "Income",
            ["Category", "Budget", "Actual"],
            [[r["category"], f"${r['budget']:.2f}", f"${r['actual']:.2f}"] for r in data["income"]],
            COLORS["success"]
        )
        
        expenses_table = create_data_table(
            "Expenses",
            ["Category", "Budget", "Actual"],
            [[r["category"], f"${r['budget']:.2f}", f"${r['actual']:.2f}"] for r in data["expenses"]],
            COLORS["error"]
        )
        
        bills_table = create_data_table(
            "Bills",
            ["Category", "Budget", "Actual"],
            [[r["category"], f"${r['budget']:.2f}", f"${r['actual']:.2f}"] for r in data["bills"]],
            COLORS["warning"]
        )
        
        savings_table = create_data_table(
            "Savings",
            ["Category", "Budget", "Actual"],
            [[r["category"], f"${r['budget']:.2f}", f"${r['actual']:.2f}"] for r in data["savings"]],
            COLORS["primary"]
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("📊 Dashboard", size=28, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                week_nav,
                ft.Container(height=10),
                metrics_row,
                ft.Container(height=20),
                ft.Row([
                    ft.Container(content=income_table, expand=True),
                    ft.Container(content=expenses_table, expand=True),
                ], spacing=20),
                ft.Container(height=10),
                ft.Row([
                    ft.Container(content=bills_table, expand=True),
                    ft.Container(content=savings_table, expand=True),
                ], spacing=20),
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True,
        )
    
    # Initialize table references
    metrics_row = ft.Row()
    income_table = ft.Container()
    expenses_table = ft.Container()
    bills_table = ft.Container()
    savings_table = ft.Container()
    
    # ===== STATISTICS VIEW =====
    def create_statistics_view():
        # Generate charts
        income_expense_chart = cs.generate_income_vs_expenses_chart(
            week_start.strftime("%Y-%m-%d"),
            week_end.strftime("%Y-%m-%d")
        )
        spending_chart = cs.generate_spending_by_category_chart(
            week_start.strftime("%Y-%m-%d"),
            week_end.strftime("%Y-%m-%d")
        )
        trend_chart = cs.generate_monthly_trend_chart(4)
        budget_chart = cs.generate_budget_vs_actual_chart(
            week_start.strftime("%Y-%m-%d"),
            week_end.strftime("%Y-%m-%d")
        )
        
        def create_chart_card(title: str, chart_base64: str):
            return ft.Container(
                content=ft.Column([
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                    ft.Image(
                        src=f"data:image/png;base64,{chart_base64}",
                        fit="contain",
                        width=400,
                        height=200,
                    ),
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                bgcolor=COLORS["surface"],
                border_radius=12,
                expand=True,
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("📈 Statistics", size=28, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                ft.Text(
                    f"Week: {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
                    color=COLORS["on_surface_variant"]
                ),
                ft.Container(height=10),
                ft.Row([
                    create_chart_card("Income vs Expenses", income_expense_chart),
                    create_chart_card("Spending by Category", spending_chart),
                ], spacing=20),
                ft.Container(height=10),
                ft.Row([
                    create_chart_card("Monthly Trend", trend_chart),
                    create_chart_card("Budget vs Actual", budget_chart),
                ], spacing=20),
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True,
        )
    
    # ===== BUDGET CONFIG VIEW =====
    def create_budget_view():
        budget_df = ds.load_budget_config()
        budget_fields = {}
        
        def save_budget(e):
            # Update budget values
            for idx, row in budget_df.iterrows():
                cat = row["Category"]
                if cat in budget_fields:
                    try:
                        budget_df.at[idx, "Budget"] = float(budget_fields[cat].value or 0)
                    except ValueError:
                        pass
            ds.save_budget_config(budget_df)
            page.snack_bar = ft.SnackBar(content=ft.Text("Budget saved!"), bgcolor=COLORS["success"])
            page.snack_bar.open = True
            page.update()
        
        def create_budget_section(title: str, cat_type: str, color: str):
            cats = budget_df[budget_df["Type"] == cat_type]
            fields = []
            for _, row in cats.iterrows():
                field = ft.TextField(
                    value=str(int(row["Budget"])),
                    label=row["Category"],
                    width=150,
                    text_size=14,
                    bgcolor=COLORS["surface_variant"],
                    border_color=color,
                )
                budget_fields[row["Category"]] = field
                fields.append(field)
            
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(width=4, height=20, bgcolor=color, border_radius=2),
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                    ], spacing=10),
                    ft.Row(fields, wrap=True, spacing=10),
                ], spacing=10),
                padding=20,
                bgcolor=COLORS["surface"],
                border_radius=12,
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("💰 Budget Config", size=28, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                ft.Text("Set your monthly budget for each category", color=COLORS["on_surface_variant"]),
                ft.Container(height=10),
                create_budget_section("Income", "Income", COLORS["success"]),
                create_budget_section("Expenses", "Expenses", COLORS["error"]),
                create_budget_section("Bills", "Bills", COLORS["warning"]),
                create_budget_section("Savings", "Savings", COLORS["primary"]),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Save Budget",
                    icon=ft.Icons.SAVE,
                    on_click=save_budget,
                    bgcolor=COLORS["primary"],
                    color="#ffffff",
                ),
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True,
        )
    
    # ===== MANAGER VIEW =====
    def create_manager_view():
        transactions_df = ds.load_transactions()
        budget_df = ds.load_budget_config()
        categories = budget_df["Category"].tolist()
        types = budget_df["Type"].unique().tolist()
        
        # Form fields
        date_field = ft.TextField(
            value=datetime.now().strftime("%Y-%m-%d"),
            label="Date (YYYY-MM-DD)",
            width=150,
            bgcolor=COLORS["surface_variant"],
        )
        category_dropdown = ft.Dropdown(
            label="Category",
            options=[ft.dropdown.Option(c) for c in categories],
            width=200,
            bgcolor=COLORS["surface_variant"],
        )
        amount_field = ft.TextField(
            label="Amount",
            width=100,
            bgcolor=COLORS["surface_variant"],
        )
        note_field = ft.TextField(
            label="Note (optional)",
            width=200,
            bgcolor=COLORS["surface_variant"],
        )
        
        trans_list = ft.Ref[ft.Column]()
        
        def refresh_transactions():
            nonlocal transactions_df
            transactions_df = ds.load_transactions()
            if trans_list.current:
                trans_list.current.controls = build_transaction_rows()
                page.update()
        
        def add_transaction(e):
            if not category_dropdown.value or not amount_field.value:
                return
            cat_type = budget_df[budget_df["Category"] == category_dropdown.value]["Type"].values[0]
            ds.add_transaction(
                date_field.value,
                category_dropdown.value,
                cat_type,
                float(amount_field.value),
                note_field.value or ""
            )
            amount_field.value = ""
            note_field.value = ""
            refresh_transactions()
            page.snack_bar = ft.SnackBar(content=ft.Text("Transaction added!"), bgcolor=COLORS["success"])
            page.snack_bar.open = True
            page.update()
        
        def delete_transaction(trans_id):
            ds.delete_transaction(trans_id)
            refresh_transactions()
            page.snack_bar = ft.SnackBar(content=ft.Text("Transaction deleted!"), bgcolor=COLORS["error"])
            page.snack_bar.open = True
            page.update()
        
        def build_transaction_rows():
            rows = []
            sorted_df = transactions_df.sort_values("Date", ascending=False) if len(transactions_df) > 0 else transactions_df
            for _, row in sorted_df.head(20).iterrows():
                type_color = COLORS["success"] if row.get("Type") == "Income" else COLORS["error"]
                rows.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(str(row.get("Date", ""))[:10], color=COLORS["on_surface_variant"], width=100),
                            ft.Text(str(row.get("Category", "")), color=COLORS["on_surface"], width=150),
                            ft.Text(f"${row.get('Actual', 0):.2f}", color=type_color, width=80),
                            ft.Text(str(row.get("Note", ""))[:20], color=COLORS["on_surface_variant"], expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=COLORS["error"],
                                on_click=lambda e, tid=row.get("id"): delete_transaction(tid),
                            ),
                        ], spacing=10),
                        padding=10,
                        bgcolor=COLORS["surface"],
                        border_radius=8,
                    )
                )
            return rows if rows else [ft.Text("No transactions yet", color=COLORS["on_surface_variant"])]
        
        return ft.Container(
            content=ft.Column([
                ft.Text("📝 Transaction Manager", size=28, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                ft.Container(height=10),
                # Add transaction form
                ft.Container(
                    content=ft.Column([
                        ft.Text("Add Transaction", weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                        ft.Row([date_field, category_dropdown, amount_field, note_field], spacing=10, wrap=True),
                        ft.ElevatedButton(
                            "Add Transaction",
                            icon=ft.Icons.ADD,
                            on_click=add_transaction,
                            bgcolor=COLORS["primary"],
                            color="#ffffff",
                        ),
                    ], spacing=10),
                    padding=20,
                    bgcolor=COLORS["surface"],
                    border_radius=12,
                ),
                ft.Container(height=20),
                ft.Text("Recent Transactions", weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                ft.Column(build_transaction_rows(), ref=trans_list, spacing=5),
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True,
        )
    
    # ===== HISTORY VIEW =====
    def create_history_view():
        # Get last 8 weeks
        weeks = []
        current = datetime.now()
        for i in range(8):
            week_date = current - timedelta(days=7 * i)
            start, end = ds.get_week_dates(week_date)
            data = ds.get_weekly_data(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
            weeks.append({
                "start": start,
                "end": end,
                "totals": data["totals"],
            })
        
        def create_week_card(week_data):
            totals = week_data["totals"]
            balance_color = COLORS["success"] if totals["balance"] >= 0 else COLORS["error"]
            
            return ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(
                            f"{week_data['start'].strftime('%b %d')} - {week_data['end'].strftime('%b %d, %Y')}",
                            weight=ft.FontWeight.BOLD,
                            color=COLORS["on_surface"]
                        ),
                    ], expand=True),
                    ft.Column([
                        ft.Text(f"Income: ${totals['income']:.0f}", color=COLORS["success"], size=12),
                        ft.Text(f"Expenses: ${totals['expenses']:.0f}", color=COLORS["error"], size=12),
                    ]),
                    ft.Column([
                        ft.Text(f"Balance", color=COLORS["on_surface_variant"], size=10),
                        ft.Text(f"${totals['balance']:.0f}", color=balance_color, size=18, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END, width=100),
                ], spacing=20),
                padding=20,
                bgcolor=COLORS["surface"],
                border_radius=12,
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("📅 History", size=28, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                ft.Text("Your weekly spending history", color=COLORS["on_surface_variant"]),
                ft.Container(height=10),
                *[create_week_card(w) for w in weeks],
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True,
        )
    
    # ===== NAVIGATION =====
    def on_nav_change(e):
        """Handle navigation rail selection changes."""
        index = e.control.selected_index
        views = [
            create_dashboard_view,
            create_statistics_view,
            create_budget_view,
            create_manager_view,
            create_history_view,
        ]
        content_area.content = views[index]()
        page.update()
    
    # Load profile
    profile = ds.load_profile()
    
    # Profile name reference for updating
    profile_name_display = ft.Text(profile.get("name", "User"), color=COLORS["on_surface_variant"], size=12)
    profile_avatar = ft.CircleAvatar(
        content=ft.Text(profile.get("name", "U")[0].upper()),
        bgcolor=COLORS["primary"],
        radius=18,
    )
    
    # Profile edit dialog
    profile_name_field = ft.TextField(
        value=profile.get("name", "User"),
        label="Your Name",
        width=250,
        bgcolor=COLORS["surface_variant"],
    )
    
    def save_profile(e):
        new_name = profile_name_field.value or "User"
        ds.save_profile({"name": new_name})
        profile_name_display.value = new_name
        profile_avatar.content = ft.Text(new_name[0].upper())
        profile_dialog.open = False
        page.snack_bar = ft.SnackBar(content=ft.Text("Profile saved!"), bgcolor=COLORS["success"])
        page.snack_bar.open = True
        page.update()
    
    def close_dialog(e):
        profile_dialog.open = False
        page.update()
    
    profile_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Profile", weight=ft.FontWeight.BOLD),
        content=ft.Column([
            profile_name_field,
        ], tight=True, spacing=10),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.ElevatedButton("Save", on_click=save_profile, bgcolor=COLORS["primary"], color="#ffffff"),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def open_profile_dialog(e):
        profile_name_field.value = profile_name_display.value
        page.overlay.append(profile_dialog)
        profile_dialog.open = True
        page.update()
    
    # Navigation Rail
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=180,
        extended=True,
        bgcolor=COLORS["surface"],
        indicator_color=COLORS["primary"],
        on_change=on_nav_change,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.BAR_CHART_OUTLINED,
                selected_icon=ft.Icons.BAR_CHART,
                label="Statistics",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                selected_icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
                label="Budget",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.EDIT_NOTE_OUTLINED,
                selected_icon=ft.Icons.EDIT_NOTE,
                label="Manager",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.HISTORY_OUTLINED,
                selected_icon=ft.Icons.HISTORY,
                label="History",
            ),
        ],
        # Profile section at bottom - now clickable
        trailing=ft.Container(
            content=ft.Column([
                ft.Divider(color=COLORS["surface_variant"]),
                ft.Container(
                    content=ft.Row([
                        profile_avatar,
                        profile_name_display,
                        ft.Icon(ft.Icons.EDIT, size=14, color=COLORS["on_surface_variant"]),
                    ], spacing=8),
                    padding=ft.Padding(left=10, top=0, right=10, bottom=20),
                    on_click=open_profile_dialog,
                    ink=True,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.Alignment(0, 1),  # bottom_center
        ),
    )
    
    # Main content area
    content_area = ft.Container(
        content=create_dashboard_view(),
        expand=True,
        bgcolor=COLORS["background"],
    )
    
    # Main layout
    page.add(
        ft.Row(
            [
                nav_rail,
                ft.VerticalDivider(width=1, color=COLORS["surface_variant"]),
                content_area,
            ],
            expand=True,
            spacing=0,
        )
    )


if __name__ == "__main__":
    ft.app(main)
