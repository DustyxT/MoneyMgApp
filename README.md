# 💰 Manage Ur Wealth - Student Money Manager

A modern, premium desktop application for international students to manage their finances effectively.

## ✨ Features

- **📊 Dashboard** - Weekly overview of income, expenses, savings, bills, and investments with live-editable values and real-time budget stats
- **📈 Statistics** - Premium charts and visual analytics (income vs expenses, spending breakdown, monthly trend, budget vs actual) with independent week navigation
- **💵 Budget** - Set weekly budget goals per category with per-week overrides; indicators show which categories have been overridden
- **📝 Manager** - Add one-time, permanent weekly, or monthly recurring transactions; view and delete transactions for any selected week
- **📜 History** - Browse all weeks that have data, jump directly to any week in the Dashboard, or delete a week's data
- **👤 Profile** - Personalize your experience with a custom display name

## 🚀 Quick Start

### Run from source
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the application:**
   ```bash
   python app.py
   ```

### Run as installer
1. Build the executable:
   ```bash
   python build_flet.py
   ```
2. Compile `setup.iss` with [Inno Setup](https://jrsoftware.org/isinfo.php) to produce `setup_build/ManageUrWealth_Setup_1.0.1.exe`
3. Run the installer — no Python required on the target machine

## 📁 Project Structure

```
Money management app/
├── app.py                      # Main application (UI & all views)
├── data_service.py             # Data access layer (CSV + JSON)
├── chart_service.py            # Matplotlib chart generation
├── build_flet.py               # PyInstaller build script
├── setup.iss                   # Inno Setup installer script
├── requirements.txt            # Python dependencies
├── ManageUrWealth.spec         # PyInstaller spec file
├── .gitignore
├── budget_config.csv           # Budget categories (auto-generated)
├── transactions.csv            # Transaction history (auto-generated)
├── weekly_budgets.csv          # Per-week budget overrides (auto-generated)
├── recurring_transactions.csv  # Recurring transaction rules (auto-generated)
└── profile.json                # User profile (auto-generated)
```

## 🛠️ Technology Stack

- **Python 3** - Core language
- **Flet** - Cross-platform desktop UI framework (Flutter for Python)
- **Pandas** - Data manipulation and CSV persistence
- **Matplotlib** - Chart generation (rendered as embedded PNG)
- **PyInstaller / Flet Pack** - Single-file EXE packaging
- **Inno Setup** - Windows installer

## 📋 Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies

## 🎨 Design

Modern dark-themed UI with:
- Premium stat cards with live progress bars
- Real-time field updates (no page reload on edits)
- Editable budget & actual values per category
- Independent week navigation per view (Dashboard, Statistics, Budget, Manager)
- Color-coded categories (income = green, expenses = red, savings = blue, investments = teal)
- Embedded Matplotlib charts with dark background styling

## 📝 Changelog

### Version 3.0 (2026-03-04)
- **Fix:** Double CSV read/write in `update_actual_value` — now uses a single load + save
- **Fix:** Wrong month boundaries in monthly trend chart (was using `timedelta(days=30)` approximation; now uses proper calendar arithmetic)
- **Fix:** Dead stub `create_dashboard_view` was silently shadowing the real implementation
- **Fix:** Duplicate `on_nav_change` definition removed
- **Cleanup:** Removed never-called `create_calendar_picker` and `_highlight_week` top-level functions
- **Cleanup:** Removed unused `week_label`, `content_container`, and `update_budget_value`
- **Cleanup:** Removed unused `Optional` import in `data_service.py`
- **Performance:** Moved repeated in-function imports (`calendar`, `pandas`, `datetime`) to module top level
- **Installer:** Bumped version to `1.0.1`, added `AppPublisher`, versioned output filename, `CloseApplications=yes`

### Version 2.0
- Complete rewrite as native Flet desktop application
- Added Statistics view with 4 chart types
- Added recurring transactions (permanent & monthly)
- Added Investments category
- Added per-week budget overrides
- Added History view with week navigation

### Version 1.0
- Initial Streamlit web UI with basic income/expense tracking

---

**Version:** 3.0 (installer: 1.0.1)
**Author:** Dusty
