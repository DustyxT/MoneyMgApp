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


def create_editable_data_table(title: str, columns: list, data: list, color: str, 
                                on_value_change, on_budget_change, page) -> ft.Container:
    """Create a styled data table with editable Budget and Actual columns and calculated Difference."""
    
    # Add Difference column if not present
    display_columns = list(columns)
    if "Difference" not in display_columns:
        display_columns.append("Difference")
        
    header_row = ft.Row(
        [
            ft.Text(display_columns[0], weight=ft.FontWeight.BOLD, color=COLORS["on_surface_variant"], size=12, expand=3), # Category
            ft.Text(display_columns[1], weight=ft.FontWeight.BOLD, color=COLORS["on_surface_variant"], size=12, expand=1, text_align=ft.TextAlign.RIGHT), # Budget
            ft.Text(display_columns[2], weight=ft.FontWeight.BOLD, color=COLORS["on_surface_variant"], size=12, expand=1, text_align=ft.TextAlign.RIGHT), # Actual
            ft.Text(display_columns[3], weight=ft.FontWeight.BOLD, color=COLORS["on_surface_variant"], size=12, expand=1, text_align=ft.TextAlign.RIGHT), # Difference
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )
    
    data_rows = []
    for item in data:
        category = item["category"]
        budget = item["budget"]
        actual = item["actual"]
        # For Income: earning more than budget is positive (Actual - Budget)
        # For Expenses/Bills/Savings: spending less than budget is positive (Budget - Actual)
        if title == "Income":
            difference = actual - budget
        else:
            difference = budget - actual
        
        # Determine difference color
        diff_color = COLORS["success"] if difference >= 0 else COLORS["error"]
        
        # Difference text control
        diff_text = ft.Text(
            f"${difference:,.2f}", 
            color=diff_color, 
            size=14, 
            weight=ft.FontWeight.BOLD,
            expand=1,
            text_align=ft.TextAlign.RIGHT
        )
        
        # Common text field style
        field_style = {
            "expand": 1,
            "height": 35,
            "text_size": 13,
            "color": COLORS["on_surface"],
            "bgcolor": COLORS["surface_variant"],
            "border_color": "transparent",
            "focused_border_color": color,
            "border_radius": 6,
            "text_align": ft.TextAlign.RIGHT,
            "content_padding": ft.Padding(left=10, top=0, right=10, bottom=0),
            "prefix": ft.Text("$", size=12, color=COLORS["on_surface_variant"]),
        }

        # Create editable TextField for Budget value
        budget_field = ft.TextField(
             value=str(int(budget)) if budget == int(budget) else f"{budget:.2f}",
             **field_style
        )

        # Create editable TextField for Actual value
        actual_field = ft.TextField(
            value=str(int(actual)) if actual == int(actual) else f"{actual:.2f}",
            **field_style
        )
        
        # Real-time update logic
        def update_diff(e, b_field=budget_field, a_field=actual_field, d_text=diff_text):
            try:
                b_val = float(b_field.value) if b_field.value else 0
                a_val = float(a_field.value) if a_field.value else 0
                # For Income: earning more is positive (Actual - Budget)
                # For others: spending less is positive (Budget - Actual)
                if title == "Income":
                    diff = a_val - b_val
                else:
                    diff = b_val - a_val
                d_text.value = f"${diff:,.2f}"
                d_text.color = COLORS["success"] if diff >= 0 else COLORS["error"]
                d_text.update()
            except ValueError:
                pass
        
        # Bind events
        budget_field.on_change = update_diff
        budget_field.on_blur = lambda e, cat=category: on_budget_change(cat, e.control.value)
        budget_field.on_submit = lambda e, cat=category: on_budget_change(cat, e.control.value)
        
        actual_field.on_change = update_diff
        actual_field.on_blur = lambda e, cat=category: on_value_change(cat, e.control.value)
        actual_field.on_submit = lambda e, cat=category: on_value_change(cat, e.control.value)
        
        # Row layout
        data_rows.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(category, color=COLORS["on_surface"], size=14, expand=3, overflow=ft.TextOverflow.ELLIPSIS),
                    budget_field,
                    actual_field,
                    diff_text,
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(0, 5, 0, 5),
                border=ft.Border.only(bottom=ft.BorderSide(1, COLORS["surface_variant"]))
            )
        )
    
    return ft.Container(
        content=ft.Column(
            [
                ft.Row([
                    ft.Container(width=4, height=16, bgcolor=color, border_radius=2),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=10),
                header_row,
                ft.Column(data_rows, spacing=2),
            ],
            spacing=0,
        ),
        bgcolor=COLORS["surface"],
        padding=15,
        border_radius=10,
    )


def create_calendar_picker(current_date: datetime, on_date_select, on_week_select) -> ft.Container:
    """Create a calendar month view with week highlighting."""
    import calendar
    
    year = current_date.year
    month = current_date.month
    cal = calendar.Calendar(firstweekday=6)  # Start on Sunday
    month_days = list(cal.itermonthdays2(year, month))
    
    # Month navigation
    month_label = ft.Text(
        current_date.strftime("%B %Y"),
        size=16,
        weight=ft.FontWeight.BOLD,
        color=COLORS["on_surface"],
    )
    
    # Day headers
    day_headers = ft.Row(
        [ft.Text(d, size=12, color=COLORS["on_surface_variant"], width=35, text_align=ft.TextAlign.CENTER) 
         for d in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]],
        spacing=2,
    )
    
    # Build weeks
    weeks = []
    current_week = []
    
    for day, weekday in month_days:
        if day == 0:
            current_week.append(
                ft.Container(width=35, height=35)  # Empty cell
            )
        else:
            day_date = datetime(year, month, day)
            is_today = day_date.date() == datetime.now().date()
            
            day_btn = ft.Container(
                content=ft.Text(
                    str(day),
                    size=12,
                    color=COLORS["on_surface"] if not is_today else COLORS["background"],
                    text_align=ft.TextAlign.CENTER,
                ),
                width=35,
                height=35,
                bgcolor=COLORS["primary"] if is_today else None,
                border_radius=17,
                alignment=ft.Alignment(0, 0),
                on_click=lambda e, d=day_date: on_date_select(d),
                data=day_date,
            )
            current_week.append(day_btn)
        
        if len(current_week) == 7:
            # Create week row with hover effect
            week_row = ft.Container(
                content=ft.Row(current_week, spacing=2),
                border_radius=4,
                on_hover=lambda e: _highlight_week(e),
                on_click=lambda e, days=current_week: on_week_select(days),
            )
            weeks.append(week_row)
            current_week = []
    
    # Add remaining days
    if current_week:
        while len(current_week) < 7:
            current_week.append(ft.Container(width=35, height=35))
        week_row = ft.Container(
            content=ft.Row(current_week, spacing=2),
            border_radius=4,
            on_hover=lambda e: _highlight_week(e),
        )
        weeks.append(week_row)
    
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.CHEVRON_LEFT, icon_size=16, icon_color=COLORS["on_surface_variant"]),
                month_label,
                ft.IconButton(ft.Icons.CHEVRON_RIGHT, icon_size=16, icon_color=COLORS["on_surface_variant"]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            day_headers,
            *weeks,
        ], spacing=5),
        padding=15,
        bgcolor=COLORS["surface"],
        border_radius=12,
        width=280,
    )


def _highlight_week(e):
    """Highlight week row on hover."""
    if e.data == "true":
        e.control.bgcolor = COLORS["surface_variant"]
    else:
        e.control.bgcolor = None
    e.control.update()


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
    
    # Independent state for Statistics view
    stats_week_start, stats_week_end = ds.get_week_dates(current_date)
    
    # Independent state for Budget view
    budget_week_start, budget_week_end = ds.get_week_dates(current_date)
    
    
    # Manager now uses shared week_start/end for sync with Dashboard
    
    # Week picker label
    week_label = ft.Text(
        f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
        size=16,
        weight=ft.FontWeight.BOLD,
        color=COLORS["on_surface"],
    )
    
    # Content container reference
    content_container = ft.Ref[ft.Container]()
    
    # Track current view index
    current_view_index = 0
    
    def navigate_week(delta: int):
        """Navigate to previous/next week."""
        nonlocal week_start, week_end
        week_start += timedelta(days=7 * delta)
        week_end += timedelta(days=7 * delta)
        week_label.value = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
        refresh_current_view()
    
    def refresh_current_view():
        """Refresh current view data."""
        if current_view_index == 0:
            content_area.content = create_dashboard_view()
        elif current_view_index == 1:
            content_area.content = create_statistics_view()
        elif current_view_index == 2:
            content_area.content = create_budget_view()
        elif current_view_index == 3:
            content_area.content = create_manager_view()
        elif current_view_index == 4:
            content_area.content = create_history_view()
        page.update()
    
    # Custom Calendar Implementation
    def create_custom_calendar(year, month, on_date_select_callback):
        import calendar
        # Calender starting on Monday (0)
        cal = calendar.Calendar(firstweekday=0)
        month_days = list(cal.itermonthdays2(year, month))
        
        # Navigation
        def prev_month(e):
            nonlocal current_cal_date
            # Calculate previous month
            if current_cal_date.month == 1:
                current_cal_date = datetime(current_cal_date.year - 1, 12, 1)
            else:
                current_cal_date = datetime(current_cal_date.year, current_cal_date.month - 1, 1)
            on_date_select_callback() # Refresh calendar UI

        def next_month(e):
            nonlocal current_cal_date
            # Calculate next month
            if current_cal_date.month == 12:
                current_cal_date = datetime(current_cal_date.year + 1, 1, 1)
            else:
                current_cal_date = datetime(current_cal_date.year, current_cal_date.month + 1, 1)
            on_date_select_callback() # Refresh calendar UI
        
        # Header
        header = ft.Row([
            ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=prev_month, icon_color=COLORS["on_surface"]),
            ft.Text(f"{calendar.month_name[month]} {year}", weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
            ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=next_month, icon_color=COLORS["on_surface"]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Days of week header
        days_header = ft.Row([
            ft.Container(content=ft.Text(day, size=12, color=COLORS["on_surface_variant"], text_align=ft.TextAlign.CENTER), width=35, alignment=ft.Alignment(0, 0))
            for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        ], spacing=2)
        
        calendar_rows = [header, days_header]
        
        # Build weeks
        week_days = []
        for day, weekday in month_days:
            if day == 0:
                day_content = ft.Container(width=35, height=35)
            else:
                is_today = (datetime.now().year == year and datetime.now().month == month and datetime.now().day == day)
                day_content = ft.Container(
                    content=ft.Text(str(day), size=12, 
                                  color=COLORS["background"] if is_today else COLORS["on_surface"]),
                    width=35, height=35,
                    bgcolor=COLORS["primary"] if is_today else None,
                    border_radius=50,
                    alignment=ft.Alignment(0, 0)
                )
            
            week_days.append(day_content)
            
            if len(week_days) == 7:
                # Create a copy of the list for the closure
                current_week_days_data = []
                # Find a valid date in this week to use for selection
                valid_date = None
                for d, wd in month_days[month_days.index((day, weekday))-6 : month_days.index((day, weekday))+1]:
                        if d != 0:
                            valid_date = datetime(year, month, d)
                            break
                
                if valid_date:
                    # Full week row with hover
                    week_row = ft.Container(
                        content=ft.Row(week_days, spacing=2),
                        padding=2,
                        border_radius=5,
                        on_hover=lambda e: highlight_week_row(e),
                        on_click=lambda e, d=valid_date: select_week_from_cal(d),
                        ink=True,
                    )
                    calendar_rows.append(week_row)
                else:
                        # Should not happen typically with standard calendar months logic but safe fallback
                        calendar_rows.append(ft.Row(week_days, spacing=2))
                
                week_days = []
        
        return ft.Column(calendar_rows, spacing=5)

    def highlight_week_row(e):
        e.control.bgcolor = COLORS["surface_variant"] if e.data == "true" else None
        e.control.update()

    def select_week_from_cal(date_in_week):
        nonlocal week_start, week_end
        week_start, week_end = ds.get_week_dates(date_in_week)
        # We need to update ALL week labels if we had multiple, but we rely on refresh_current_view
        # to rebuild the UI which will call create_week_nav again with new date.
        refresh_current_view()

    def go_to_today():
        nonlocal week_start, week_end
        week_start, week_end = ds.get_week_dates(datetime.now())
        refresh_current_view()

    # Calendar state
    current_cal_date = datetime.now()

    def create_week_nav():
        """Factory to create a fresh week navigation and calendar control."""
        
        calendar_container = ft.Container(
            visible=False,
            bgcolor=COLORS["surface"],
            padding=15,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, color="#80000000"),
            width=300,
            alignment=ft.Alignment(0, 0)
        )

        def update_calendar_ui():
            calendar_container.content = create_custom_calendar(current_cal_date.year, current_cal_date.month, update_calendar_ui)
            if calendar_container.visible:
                calendar_container.update()

        def toggle_calendar(e):
            calendar_container.visible = not calendar_container.visible
            if calendar_container.visible:
                update_calendar_ui()
            page.update()

        # Create fresh week label
        current_week_label = ft.Text(
            f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=COLORS["on_surface"],
        )
        
        nav_row = ft.Row([
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=lambda _: navigate_week(-1),
                icon_color=COLORS["on_surface"],
                tooltip="Previous week",
            ),
            ft.Container(
                content=ft.Row([
                    current_week_label,
                    ft.Icon(ft.Icons.CALENDAR_MONTH, size=18, color=COLORS["primary"]),
                ], spacing=8),
                bgcolor=COLORS["surface"],
                padding=ft.Padding(left=20, top=10, right=20, bottom=10),
                border_radius=8,
                on_click=toggle_calendar,
                ink=True,
                tooltip="Click to open calendar",
            ),
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                on_click=lambda _: navigate_week(1),
                icon_color=COLORS["on_surface"],
                tooltip="Next week",
            ),
            ft.IconButton(
                icon=ft.Icons.TODAY,
                tooltip="Go to current week",
                on_click=lambda _: go_to_today(),
                icon_color=COLORS["primary"],
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)

        return ft.Column([
            nav_row,
            ft.Row([calendar_container], alignment=ft.MainAxisAlignment.CENTER)
        ])

    # ===== DASHBOARD VIEW =====
    def create_dashboard_view():
        nonlocal metrics_row, income_table, expenses_table, bills_table, savings_table, investments_table
        
        # ... (rest of dashboard view code matches existing)

    # Note: Using replace_file_content, I need to be careful not to delete the huge dashboard function.
    # I will target specific blocks. This replacement handles the refresh logic and state.
    
    # [SKIP TO STATS VIEW MODIFICATION]
    
    # Stats navigation helper functions (must be defined before create_stats_week_nav)
    def navigate_stats_week(delta: int):
        nonlocal stats_week_start, stats_week_end
        stats_week_start += timedelta(days=7 * delta)
        stats_week_end += timedelta(days=7 * delta)
        refresh_current_view()

    def navigate_stats_today():
        nonlocal stats_week_start, stats_week_end
        stats_week_start, stats_week_end = ds.get_week_dates(datetime.now())
        refresh_current_view()
        
    def select_stats_week(date_in_week):
        nonlocal stats_week_start, stats_week_end
        stats_week_start, stats_week_end = ds.get_week_dates(date_in_week)
        refresh_current_view()
    
    # Separate Stats Navigation
    def create_stats_week_nav():
        """Factory specifically for Statistics view independent navigation."""
        
        # Local calendar container for stats
        stats_calendar_container = ft.Container(
            visible=False,
            bgcolor=COLORS["surface"],
            padding=15,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, color="#80000000"),
            width=300,
            alignment=ft.Alignment(0, 0)
        )
        
        # Local stats calendar state
        # We need a closure for current_cal_date specific to this instance/view
        current_stats_cal_date = datetime.now()

        def update_stats_calendar_ui():
            # We can reuse create_custom_calendar because it renders UI based on year/month
            # We just need to wrap the callback to update THIS container and variable
            
            # Helper to handle date selection in stats context
            def on_stats_date_nav():
                 nonlocal current_stats_cal_date
                 # Logic is internal to create_custom_calendar's next/prev buttons which modify 
                 # the variable passed to it? No, create_custom_calendar uses variable from scope.
                 # Wait, create_custom_calendar in current implementation uses 'current_cal_date' from MAIN scope.
                 # We need to make create_custom_calendar fully parameterized or duplicate it slightly 
                 # to use 'current_stats_cal_date'.
                 pass

            # Since create_custom_calendar relies on 'current_cal_date' from main scope, 
            # we should refactor create_custom_calendar to accept the date object.
            # But to avoid breaking dashboard, I will create a stats-specific renderer here.
            
            stats_calendar_container.content = create_stats_calendar_renderer(
                current_stats_cal_date.year, 
                current_stats_cal_date.month
            )
            if stats_calendar_container.visible:
                stats_calendar_container.update()

        def create_stats_calendar_renderer(year, month):
            import calendar
            cal = calendar.Calendar(firstweekday=0)
            month_days = list(cal.itermonthdays2(year, month))
            
            def prev_month(e):
                nonlocal current_stats_cal_date
                if current_stats_cal_date.month == 1:
                    current_stats_cal_date = datetime(current_stats_cal_date.year - 1, 12, 1)
                else:
                    current_stats_cal_date = datetime(current_stats_cal_date.year, current_stats_cal_date.month - 1, 1)
                update_stats_calendar_ui()

            def next_month(e):
                nonlocal current_stats_cal_date
                if current_stats_cal_date.month == 12:
                    current_stats_cal_date = datetime(current_stats_cal_date.year + 1, 1, 1)
                else:
                    current_stats_cal_date = datetime(current_stats_cal_date.year, current_stats_cal_date.month + 1, 1)
                update_stats_calendar_ui()
            
            header = ft.Row([
                ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=prev_month, icon_color=COLORS["on_surface"]),
                ft.Text(f"{calendar.month_name[month]} {year}", weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=next_month, icon_color=COLORS["on_surface"]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            
            days_header = ft.Row([
                ft.Container(content=ft.Text(day, size=12, color=COLORS["on_surface_variant"], text_align=ft.TextAlign.CENTER), width=35, alignment=ft.Alignment(0, 0))
                for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            ], spacing=2)
            
            calendar_rows = [header, days_header]
            
            week_days = []
            for day, weekday in month_days:
                if day == 0:
                    day_content = ft.Container(width=35, height=35)
                else:
                    is_today = (datetime.now().year == year and datetime.now().month == month and datetime.now().day == day)
                    day_content = ft.Container(
                        content=ft.Text(str(day), size=12, 
                                      color=COLORS["background"] if is_today else COLORS["on_surface"]),
                        width=35, height=35,
                        bgcolor=COLORS["primary"] if is_today else None,
                        border_radius=50,
                        alignment=ft.Alignment(0, 0)
                    )
                week_days.append(day_content)
                
                if len(week_days) == 7:
                    valid_date = None
                    for d, wd in month_days[month_days.index((day, weekday))-6 : month_days.index((day, weekday))+1]:
                            if d != 0:
                                valid_date = datetime(year, month, d)
                                break
                    if valid_date:
                        week_row = ft.Container(
                            content=ft.Row(week_days, spacing=2),
                            padding=2,
                            border_radius=5,
                            on_hover=lambda e: highlight_week_row(e), # Reusing shared highlighter
                            on_click=lambda e, d=valid_date: select_stats_week(d),
                            ink=True,
                        )
                        calendar_rows.append(week_row)
                    else:
                        calendar_rows.append(ft.Row(week_days, spacing=2))
                    week_days = []
            
            return ft.Column(calendar_rows, spacing=5)


        # Note: select_stats_week is defined in main scope (after this factory function)
        # The lambda in on_click will correctly call the outer-scope function

        def toggle_stats_calendar(e):
            stats_calendar_container.visible = not stats_calendar_container.visible
            if stats_calendar_container.visible:
                update_stats_calendar_ui()
            page.update()

        def nav_stats_week(delta):
            # We need to modify the main scope stats_week_start
            # Since we can't easily nonlocal it from this nested depth without chaining,
            # we will set it directly if possible or trigger a refresh that handles it.
            # Actually, we can define 'navigate_stats_week' in main scope similarly to 'navigate_week'.
            navigate_stats_week(delta)

        def go_to_stats_today():
            navigate_stats_today()

        # Create fresh week label
        stats_week_label = ft.Text(
            f"{stats_week_start.strftime('%b %d')} - {stats_week_end.strftime('%b %d, %Y')}",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=COLORS["on_surface"],
        )
        
        nav_row = ft.Row([
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=lambda _: nav_stats_week(-1),
                icon_color=COLORS["on_surface"],
                tooltip="Previous week",
            ),
            ft.Container(
                content=ft.Row([
                    stats_week_label,
                    ft.Icon(ft.Icons.CALENDAR_MONTH, size=18, color=COLORS["primary"]),
                ], spacing=8),
                bgcolor=COLORS["surface"],
                padding=ft.Padding(left=20, top=10, right=20, bottom=10),
                border_radius=8,
                on_click=toggle_stats_calendar,
                ink=True,
                tooltip="Click to open calendar",
            ),
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                on_click=lambda _: nav_stats_week(1),
                icon_color=COLORS["on_surface"],
                tooltip="Next week",
            ),
            ft.IconButton(
                icon=ft.Icons.TODAY,
                tooltip="Go to current week",
                on_click=lambda _: go_to_stats_today(),
                icon_color=COLORS["primary"],
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)

        return ft.Column([
            nav_row,
            ft.Row([stats_calendar_container], alignment=ft.MainAxisAlignment.CENTER)
        ])

    # ===== HISTORY VIEW =====
    # ... (existing history view)

    # ===== NAVIGATION =====
    def on_nav_change(e):
        """Handle navigation rail selection changes."""
        nonlocal current_view_index
        index = e.control.selected_index
        current_view_index = index
        refresh_current_view()
    
    # ===== DASHBOARD VIEW =====
    def create_dashboard_view():
        nonlocal metrics_row, income_table, expenses_table, bills_table, savings_table, investments_table
        
        # Track pending changes 
        pending_changes = {}
        
        # ===== NAMED REFERENCES FOR LIVE-UPDATING STATS =====
        # Budget Overview card texts
        budget_total_value = ft.Text("$0.00", size=22, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"])
        budget_total_subtitle = ft.Text("Expenses + Bills weekly", size=10, color=COLORS["on_surface_variant"])
        
        spent_value = ft.Text("$0.00", size=22, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"])
        spent_subtitle = ft.Text("0% of budget used", size=10, color=COLORS["on_surface_variant"])
        spent_progress_bar = ft.Container(bgcolor=COLORS["success"], border_radius=4, height=6, width=0)
        
        remaining_value = ft.Text("$0.00", size=22, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"])
        remaining_subtitle = ft.Text("Left to spend", size=10, color=COLORS["on_surface_variant"])
        remaining_icon_container = ft.Container(
            content=ft.Icon(ft.Icons.SAVINGS, color="#ffffff", size=18),
            bgcolor=COLORS["success"], padding=8, border_radius=8,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color=f"{COLORS['success']}50", offset=ft.Offset(0, 2)),
        )
        
        # Status badge
        status_icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color=COLORS["success"], size=14)
        status_text = ft.Text("On Track", size=11, color=COLORS["success"], weight=ft.FontWeight.W_600)
        status_badge = ft.Container(
            content=ft.Row([status_icon, status_text], spacing=4),
            bgcolor=f"{COLORS['success']}15",
            padding=ft.Padding(10, 4, 10, 4),
            border_radius=20,
        )
        
        # Actual Stats card texts
        cashflow_value = ft.Text("$0.00", size=22, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"])
        cashflow_subtitle = ft.Text("No outflow yet", size=10, color=COLORS["on_surface_variant"])
        cashflow_icon_container = ft.Container(
            content=ft.Icon(ft.Icons.SWAP_VERT, color="#ffffff", size=18),
            bgcolor=COLORS["success"], padding=8, border_radius=8,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color=f"{COLORS['success']}50", offset=ft.Offset(0, 2)),
        )
        
        biggest_value = ft.Text("$0.00", size=22, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"])
        biggest_subtitle = ft.Text("N/A", size=10, color=COLORS["on_surface_variant"])
        
        savings_rate_value = ft.Text("0.0%", size=22, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"])
        savings_rate_subtitle = ft.Text("$0.00 saved this week", size=10, color=COLORS["on_surface_variant"])
        savings_rate_bar = ft.Container(bgcolor=COLORS["warning"], border_radius=4, height=6, width=0)
        savings_rate_icon_container = ft.Container(
            content=ft.Icon(ft.Icons.TRENDING_UP, color="#ffffff", size=18),
            bgcolor=COLORS["warning"], padding=8, border_radius=8,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color=f"{COLORS['warning']}50", offset=ft.Offset(0, 2)),
        )
        
        _initializing = True
        
        def update_metrics():
            """Recalculate and update top metric cards AND budget/actual stats."""
            # Calculate totals from current data state
            total_income = sum(item["actual"] for item in data["income"])
            total_expenses = sum(item["actual"] for item in data["expenses"])
            total_bills = sum(item["actual"] for item in data["bills"])
            total_savings = sum(item["actual"] for item in data["savings"])
            total_investments = sum(item["actual"] for item in data.get("investments", []))
            
            # Expenses include bills
            final_expenses = total_expenses + total_bills
            
            # Balance = Income - Expenses - Savings - Investments
            balance = total_income - final_expenses - total_savings - total_investments
            
            # Update metric cards
            metrics_row.controls[0].content.controls[1].value = f"${total_income:,.2f}"
            metrics_row.controls[1].content.controls[1].value = f"${final_expenses:,.2f}"
            metrics_row.controls[2].content.controls[1].value = f"${total_savings:,.2f}"
            metrics_row.controls[3].content.controls[1].value = f"${total_investments:,.2f}"
            metrics_row.controls[4].content.controls[1].value = f"${balance:,.2f}"
            metrics_row.controls[4].content.controls[1].color = COLORS["success"] if balance >= 0 else COLORS["error"]
            if not _initializing:
                metrics_row.update()
            
            # ===== UPDATE BUDGET OVERVIEW =====
            total_expense_budget = sum(item["budget"] for item in data["expenses"])
            total_bills_budget = sum(item["budget"] for item in data["bills"])
            total_spending_budget = total_expense_budget + total_bills_budget
            total_spending_actual = total_expenses + total_bills
            s_remaining = total_spending_budget - total_spending_actual
            s_pct = (total_spending_actual / total_spending_budget * 100) if total_spending_budget > 0 else 0
            
            # Budget total card
            budget_total_value.value = f"${total_spending_budget:,.2f}"
            
            # Spent card
            spent_value.value = f"${total_spending_actual:,.2f}"
            spent_subtitle.value = f"{s_pct:.0f}% of budget used"
            bar_pct = s_pct / 100
            bar_color = COLORS["success"] if bar_pct <= 0.75 else (COLORS["warning"] if bar_pct <= 1.0 else COLORS["error"])
            spent_progress_bar.bgcolor = bar_color
            spent_progress_bar.width = max(0, min(bar_pct, 1.0)) * 200
            
            # Remaining card
            remaining_value.value = f"${s_remaining:,.2f}"
            remaining_subtitle.value = "Left to spend" if s_remaining >= 0 else "Over budget!"
            rem_color = COLORS["success"] if s_remaining >= 0 else COLORS["error"]
            remaining_icon_container.bgcolor = rem_color
            remaining_icon_container.shadow = ft.BoxShadow(spread_radius=0, blur_radius=8, color=f"{rem_color}50", offset=ft.Offset(0, 2))
            
            # Status badge
            if s_pct <= 75:
                u_color, u_text, u_icon = COLORS["success"], "On Track", ft.Icons.CHECK_CIRCLE
            elif s_pct <= 100:
                u_color, u_text, u_icon = COLORS["warning"], "Caution", ft.Icons.WARNING
            else:
                u_color, u_text, u_icon = COLORS["error"], "Over Budget", ft.Icons.ERROR
            status_icon.name = u_icon
            status_icon.color = u_color
            status_text.value = u_text
            status_text.color = u_color
            status_badge.bgcolor = f"{u_color}15"
            
            if not _initializing:
                budget_stats_section.update()
            
            # ===== UPDATE ACTUAL STATS =====
            outflow = total_spending_actual + total_savings + total_investments
            i_coverage = (total_income / outflow * 100) if outflow > 0 else 0
            n_flow = total_income - outflow
            
            cashflow_value.value = f"${n_flow:,.2f}"
            cashflow_subtitle.value = f"Income covers {i_coverage:.0f}% of outflow" if outflow > 0 else "No outflow yet"
            cf_color = COLORS["success"] if n_flow >= 0 else COLORS["error"]
            cashflow_icon_container.bgcolor = cf_color
            cashflow_icon_container.shadow = ft.BoxShadow(spread_radius=0, blur_radius=8, color=f"{cf_color}50", offset=ft.Offset(0, 2))
            
            # Biggest expense (handle ties)
            all_spend = data["expenses"] + data["bills"]
            if all_spend:
                max_val = max(item["actual"] for item in all_spend)
                top_cats = [item["category"] for item in all_spend if item["actual"] == max_val and item["actual"] > 0]
                biggest_value.value = f"${max_val:,.2f}"
                biggest_subtitle.value = ", ".join(top_cats) if top_cats else "No spending yet"
            else:
                biggest_value.value = "$0.00"
                biggest_subtitle.value = "N/A"
            
            # Savings rate
            sv_rate = (total_savings / total_income * 100) if total_income > 0 else 0
            savings_rate_value.value = f"{sv_rate:.1f}%"
            savings_rate_subtitle.value = f"${total_savings:,.2f} saved this week"
            sr_color = COLORS["success"] if sv_rate >= 20 else COLORS["warning"]
            savings_rate_icon_container.bgcolor = sr_color
            savings_rate_icon_container.shadow = ft.BoxShadow(spread_radius=0, blur_radius=8, color=f"{sr_color}50", offset=ft.Offset(0, 2))
            sr_bar_pct = sv_rate / 100 if total_income > 0 else 0
            savings_rate_bar.bgcolor = sr_color
            savings_rate_bar.width = max(0, min(sr_bar_pct, 1.0)) * 200
            
            if not _initializing:
                actual_stats_section.update()

        def on_actual_change(category: str, value: str, data_type: str):
            """Handle actual value changes from editable fields."""
            try:
                amount = float(value) if value else 0
                key = f"actual_{data_type}_{category}"
                pending_changes[key] = {
                    "category": category,
                    "type": data_type,
                    "amount": amount,
                    "is_budget": False
                }
                
                # Update local data for real-time stats
                category_list = data[data_type.lower()]
                for item in category_list:
                    if item["category"] == category:
                        item["actual"] = amount
                        break
                
                update_metrics()
            except ValueError:
                pass

        def on_budget_change(category: str, value: str):
            """Handle budget value changes from editable fields."""
            try:
                amount = float(value) if value else 0
                key = f"budget_{category}"
                pending_changes[key] = {
                    "category": category,
                    "amount": amount,
                    "is_budget": True
                }
                
                # Update local data for real-time budget stats
                for section in ["income", "expenses", "bills", "savings", "investments"]:
                    for item in data[section]:
                        if item["category"] == category:
                            item["budget"] = amount
                            update_metrics()
                            return
            except ValueError:
                pass
        
        def refresh_dashboard():
            refresh_current_view()

        def save_all_changes(e):
            """Save all pending changes."""
            if not pending_changes:
                snack = ft.SnackBar(
                    content=ft.Text("No changes to save"),
                    bgcolor=COLORS["warning"],
                    duration=3000
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
                return
            
            for key, change in pending_changes.items():
                if change.get("is_budget"):
                     # Save as weekly override
                     ds.set_weekly_budget_override(
                         week_start.strftime("%Y-%m-%d"), 
                         change["category"], 
                         change["amount"]
                     )
                else:
                    ds.update_actual_value(
                        week_start.strftime("%Y-%m-%d"),
                        week_end.strftime("%Y-%m-%d"),
                        change["category"],
                        change["type"],
                        change["amount"]
                    )
            
            pending_changes.clear()
            refresh_dashboard()
            
            # Show success message using overlay
            snack = ft.SnackBar(
                content=ft.Text("✅ Changes saved!"),
                bgcolor=COLORS["success"],
                duration=3000
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
        
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
            create_metric_card("Investments", f"${totals.get('investments', 0):,.2f}", "#14b8a6", ft.Icons.SHOW_CHART),
            create_metric_card("Balance", f"${totals['balance']:,.2f}", 
                              COLORS["success"] if totals['balance'] >= 0 else COLORS["error"], 
                              ft.Icons.ACCOUNT_BALANCE_WALLET),
        ], spacing=20)
        
        # ===== BUILD STAT CARD HELPER =====
        def create_budget_stat_card(title, value_ref, subtitle_ref, icon, icon_container_ref=None, color=COLORS["primary"], progress_bar_ref=None):
            """Create a premium budget stat card with named text references."""
            if icon_container_ref is None:
                icon_container_ref = ft.Container(
                    content=ft.Icon(icon, color="#ffffff", size=18),
                    bgcolor=color, padding=8, border_radius=8,
                    shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color=f"{color}50", offset=ft.Offset(0, 2)),
                )
            card_content = [
                ft.Row([
                    icon_container_ref,
                    ft.Text(title, size=11, color=COLORS["on_surface_variant"], weight=ft.FontWeight.W_500),
                ], spacing=10, alignment=ft.MainAxisAlignment.START),
                ft.Container(height=6),
                value_ref,
                subtitle_ref,
            ]
            if progress_bar_ref is not None:
                card_content.append(ft.Container(height=4))
                card_content.append(
                    ft.Container(
                        content=ft.Stack([
                            ft.Container(bgcolor="#333333", border_radius=4, height=6, expand=True),
                            progress_bar_ref,
                        ]),
                        height=6,
                    )
                )
            return ft.Container(
                content=ft.Column(card_content, spacing=2, horizontal_alignment=ft.CrossAxisAlignment.START),
                padding=ft.Padding(16, 14, 16, 14),
                bgcolor=COLORS["surface"],
                border_radius=14,
                border=ft.Border.all(1, f"{COLORS['surface_variant']}80"),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=15, color="#00000012", offset=ft.Offset(0, 3)),
                expand=True,
            )
        
        # Budget Overview Section
        budget_stats_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(width=4, height=20, bgcolor=COLORS["secondary"], border_radius=2),
                    ft.Text("Budget Overview", size=16, weight=ft.FontWeight.W_600, color=COLORS["on_surface"]),
                    ft.Container(expand=True),
                    status_badge,
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=6),
                ft.Row([
                    create_budget_stat_card("Total Budget", budget_total_value, budget_total_subtitle, ft.Icons.ACCOUNT_BALANCE, color=COLORS["primary"]),
                    create_budget_stat_card("Total Spent", spent_value, spent_subtitle, ft.Icons.SHOPPING_CART, color=COLORS["error"], progress_bar_ref=spent_progress_bar),
                    create_budget_stat_card("Budget Remaining", remaining_value, remaining_subtitle, ft.Icons.SAVINGS, icon_container_ref=remaining_icon_container),
                ], spacing=14),
            ], spacing=4),
        )
        
        # Actual Stats Section
        actual_stats_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(width=4, height=20, bgcolor=COLORS["success"], border_radius=2),
                    ft.Text("Actual Stats", size=16, weight=ft.FontWeight.W_600, color=COLORS["on_surface"]),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=6),
                ft.Row([
                    create_budget_stat_card("Net Cash Flow", cashflow_value, cashflow_subtitle, ft.Icons.SWAP_VERT, icon_container_ref=cashflow_icon_container),
                    create_budget_stat_card("Biggest Expense", biggest_value, biggest_subtitle, ft.Icons.STAR, color=COLORS["warning"]),
                    create_budget_stat_card("Savings Rate", savings_rate_value, savings_rate_subtitle, ft.Icons.TRENDING_UP, icon_container_ref=savings_rate_icon_container, progress_bar_ref=savings_rate_bar),
                ], spacing=14),
            ], spacing=4),
        )
        
        # Trigger initial calculation to populate all stat values
        update_metrics()
        _initializing = False
        
        # Editable data tables
        income_table = create_editable_data_table(
            "Income", ["Category", "Budget", "Actual"],
            data["income"], COLORS["success"],
            lambda cat, val: on_actual_change(cat, val, "Income"), 
            on_budget_change, page
        )
        
        expenses_table = create_editable_data_table(
            "Expenses", ["Category", "Budget", "Actual"],
            data["expenses"], COLORS["error"],
            lambda cat, val: on_actual_change(cat, val, "Expenses"), 
            on_budget_change, page
        )
        
        bills_table = create_editable_data_table(
            "Bills", ["Category", "Budget", "Actual"],
            data["bills"], COLORS["warning"],
            lambda cat, val: on_actual_change(cat, val, "Bills"), 
            on_budget_change, page
        )
        
        savings_table = create_editable_data_table(
            "Savings", ["Category", "Budget", "Actual"],
            data["savings"], COLORS["primary"],
            lambda cat, val: on_actual_change(cat, val, "Savings"), 
            on_budget_change, page
        )
        
        investments_table = create_editable_data_table(
            "Investments", ["Category", "Budget", "Actual"],
            data.get("investments", []), "#14b8a6",
            lambda cat, val: on_actual_change(cat, val, "Investments"), 
            on_budget_change, page
        )
        
        # Save button
        save_btn = ft.Container(
            content=ft.Button(
                "Save All Changes",
                icon=ft.Icons.SAVE,
                on_click=save_all_changes,
                bgcolor=COLORS["primary"],
                color="#ffffff",
            ),
            alignment=ft.Alignment(0, 0),
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("📊 Dashboard", size=28, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                create_week_nav(),
                ft.Container(height=10),
                metrics_row,
                ft.Container(height=16),
                budget_stats_section,
                ft.Container(height=12),
                actual_stats_section,
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
                ft.Container(height=10),
                ft.Row([
                    ft.Container(content=investments_table, expand=True),
                ], spacing=20),
                ft.Container(height=20),
                save_btn,
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
    investments_table = ft.Container()
    
    # ===== STATISTICS VIEW =====
    def create_statistics_view():
        # Generate charts
        income_expense_chart = cs.generate_income_vs_expenses_chart(
            stats_week_start.strftime("%Y-%m-%d"),
            stats_week_end.strftime("%Y-%m-%d")
        )
        spending_chart = cs.generate_spending_by_category_chart(
            stats_week_start.strftime("%Y-%m-%d"),
            stats_week_end.strftime("%Y-%m-%d")
        )
        trend_chart = cs.generate_monthly_trend_chart(4)
        budget_chart = cs.generate_budget_vs_actual_chart(
            stats_week_start.strftime("%Y-%m-%d"),
            stats_week_end.strftime("%Y-%m-%d")
        )
        
        # Get data for summary metrics
        data = ds.get_weekly_data(
            stats_week_start.strftime("%Y-%m-%d"),
            stats_week_end.strftime("%Y-%m-%d")
        )
        totals = data["totals"]
        
        # Calculate ratios
        savings_rate = (totals["savings"] / totals["income"] * 100) if totals["income"] > 0 else 0
        expense_ratio = (totals["expenses"] / totals["income"] * 100) if totals["income"] > 0 else 0
        investment_ratio = (totals["investments"] / totals["income"] * 100) if totals["income"] > 0 else 0
        
        def stat_card(label, value, icon, color, sub=""):
            """Create a stat metric card."""
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(icon, color="#ffffff", size=18),
                            bgcolor=color,
                            padding=8,
                            border_radius=8,
                        ),
                        ft.Text(label, size=12, color=COLORS["on_surface_variant"], weight=ft.FontWeight.W_500),
                    ], spacing=10),
                    ft.Container(height=6),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                    ft.Text(sub, size=11, color=COLORS["on_surface_variant"]) if sub else ft.Container(height=0),
                ], spacing=2),
                padding=16,
                bgcolor=COLORS["surface"],
                border_radius=12,
                expand=True,
            )
        
        def chart_card(title, chart_b64, sub="", accent=COLORS["primary"]):
            """Create a chart card."""
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(width=4, height=20, bgcolor=accent, border_radius=2),
                        ft.Column([
                            ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                            ft.Text(sub, size=11, color=COLORS["on_surface_variant"]) if sub else ft.Container(height=0),
                        ], spacing=2),
                    ], spacing=10),
                    ft.Container(height=10),
                    ft.Image(
                        src=f"data:image/png;base64,{chart_b64}",
                        fit="contain",
                        width=420,
                        height=220,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=18,
                bgcolor=COLORS["surface"],
                border_radius=14,
                expand=True,
            )
        
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.ANALYTICS, color="#ffffff", size=24),
                        bgcolor=COLORS["secondary"],
                        padding=12,
                        border_radius=12,
                    ),
                    ft.Column([
                        ft.Text("Statistics", size=26, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                        ft.Text("Analyze your financial performance", size=13, color=COLORS["on_surface_variant"]),
                    ], spacing=2),
                ], spacing=14),
                
                ft.Container(height=8),
                create_stats_week_nav(),
                ft.Container(height=16),
                
                # Metrics row 1
                ft.Row([
                    stat_card("Total Income", f"${totals['income']:,.0f}", 
                              ft.Icons.ACCOUNT_BALANCE_WALLET, COLORS["success"], "This week"),
                    stat_card("Total Spent", f"${totals['expenses']:,.0f}", 
                              ft.Icons.SHOPPING_CART, COLORS["error"],
                              f"{expense_ratio:.0f}% of income" if totals["income"] > 0 else "No income"),
                    stat_card("Net Savings", f"${totals['savings']:,.0f}", 
                              ft.Icons.SAVINGS, COLORS["primary"],
                              f"{savings_rate:.1f}% savings rate" if totals["income"] > 0 else "No income"),
                ], spacing=12),
                
                # Metrics row 2
                ft.Row([
                    stat_card("Investments", f"${totals['investments']:,.0f}", 
                              ft.Icons.TRENDING_UP, "#14b8a6",
                              f"{investment_ratio:.1f}% of income" if totals["income"] > 0 else "No income"),
                    stat_card("Balance", f"${totals['balance']:,.0f}", 
                              ft.Icons.ACCOUNT_BALANCE, 
                              COLORS["warning"] if totals["balance"] > 0 else COLORS["error"],
                              "Remaining funds"),
                ], spacing=12),
                
                ft.Container(height=20),
                
                # Section label
                ft.Row([
                    ft.Container(width=36, height=3, bgcolor=COLORS["primary"], border_radius=2),
                    ft.Text("Visual Analytics", size=13, weight=ft.FontWeight.W_600, color=COLORS["on_surface_variant"]),
                ], spacing=10),
                
                ft.Container(height=12),
                
                # Charts Row 1
                ft.Row([
                    chart_card("Income vs Expenses", income_expense_chart, "Weekly comparison", COLORS["success"]),
                    chart_card("Spending by Category", spending_chart, "Where your money goes", COLORS["error"]),
                ], spacing=16),
                
                ft.Container(height=16),
                
                # Charts Row 2
                ft.Row([
                    chart_card("Monthly Trend", trend_chart, "Last 4 months", COLORS["primary"]),
                    chart_card("Budget vs Actual", budget_chart, "Are you on track?", COLORS["warning"]),
                ], spacing=16),
                
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            padding=28,
            expand=True,
        )

    
    # Separate Budget Navigation
    def create_budget_week_nav():
        """Factory specifically for Budget view independent navigation."""
        
        # Local calendar container for budget
        budget_calendar_container = ft.Container(
            visible=False,
            bgcolor=COLORS["surface"],
            padding=15,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, color="#80000000"),
            width=300,
            alignment=ft.Alignment(0, 0)
        )
        
        current_budget_cal_date = datetime.now()

        def update_budget_calendar_ui():
            budget_calendar_container.content = create_budget_calendar_renderer(
                current_budget_cal_date.year, 
                current_budget_cal_date.month
            )
            if budget_calendar_container.visible:
                budget_calendar_container.update()

        def create_budget_calendar_renderer(year, month):
            import calendar
            cal = calendar.Calendar(firstweekday=0)
            month_days = list(cal.itermonthdays2(year, month))
            
            def prev_month(e):
                nonlocal current_budget_cal_date
                if current_budget_cal_date.month == 1:
                    current_budget_cal_date = datetime(current_budget_cal_date.year - 1, 12, 1)
                else:
                    current_budget_cal_date = datetime(current_budget_cal_date.year, current_budget_cal_date.month - 1, 1)
                update_budget_calendar_ui()

            def next_month(e):
                nonlocal current_budget_cal_date
                if current_budget_cal_date.month == 12:
                    current_budget_cal_date = datetime(current_budget_cal_date.year + 1, 1, 1)
                else:
                    current_budget_cal_date = datetime(current_budget_cal_date.year, current_budget_cal_date.month + 1, 1)
                update_budget_calendar_ui()
            
            header = ft.Row([
                ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=prev_month, icon_color=COLORS["on_surface"]),
                ft.Text(f"{calendar.month_name[month]} {year}", weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=next_month, icon_color=COLORS["on_surface"]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            
            days_header = ft.Row([
                ft.Container(content=ft.Text(day, size=12, color=COLORS["on_surface_variant"], text_align=ft.TextAlign.CENTER), width=35, alignment=ft.Alignment(0, 0))
                for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            ], spacing=2)
            
            calendar_rows = [header, days_header]
            
            week_days = []
            for day, weekday in month_days:
                if day == 0:
                    day_content = ft.Container(width=35, height=35)
                else:
                    is_today = (datetime.now().year == year and datetime.now().month == month and datetime.now().day == day)
                    day_content = ft.Container(
                        content=ft.Text(str(day), size=12, 
                                      color=COLORS["background"] if is_today else COLORS["on_surface"]),
                        width=35, height=35,
                        bgcolor=COLORS["primary"] if is_today else None,
                        border_radius=50,
                        alignment=ft.Alignment(0, 0)
                    )
                week_days.append(day_content)
                
                if len(week_days) == 7:
                    valid_date = None
                    for d, wd in month_days[month_days.index((day, weekday))-6 : month_days.index((day, weekday))+1]:
                            if d != 0:
                                valid_date = datetime(year, month, d)
                                break
                    if valid_date:
                        week_row = ft.Container(
                            content=ft.Row(week_days, spacing=2),
                            padding=2,
                            border_radius=5,
                            on_hover=lambda e: highlight_week_row(e), 
                            on_click=lambda e, d=valid_date: select_budget_week(d),
                            ink=True,
                        )
                        calendar_rows.append(week_row)
                    else:
                        calendar_rows.append(ft.Row(week_days, spacing=2))
                    week_days = []
            
            return ft.Column(calendar_rows, spacing=5)

        def toggle_budget_calendar(e):
            budget_calendar_container.visible = not budget_calendar_container.visible
            if budget_calendar_container.visible:
                update_budget_calendar_ui()
            page.update()

        def nav_budget_week(delta):
            navigate_budget_week(delta)

        def go_to_budget_today():
            navigate_budget_today()

        # Create fresh budget week label
        budget_week_label = ft.Text(
            f"{budget_week_start.strftime('%b %d')} - {budget_week_end.strftime('%b %d, %Y')}",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=COLORS["on_surface"],
        )
        
        nav_row = ft.Row([
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=lambda _: nav_budget_week(-1),
                icon_color=COLORS["on_surface"],
                tooltip="Previous week",
            ),
            ft.Container(
                content=ft.Row([
                    budget_week_label,
                    ft.Icon(ft.Icons.CALENDAR_MONTH, size=18, color=COLORS["primary"]),
                ], spacing=8),
                bgcolor=COLORS["surface"],
                padding=ft.Padding(left=20, top=10, right=20, bottom=10),
                border_radius=8,
                on_click=toggle_budget_calendar,
                ink=True,
                tooltip="Click to open calendar",
            ),
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                on_click=lambda _: nav_budget_week(1),
                icon_color=COLORS["on_surface"],
                tooltip="Next week",
            ),
            ft.IconButton(
                icon=ft.Icons.TODAY,
                tooltip="Go to current week",
                on_click=lambda _: go_to_budget_today(),
                icon_color=COLORS["primary"],
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)

        return ft.Column([
            nav_row,
            ft.Row([budget_calendar_container], alignment=ft.MainAxisAlignment.CENTER)
        ])

    def navigate_budget_week(delta: int):
        nonlocal budget_week_start, budget_week_end
        budget_week_start += timedelta(days=7 * delta)
        budget_week_end += timedelta(days=7 * delta)
        refresh_current_view()

    def navigate_budget_today():
        nonlocal budget_week_start, budget_week_end
        budget_week_start, budget_week_end = ds.get_week_dates(datetime.now())
        refresh_current_view()
        
    def select_budget_week(date_in_week):
        nonlocal budget_week_start, budget_week_end
        budget_week_start, budget_week_end = ds.get_week_dates(date_in_week)
        refresh_current_view()
    
    
    # Manager navigation helper functions - use shared week_start/end
    def navigate_manager_week(delta: int):
        nonlocal week_start, week_end
        week_start += timedelta(days=7 * delta)
        week_end += timedelta(days=7 * delta)
        refresh_current_view()

    def navigate_manager_today():
        nonlocal week_start, week_end
        week_start, week_end = ds.get_week_dates(datetime.now())
        refresh_current_view()
        
    def select_manager_week(date_in_week):
        nonlocal week_start, week_end
        week_start, week_end = ds.get_week_dates(date_in_week)
        refresh_current_view()
    
    # ===== BUDGET CONFIG VIEW =====
    def create_budget_view():
        # Load defaults
        budget_df = ds.load_budget_config()
        # Load overrides for selected week (returns DataFrame)
        weekly_budgets_df = ds.load_weekly_budgets()
        week_key = budget_week_start.strftime("%Y-%m-%d")
        
        budget_fields = {}
        
        def save_budget(e):
            # Update budget values
            for idx, row in budget_df.iterrows():
                cat = row["Category"]
                if cat in budget_fields:
                    try:
                        val = float(budget_fields[cat].value or 0)
                        ds.set_weekly_budget_override(week_key, cat, val)
                    except ValueError:
                        pass
            
            # Show success message
            snack = ft.SnackBar(
                content=ft.Text(f"✅ Weekly budget saved for {week_key}!"),
                bgcolor=COLORS["success"],
                duration=3000
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
        
        def create_budget_section(title: str, cat_type: str, color: str):
            cats = budget_df[budget_df["Type"] == cat_type]
            fields = []
            for _, row in cats.iterrows():
                cat = row["Category"]
                # Determine value to show: Override > Default
                val = row["Budget"] # Default monthly
                
                # Check for override in the DataFrame
                override_row = weekly_budgets_df[
                    (weekly_budgets_df["WeekStart"] == week_key) & 
                    (weekly_budgets_df["Category"] == cat)
                ]
                has_override = not override_row.empty
                if has_override:
                    val = override_row.iloc[0]["Amount"]
                
                field = ft.TextField(
                    value=str(int(val)),
                    label=f"{cat} (w)" if has_override else cat,
                    width=150,
                    text_size=14,
                    bgcolor=COLORS["surface_variant"],
                    border_color=color,
                )
                budget_fields[cat] = field
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
                create_budget_week_nav(),
                ft.Text("Set your budget for this specific week. (w) indicates a weekly override.", color=COLORS["on_surface_variant"]),
                ft.Container(height=10),
                create_budget_section("Income", "Income", COLORS["success"]),
                create_budget_section("Expenses", "Expenses", COLORS["error"]),
                create_budget_section("Bills", "Bills", COLORS["warning"]),
                create_budget_section("Savings", "Savings", COLORS["primary"]),
                create_budget_section("Investments", "Investments", "#14b8a6"),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Save Weekly Budget",
                    icon=ft.Icons.SAVE,
                    on_click=save_budget,
                    bgcolor=COLORS["primary"],
                    color="#ffffff",
                ),
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True,
        )
    
    
    # Separate Manager Navigation
    def create_manager_week_nav():
        """Factory specifically for Manager view independent navigation."""
        
        # Local state for calendar UI
        current_cal_date = datetime.now()
        
        manager_calendar_container = ft.Container(
            content=None,
            visible=False,
        )
        
        def on_manager_week_select(date_in_week):
            select_manager_week(date_in_week)
            manager_calendar_container.visible = False
            page.update()

        def update_manager_calendar_ui():
            manager_calendar_container.content = create_custom_calendar(current_cal_date.year, current_cal_date.month, update_manager_calendar_ui)
            if manager_calendar_container.visible:
                manager_calendar_container.update()

        def toggle_manager_calendar(e):
            manager_calendar_container.visible = not manager_calendar_container.visible
            if manager_calendar_container.visible:
                update_manager_calendar_ui()
            page.update()

        # Create fresh week label using shared week state
        manager_week_label = ft.Text(
            f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=COLORS["on_surface"],
        )
        
        nav_row = ft.Row([
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=lambda _: navigate_manager_week(-1),
                icon_color=COLORS["on_surface"],
                tooltip="Previous week",
            ),
            ft.Container(
                content=ft.Row([
                    manager_week_label,
                    ft.Icon(ft.Icons.CALENDAR_MONTH, size=18, color=COLORS["primary"]),
                ], spacing=8),
                bgcolor=COLORS["surface"],
                padding=ft.Padding(left=20, top=10, right=20, bottom=10),
                border_radius=8,
                on_click=toggle_manager_calendar,
                ink=True,
                tooltip="Click to open calendar",
            ),
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                on_click=lambda _: navigate_manager_week(1),
                icon_color=COLORS["on_surface"],
                tooltip="Next week",
            ),
            ft.IconButton(
                icon=ft.Icons.TODAY,
                tooltip="Go to current week",
                on_click=lambda _: navigate_manager_today(),
                icon_color=COLORS["primary"],
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)

        return ft.Column([
            nav_row,
            ft.Row([manager_calendar_container], alignment=ft.MainAxisAlignment.CENTER)
        ])

    # ===== MANAGER VIEW =====
    def create_manager_view():
        transactions_df = ds.load_transactions()
        budget_df = ds.load_budget_config()
        categories = budget_df["Category"].tolist()
        types = budget_df["Type"].unique().tolist()
        
        # Form fields
        type_dropdown = ft.Dropdown(
            label="Type",
            options=[ft.dropdown.Option(t) for t in types],
            width=150,
            bgcolor=COLORS["surface_variant"],
        )
        
        category_field = ft.TextField(
            label="Category",
            width=200,
            bgcolor=COLORS["surface_variant"],
            hint_text="e.g., Rent, Groceries, Salary",
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
        
        # Year and Month pickers for monthly recurrence
        from datetime import date as _date
        _current_year = _date.today().year
        
        year_dropdown = ft.Dropdown(
            label="Year",
            options=[ft.dropdown.Option(key=str(y), text=str(y)) for y in range(_current_year, 2071)],
            width=110,
            bgcolor=COLORS["surface_variant"],
        )
        
        month_dropdown = ft.Dropdown(
            label="Month",
            options=[
                ft.dropdown.Option(key="01", text="January"),
                ft.dropdown.Option(key="02", text="February"),
                ft.dropdown.Option(key="03", text="March"),
                ft.dropdown.Option(key="04", text="April"),
                ft.dropdown.Option(key="05", text="May"),
                ft.dropdown.Option(key="06", text="June"),
                ft.dropdown.Option(key="07", text="July"),
                ft.dropdown.Option(key="08", text="August"),
                ft.dropdown.Option(key="09", text="September"),
                ft.dropdown.Option(key="10", text="October"),
                ft.dropdown.Option(key="11", text="November"),
                ft.dropdown.Option(key="12", text="December"),
            ],
            width=140,
            bgcolor=COLORS["surface_variant"],
        )
        
        # Recurrence dropdown
        recurrence_dropdown = ft.Dropdown(
            label="Recurrence",
            options=[
                ft.dropdown.Option(key="one-time", text="One-time"),
                ft.dropdown.Option(key="permanent", text="Weekly (Permanent)"),
                ft.dropdown.Option(key="monthly", text="Monthly"),
            ],
            value="one-time",
            width=180,
            bgcolor=COLORS["surface_variant"],
        )
        
        trans_list = ft.Ref[ft.Column]()
        recurring_list = ft.Ref[ft.Column]()
        
        def refresh_transactions():
            nonlocal transactions_df
            transactions_df = ds.load_transactions()
            if trans_list.current:
                trans_list.current.controls = build_transaction_rows()
                page.update()
        
        def refresh_recurring():
            if recurring_list.current:
                recurring_list.current.controls = build_recurring_rows()
                page.update()
        
        def add_transaction(e):
            if not type_dropdown.value or not category_field.value or not amount_field.value:
                snack = ft.SnackBar(
                    content=ft.Text("Please fill in Type, Category, and Amount"), 
                    bgcolor=COLORS["error"],
                    duration=3000
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
                return
            
            try:
                amount = float(amount_field.value)
            except ValueError:
                snack = ft.SnackBar(
                    content=ft.Text("Amount must be a number"),
                    bgcolor=COLORS["error"],
                    duration=3000
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
                return
            
            recurrence = recurrence_dropdown.value or "one-time"
            
            if recurrence == "one-time":
                ds.add_transaction(
                    week_start.strftime("%Y-%m-%d"),
                    category_field.value.strip(),
                    type_dropdown.value,
                    amount,
                    note_field.value or ""
                )
                msg = "✅ Transaction added!"
            elif recurrence == "monthly":
                if not year_dropdown.value or not month_dropdown.value:
                    snack = ft.SnackBar(
                        content=ft.Text("Please select a year and month"),
                        bgcolor=COLORS["error"],
                        duration=3000
                    )
                    page.overlay.append(snack)
                    snack.open = True
                    page.update()
                    return
                target_month = f"{year_dropdown.value}-{month_dropdown.value}"
                ds.add_recurring_transaction(
                    category_field.value.strip(),
                    type_dropdown.value,
                    amount,
                    recurrence,
                    note_field.value or "",
                    target_month=target_month
                )
                msg = f"🔄 Monthly transaction added for {target_month}!"
            else:
                ds.add_recurring_transaction(
                    category_field.value.strip(),
                    type_dropdown.value,
                    amount,
                    recurrence,
                    note_field.value or ""
                )
                msg = "🔄 Weekly (Permanent) recurring transaction added!"
            
            # Clear form
            category_field.value = ""
            amount_field.value = ""
            note_field.value = ""
            recurrence_dropdown.value = "one-time"
            year_dropdown.value = None
            month_dropdown.value = None
            
            refresh_transactions()
            refresh_recurring()
            
            snack = ft.SnackBar(
                content=ft.Text(msg),
                bgcolor=COLORS["success"],
                duration=3000
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
        
        def delete_transaction(trans_id):
            ds.delete_transaction(trans_id)
            refresh_transactions()
            snack = ft.SnackBar(
                content=ft.Text("🗑️ Transaction deleted!"),
                bgcolor=COLORS["error"],
                duration=3000
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
        
        def delete_recurring(rec_id):
            ds.delete_recurring_transaction(rec_id)
            refresh_recurring()
            refresh_transactions()  # Refresh to remove injected entries
            snack = ft.SnackBar(
                content=ft.Text("🗑️ Recurring transaction deleted!"),
                bgcolor=COLORS["error"],
                duration=3000
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
        
        def build_transaction_rows():
            import pandas as pd
            rows = []
            # Filter transactions by shared week state
            if len(transactions_df) > 0 and "Date" in transactions_df.columns:
                df_copy = transactions_df.copy()
                df_copy["Date"] = pd.to_datetime(df_copy["Date"], errors="coerce")
                start = pd.to_datetime(week_start.strftime("%Y-%m-%d"))
                end = pd.to_datetime(week_end.strftime("%Y-%m-%d"))
                week_trans = df_copy[(df_copy["Date"] >= start) & (df_copy["Date"] <= end)]
                sorted_df = week_trans.sort_values("Date", ascending=False)
            else:
                sorted_df = pd.DataFrame()
            
            # Also include recurring transactions for this week
            recurring = ds.load_recurring_transactions()
            recurring_cats = set()
            if len(recurring) > 0:
                for _, rec in recurring.iterrows():
                    created = pd.to_datetime(rec.get("CreatedDate", "2000-01-01"), errors="coerce")
                    if created > pd.to_datetime(week_end.strftime("%Y-%m-%d")):
                        continue
                    # Check if manual entry exists for this category
                    has_manual = False
                    if len(sorted_df) > 0:
                        has_manual = len(sorted_df[
                            (sorted_df["Category"] == rec["Category"]) & 
                            (sorted_df["Type"] == rec["Type"])
                        ]) > 0
                    if not has_manual:
                        rec_label = "🔄 Weekly" if rec["Recurrence"] == "permanent" else "🔄 Monthly"
                        type_color = COLORS["success"] if rec["Type"] == "Income" else "#14b8a6" if rec["Type"] == "Investments" else COLORS["error"]
                        rows.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Container(
                                        content=ft.Text(rec_label, size=9, color="#ffffff", weight=ft.FontWeight.W_600),
                                        bgcolor="#6366f1",
                                        padding=ft.Padding(6, 2, 6, 2),
                                        border_radius=8,
                                        width=100,
                                    ),
                                    ft.Text(str(rec.get("Category", "")), color=COLORS["on_surface"], width=150),
                                    ft.Text(f"${rec.get('Amount', 0):.2f}", color=type_color, width=80),
                                    ft.Text(str(rec.get("Type", "")), color=COLORS["on_surface_variant"], expand=True),
                                ], spacing=10),
                                padding=10,
                                bgcolor=f"{COLORS['surface']}",
                                border_radius=8,
                                border=ft.Border.all(1, "#6366f140"),
                            )
                        )
                        recurring_cats.add((rec["Category"], rec["Type"]))
            
            for _, row in sorted_df.iterrows():
                type_color = COLORS["success"] if row.get("Type") == "Income" else "#14b8a6" if row.get("Type") == "Investments" else COLORS["error"]
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
            return rows if rows else [ft.Text("No transactions for this week", color=COLORS["on_surface_variant"])]
        
        def build_recurring_rows():
            """Build list of all recurring transactions with delete buttons."""
            recurring = ds.load_recurring_transactions()
            rows = []
            
            if len(recurring) == 0:
                return [ft.Text("No recurring transactions set up", color=COLORS["on_surface_variant"], size=13)]
            
            for _, rec in recurring.iterrows():
                rec_type = rec.get("Recurrence", "permanent")
                badge_color = "#6366f1" if rec_type == "permanent" else "#ec4899"
                badge_text = "Weekly" if rec_type == "permanent" else "Monthly"
                type_color = COLORS["success"] if rec.get("Type") == "Income" else "#14b8a6" if rec.get("Type") == "Investments" else COLORS["error"]
                
                rows.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text(badge_text, size=10, color="#ffffff", weight=ft.FontWeight.W_600),
                                bgcolor=badge_color,
                                padding=ft.Padding(8, 3, 8, 3),
                                border_radius=10,
                            ),
                            ft.Text(str(rec.get("Category", "")), color=COLORS["on_surface"], width=140, weight=ft.FontWeight.W_500),
                            ft.Text(str(rec.get("Type", "")), color=COLORS["on_surface_variant"], width=100, size=12),
                            ft.Text(f"${rec.get('Amount', 0):.2f}", color=type_color, width=90, weight=ft.FontWeight.BOLD),
                            ft.Text(str(rec.get("Note", ""))[:15], color=COLORS["on_surface_variant"], expand=True, size=11),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_FOREVER,
                                icon_color=COLORS["error"],
                                tooltip="Delete recurring transaction",
                                on_click=lambda e, rid=rec.get("id"): delete_recurring(rid),
                            ),
                        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.Padding(14, 8, 8, 8),
                        bgcolor=COLORS["surface"],
                        border_radius=10,
                        border=ft.Border.all(1, f"{badge_color}30"),
                    )
                )
            return rows
        
        return ft.Container(
            content=ft.Column([
                ft.Text("📝 Transaction Manager", size=28, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                create_manager_week_nav(),
                ft.Container(height=10),
                # Add transaction form
                ft.Container(
                    content=ft.Column([
                        ft.Text("Add Transaction", weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                        ft.Row([type_dropdown, category_field, amount_field], spacing=10, wrap=True),
                        ft.Row([recurrence_dropdown, year_dropdown, month_dropdown, note_field], spacing=10, wrap=True),
                        ft.Button(
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
                # Recurring Transactions Section
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(width=4, height=20, bgcolor="#6366f1", border_radius=2),
                            ft.Text("Recurring Transactions", size=16, weight=ft.FontWeight.W_600, color=COLORS["on_surface"]),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text("Auto-applied each period", size=10, color=COLORS["on_surface_variant"]),
                            ),
                        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Container(height=6),
                        ft.Column(build_recurring_rows(), ref=recurring_list, spacing=6),
                    ], spacing=4),
                    padding=20,
                    bgcolor=f"{COLORS['surface']}80",
                    border_radius=12,
                ),
                ft.Container(height=20),
                ft.Text("Transactions for Selected Week", weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                ft.Column(build_transaction_rows(), ref=trans_list, spacing=5),
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True,
        )
    
    # ===== HISTORY VIEW =====
    def create_history_view():
        # Get weeks that have data + current week
        weeks = []
        history_weeks = ds.get_history_weeks()
        
        for start, end in history_weeks:
            # Format dates for API
            start_str = start.strftime("%Y-%m-%d")
            end_str = end.strftime("%Y-%m-%d")
            
            data = ds.get_weekly_data(start_str, end_str)
            weeks.append({
                "start": start,
                "end": end,
                "totals": data["totals"],
                "has_data": len(data["transactions"]) > 0
            })
        
        def view_week_details(start_date):
            nonlocal week_start, week_end, current_view_index
            week_start, week_end = ds.get_week_dates(start_date)
            
            # Switch to Dashboard (index 0)
            current_view_index = 0
            nav_rail.selected_index = 0
            refresh_current_view()
            page.update()
            
        def delete_week_data(start, end):
            start_str = start.strftime("%Y-%m-%d")
            end_str = end.strftime("%Y-%m-%d")
            
            if ds.delete_week_transactions(start_str, end_str):
                # Refresh history
                refresh_current_view()
                snack = ft.SnackBar(
                    content=ft.Text(f"🗑️ Deleted data for {start.strftime('%b %d')} - {end.strftime('%b %d')}"),
                    bgcolor=COLORS["success"],
                    duration=3000
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
            else:
                snack = ft.SnackBar(
                    content=ft.Text("No data to delete"),
                    bgcolor=COLORS["warning"],
                    duration=3000
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
        
        def create_week_card(week_data):
            totals = week_data["totals"]
            balance = totals['income'] - totals['expenses']
            balance_color = COLORS["success"] if balance >= 0 else COLORS["error"]
            has_data = week_data["has_data"]
            
            return ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_TODAY, color=COLORS["primary"], size=24),
                            ft.Column([
                                ft.Text(
                                    f"{week_data['start'].strftime('%b %d')} - {week_data['end'].strftime('%b %d, %Y')}",
                                    weight=ft.FontWeight.BOLD,
                                    color=COLORS["on_surface"],
                                    size=16
                                ),
                                ft.Row([
                                    ft.Text(f"Income: ${totals['income']:.0f}", color=COLORS["success"], size=12),
                                    ft.Text(f"Expenses: ${totals['expenses']:.0f}", color=COLORS["error"], size=12),
                                ], spacing=10)
                            ], expand=True),
                            ft.Column([
                                ft.Text(f"Balance", color=COLORS["on_surface_variant"], size=10),
                                ft.Text(f"${balance:.0f}", color=balance_color, size=18, weight=ft.FontWeight.BOLD),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END, width=100),
                        ], spacing=15),
                        expand=True,
                    ),
                    # View button - navigate to Dashboard for this week
                    ft.Button(
                        "View",
                        icon=ft.Icons.VISIBILITY,
                        bgcolor=COLORS["primary"],
                        color="#ffffff",
                        on_click=lambda _, s=week_data['start']: view_week_details(s),
                    ),
                    # Delete button
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=COLORS["error"] if has_data else COLORS["surface_variant"],
                        tooltip="Delete week data",
                        on_click=lambda _, s=week_data['start'], e=week_data['end']: delete_week_data(s, e)
                    )
                ], spacing=10),
                padding=20,
                bgcolor=COLORS["surface"],
                border_radius=12,
                margin=ft.margin.only(bottom=5),
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("📅 History", size=28, weight=ft.FontWeight.BOLD, color=COLORS["on_surface"]),
                ft.Text("View or manage your past weeks. Click a week to view details.", color=COLORS["on_surface_variant"]),
                ft.Container(height=10),
                *[create_week_card(w) for w in weeks],
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            padding=30,
            expand=True,
        )
    
    # ===== NAVIGATION =====
    def on_nav_change(e):
        """Handle navigation rail selection changes."""
        nonlocal current_view_index
        index = e.control.selected_index
        current_view_index = index
        refresh_current_view()
    
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
            ft.Button("Save", on_click=save_profile, bgcolor=COLORS["primary"], color="#ffffff"),
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
    ft.run(main)
