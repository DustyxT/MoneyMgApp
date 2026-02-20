# 💰 Manage Ur Wealth - Student Money Manager

A modern, premium desktop application for international students to manage their finances effectively.

## ✨ Features

- **📊 Dashboard** - Weekly overview of income, expenses, savings, and bills with editable values
- **📈 Statistics** - Premium charts and visual analytics of your financial performance  
- **💵 Budget** - Set weekly budget goals with category-specific limits
- **📝 Manager** - Add and manage individual transactions
- **📜 History** - View and manage past weeks' financial data
- **👤 Profile** - Personalize your experience with custom profile picture

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

## 📁 Project Structure

```
Money management app/
├── app.py              # Main application (UI)
├── data_service.py     # Data access layer
├── chart_service.py    # Chart generation
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
├── budget_config.csv   # Budget categories (auto-generated)
├── transactions.csv    # Transaction data (auto-generated)
├── weekly_budgets.csv  # Weekly budget overrides (auto-generated)
└── profile.json        # User profile data (auto-generated)
```

## 🛠️ Technology Stack

- **Python 3** - Core language
- **Flet** - Cross-platform UI framework (Flutter for Python)
- **Pandas** - Data manipulation
- **Matplotlib** - Chart generation

## 📋 Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies

## 🎨 Design

Modern, dark-themed UI with:
- Premium gradient cards
- Smooth animations
- Responsive layout
- Color-coded categories

---

**Version:** 1.0.0  
**Author:** Dusty
