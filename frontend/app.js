/**
 * Student Finance Commander - Frontend Application
 * Professional Finance Dashboard
 */

// API Base URL
const API_BASE = 'http://localhost:8000/api';

// State
let currentWeekStart = null;
let weeklyData = [];
let charts = {};
let budgetItems = [];

// Manager Tab Filter State
let managerFilterStart = null;
let managerFilterEnd = null;

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', async () => {
    initNavigation();
    initWeekNavigation();
    initDateInputs();
    initSaveButtons();
    initViewToggle();
    initBudgetDateInputs();
    initTransactionFilters();
    initTransactionModal();
    initExportButton();
    initCalendarPickers();

    // Load initial data
    await loadCurrentWeek();
    await loadDashboardData();
});

// ========================================
// CALENDAR PICKERS (Flatpickr)
// ========================================
function initCalendarPickers() {
    console.log("📅 initCalendarPickers() started");

    const baseConfig = {
        dateFormat: "Y-m-d",
        theme: "dark",
        disableMobile: true,
        animate: true,
        allowInput: true,
        showMonths: 1,
        // Show week numbers in calendar
        weekNumbers: true,
        // Highlight week on hover
        onDayCreate: function (dObj, dStr, fp, dayElem) {
            // Add week highlight on hover
            dayElem.addEventListener('mouseenter', function () {
                const weekDays = dayElem.closest('.flatpickr-days').querySelectorAll('.flatpickr-day');
                const dayIndex = Array.from(weekDays).indexOf(dayElem);
                const weekStart = Math.floor(dayIndex / 7) * 7;

                for (let i = weekStart; i < weekStart + 7 && i < weekDays.length; i++) {
                    weekDays[i].classList.add('week-hover');
                }
            });
            dayElem.addEventListener('mouseleave', function () {
                const weekDays = dayElem.closest('.flatpickr-days').querySelectorAll('.flatpickr-day');
                weekDays.forEach(d => d.classList.remove('week-hover'));
            });
        }
    };

    // Week highlighting function for reuse
    const weekHighlightConfig = {
        onDayCreate: function (dObj, dStr, fp, dayElem) {
            dayElem.addEventListener('mouseenter', function () {
                const container = dayElem.closest('.dayContainer');
                if (!container) return;

                const allDays = Array.from(container.querySelectorAll('.flatpickr-day'));
                const dayIndex = allDays.indexOf(dayElem);
                const weekStart = Math.floor(dayIndex / 7) * 7;
                const weekEnd = weekStart + 7;

                for (let i = weekStart; i < weekEnd && i < allDays.length; i++) {
                    allDays[i].classList.add('week-hover');
                }
            });
            dayElem.addEventListener('mouseleave', function () {
                const container = dayElem.closest('.dayContainer');
                if (!container) return;

                const allDays = container.querySelectorAll('.flatpickr-day');
                allDays.forEach(d => d.classList.remove('week-hover'));
            });
        }
    };

    // Helper function to format date
    const fmtDate = (d) => {
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    // Statistics page - Weekly picker with auto end date
    try {
        const statsWeekEl = document.getElementById('stats-week-start');
        if (statsWeekEl) {
            flatpickr(statsWeekEl, {
                dateFormat: "Y-m-d",
                theme: "dark",
                disableMobile: true,
                animate: true,
                weekNumbers: true,
                locale: { firstDayOfWeek: 1 },
                ...weekHighlightConfig,
                onChange: function (selectedDates, dateStr, instance) {
                    if (selectedDates.length > 0) {
                        const clickedDate = new Date(selectedDates[0]);

                        // Get Monday of selected week
                        const dayOfWeek = clickedDate.getDay();
                        const monday = new Date(clickedDate);

                        if (dayOfWeek === 0) {
                            monday.setDate(clickedDate.getDate() - 6);
                        } else {
                            monday.setDate(clickedDate.getDate() - (dayOfWeek - 1));
                        }

                        // Calculate Sunday
                        const sunday = new Date(monday);
                        sunday.setDate(monday.getDate() + 6);

                        // Update display
                        instance.setDate(monday, false);
                        document.getElementById('stats-week-end').textContent = fmtDate(sunday);

                        // Store dates and load data
                        window.statsStartDate = fmtDate(monday);
                        window.statsEndDate = fmtDate(sunday);
                        loadStatisticsData();

                        instance.close();
                    }
                }
            });
            console.log("✓ Stats week picker initialized");
        }
    } catch (e) {
        console.error("× Error initializing stats week picker:", e);
    }

    // Statistics page - Monthly picker (year and month only)
    // Use try-catch to prevent breaking other calendar pickers if plugin isn't available
    try {
        const monthPlugin = window.flatpickr?.monthSelectPlugin || window.monthSelectPlugin;
        if (monthPlugin) {
            flatpickr("#stats-month", {
                dateFormat: "Y-m",
                theme: "dark",
                disableMobile: true,
                animate: true,
                plugins: [new monthPlugin({
                    shorthand: true,
                    dateFormat: "Y-m",
                    altFormat: "F Y"
                })],
                onChange: function (selectedDates, dateStr, instance) {
                    if (selectedDates.length > 0) {
                        const selectedMonth = selectedDates[0];
                        const year = selectedMonth.getFullYear();
                        const month = selectedMonth.getMonth();

                        // First day of month
                        const firstDay = new Date(year, month, 1);
                        // Last day of month
                        const lastDay = new Date(year, month + 1, 0);

                        // Store dates and load data
                        window.statsStartDate = fmtDate(firstDay);
                        window.statsEndDate = fmtDate(lastDay);
                        loadStatisticsData();

                        instance.close();
                    }
                }
            });
        } else {
            console.warn("monthSelectPlugin not available, skipping month picker initialization");
        }
    } catch (e) {
        console.error("Error initializing month picker:", e);
    }

    // Budget config - Week picker with auto end date and week highlighting
    try {
        const budgetStartEl = document.getElementById('budget-start-date');
        if (budgetStartEl) {
            flatpickr(budgetStartEl, {
                dateFormat: "Y-m-d",
                theme: "dark",
                disableMobile: true,
                animate: true,
                weekNumbers: true,
                locale: { firstDayOfWeek: 1 }, // Start week on Monday
                // Highlight entire week row on hover
                onDayCreate: function (dObj, dStr, fp, dayElem) {
                    dayElem.addEventListener('mouseenter', function () {
                        // Get the container with all days
                        const container = dayElem.closest('.dayContainer');
                        if (!container) return;

                        const allDays = Array.from(container.querySelectorAll('.flatpickr-day'));
                        const dayIndex = allDays.indexOf(dayElem);

                        // Calculate the start of the week row (7 days per row)
                        const weekStart = Math.floor(dayIndex / 7) * 7;
                        const weekEnd = weekStart + 7;

                        // Highlight only the 7 days in this week row
                        for (let i = weekStart; i < weekEnd && i < allDays.length; i++) {
                            allDays[i].classList.add('week-hover');
                        }
                    });
                    dayElem.addEventListener('mouseleave', function () {
                        // Remove highlight from all days
                        const container = dayElem.closest('.dayContainer');
                        if (!container) return;

                        const allDays = container.querySelectorAll('.flatpickr-day');
                        allDays.forEach(d => d.classList.remove('week-hover'));
                    });
                },
                onChange: function (selectedDates, dateStr, instance) {
                    if (selectedDates.length > 0) {
                        const clickedDate = new Date(selectedDates[0]);

                        // Get Monday of selected week
                        const dayOfWeek = clickedDate.getDay(); // 0=Sun, 1=Mon, ..., 6=Sat
                        const monday = new Date(clickedDate);

                        if (dayOfWeek === 0) {
                            // If Sunday, go back 6 days to get Monday
                            monday.setDate(clickedDate.getDate() - 6);
                        } else {
                            // Otherwise, go back (dayOfWeek - 1) days
                            monday.setDate(clickedDate.getDate() - (dayOfWeek - 1));
                        }

                        // Calculate Sunday (add 6 days to Monday)
                        const sunday = new Date(monday);
                        sunday.setDate(monday.getDate() + 6);

                        // Format dates as YYYY-MM-DD
                        const fmtDate = (d) => {
                            const year = d.getFullYear();
                            const month = String(d.getMonth() + 1).padStart(2, '0');
                            const day = String(d.getDate()).padStart(2, '0');
                            return `${year}-${month}-${day}`;
                        };

                        // Set the input values
                        instance.setDate(monday, false);
                        document.getElementById('budget-end-date').value = fmtDate(sunday);
                        document.getElementById('budget-end-display').textContent = fmtDate(sunday);

                        // Close the picker after selection
                        instance.close();
                    }
                }
            });
            console.log("✓ Budget date picker initialized");
        }
    } catch (e) {
        console.error("× Error initializing budget date picker:", e);
    }

    // Transaction filters date pickers with week highlighting
    try {
        const filterStartEl = document.getElementById('filter-start');
        if (filterStartEl) {
            flatpickr(filterStartEl, {
                ...baseConfig,
                ...weekHighlightConfig,
                onChange: function () { loadTransactionHistory(); }
            });
            console.log("✓ Filter start picker initialized");
        }
    } catch (e) {
        console.error("× Error initializing filter start picker:", e);
    }

    try {
        const filterEndEl = document.getElementById('filter-end');
        if (filterEndEl) {
            flatpickr(filterEndEl, {
                ...baseConfig,
                ...weekHighlightConfig,
                onChange: function () { loadTransactionHistory(); }
            });
            console.log("✓ Filter end picker initialized");
        }
    } catch (e) {
        console.error("× Error initializing filter end picker:", e);
    }

    // Dashboard week picker - click to select any week
    try {
        const dashboardWeekEl = document.getElementById('dashboard-week-picker');
        if (dashboardWeekEl) {
            flatpickr(dashboardWeekEl, {
                dateFormat: "Y-m-d",
                theme: "dark",
                disableMobile: true,
                animate: true,
                weekNumbers: true,
                locale: { firstDayOfWeek: 1 },
                // Highlight entire week row on hover
                onDayCreate: function (dObj, dStr, fp, dayElem) {
                    dayElem.addEventListener('mouseenter', function () {
                        const container = dayElem.closest('.dayContainer');
                        if (!container) return;

                        const allDays = Array.from(container.querySelectorAll('.flatpickr-day'));
                        const dayIndex = allDays.indexOf(dayElem);
                        const weekStart = Math.floor(dayIndex / 7) * 7;
                        const weekEnd = weekStart + 7;

                        for (let i = weekStart; i < weekEnd && i < allDays.length; i++) {
                            allDays[i].classList.add('week-hover');
                        }
                    });
                    dayElem.addEventListener('mouseleave', function () {
                        const container = dayElem.closest('.dayContainer');
                        if (!container) return;

                        const allDays = container.querySelectorAll('.flatpickr-day');
                        allDays.forEach(d => d.classList.remove('week-hover'));
                    });
                },
                onChange: function (selectedDates, dateStr, instance) {
                    if (selectedDates.length > 0) {
                        const clickedDate = new Date(selectedDates[0]);

                        // Get Monday of selected week
                        const dayOfWeek = clickedDate.getDay();
                        const monday = new Date(clickedDate);

                        if (dayOfWeek === 0) {
                            monday.setDate(clickedDate.getDate() - 6);
                        } else {
                            monday.setDate(clickedDate.getDate() - (dayOfWeek - 1));
                        }

                        // Format as YYYY-MM-DD
                        const fmtDate = (d) => {
                            const year = d.getFullYear();
                            const month = String(d.getMonth() + 1).padStart(2, '0');
                            const day = String(d.getDate()).padStart(2, '0');
                            return `${year}-${month}-${day}`;
                        };

                        // Update the current week and reload dashboard
                        currentWeekStart = fmtDate(monday);
                        loadDashboardData();

                        // Close the picker
                        instance.close();
                    }
                }
            });
            console.log("✓ Dashboard week picker initialized");
        }
    } catch (e) {
        console.error("× Error initializing dashboard week picker:", e);
    }
}

// ========================================
// NAVIGATION
// ========================================
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;

            // Update active nav item
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Show corresponding page
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(`page-${page}`).classList.add('active');

            // Load page-specific data
            if (page === 'statistics') {
                loadStatisticsData();
            } else if (page === 'budget') {
                loadBudgetConfig();
            } else if (page === 'manager') {
                initManagerCalendar(); // Initialize calendar when tab becomes visible
                loadTransactionHistory();
            } else if (page === 'history') {
                loadHistoryWeeks();
            }
        });
    });
}

// ========================================
// MANAGER TAB - Inline Calendar
// ========================================
let managerCalendarInitialized = false;

async function initManagerCalendar() {
    // Only initialize once
    if (managerCalendarInitialized) return;

    const managerCalendarEl = document.getElementById('manager-calendar');
    if (!managerCalendarEl) return;

    // Inject highlight styles if not present
    if (!document.getElementById('manager-calendar-highlights')) {
        const style = document.createElement('style');
        style.id = 'manager-calendar-highlights';
        style.innerHTML = `
            .flatpickr-day.has-data {
                background: rgba(34, 197, 94, 0.3) !important;
                border-color: #22c55e !important;
                font-weight: bold;
            }
            .flatpickr-day.has-data:hover {
                background: #22c55e !important;
                color: white;
            }
        `;
        document.head.appendChild(style);
    }

    try {
        // Fetch weeks with data to highlight
        const response = await fetch(`${API_BASE}/transactions/history/weeks`);
        const data = await response.json();
        const savedWeeks = data.weeks ? data.weeks.map(w => w.week_start) : [];

        flatpickr("#manager-calendar", {
            inline: true,
            dateFormat: "Y-m-d",
            theme: "dark",
            weekNumbers: true,
            locale: { firstDayOfWeek: 1 },

            // Highlight saved weeks
            onDayCreate: function (dObj, dStr, fp, dayElem) {
                const dateObj = dayElem.dateObj;
                // Get week start (Monday) for this date
                const dayOfWeek = dateObj.getDay();
                const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
                const monday = new Date(dateObj);
                monday.setDate(dateObj.getDate() + diff);

                const weekStart = monday.getFullYear() + '-' +
                    String(monday.getMonth() + 1).padStart(2, '0') + '-' +
                    String(monday.getDate()).padStart(2, '0');

                if (savedWeeks.includes(weekStart)) {
                    dayElem.classList.add("has-data");
                    dayElem.title = "Has transactions";
                }
            },

            // On click: Filter table to this week
            onChange: function (selectedDates, dateStr, instance) {
                if (selectedDates.length > 0) {
                    const date = selectedDates[0];
                    // Calculate Week Start (Monday) and End (Sunday)
                    const dayOfWeek = date.getDay();
                    const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
                    const monday = new Date(date);
                    monday.setDate(date.getDate() + diff);

                    const sunday = new Date(monday);
                    sunday.setDate(monday.getDate() + 6);

                    // Format dates
                    const fmtDate = (d) => {
                        return d.getFullYear() + '-' +
                            String(d.getMonth() + 1).padStart(2, '0') + '-' +
                            String(d.getDate()).padStart(2, '0');
                    };

                    // Store in global filter vars
                    managerFilterStart = fmtDate(monday);
                    managerFilterEnd = fmtDate(sunday);

                    // Update display
                    const displayEl = document.getElementById('selected-week-display');
                    if (displayEl) {
                        displayEl.innerHTML = `<span class="week-label">📅 ${managerFilterStart} – ${managerFilterEnd}</span>`;
                    }

                    // Trigger load
                    loadTransactionHistory();
                    showToast(`Viewing transactions for week of ${managerFilterStart}`, 'success');
                }
            }
        });

        managerCalendarInitialized = true;
        console.log("Manager calendar initialized successfully");
    } catch (error) {
        console.error("Error initializing manager calendar:", error);
    }
}

// ========================================
// WEEK NAVIGATION
// ========================================
function initWeekNavigation() {
    document.getElementById('prev-week').addEventListener('click', () => {
        const date = new Date(currentWeekStart);
        date.setDate(date.getDate() - 7);
        currentWeekStart = formatDate(date);
        loadDashboardData();
    });

    document.getElementById('next-week').addEventListener('click', () => {
        const date = new Date(currentWeekStart);
        date.setDate(date.getDate() + 7);
        currentWeekStart = formatDate(date);
        loadDashboardData();
    });
}

async function loadCurrentWeek() {
    try {
        const response = await fetch(`${API_BASE}/transactions/current-week`);
        const data = await response.json();
        currentWeekStart = data.week_start;
    } catch (error) {
        console.error('Error loading current week:', error);
        // Fallback to today's week
        const today = new Date();
        const monday = new Date(today);
        monday.setDate(today.getDate() - today.getDay() + 1);
        currentWeekStart = formatDate(monday);
    }
}

// ========================================
// DASHBOARD
// ========================================
async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE}/transactions/weekly/${currentWeekStart}`);
        const data = await response.json();

        weeklyData = data.data;
        document.getElementById('current-week-label').textContent = data.week_label;

        renderDashboardTables();
        updateMetrics();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Failed to load data. Is the backend running?', 'error');
    }
}

function renderDashboardTables() {
    const types = ['Income', 'Bills', 'Expenses', 'Savings', 'Debt'];
    const tableIds = ['income-table', 'bills-table', 'expenses-table', 'savings-table', 'debt-table'];

    types.forEach((type, index) => {
        const tableBody = document.querySelector(`#${tableIds[index]} tbody`);
        const typeData = weeklyData.filter(item => item.type === type);

        tableBody.innerHTML = typeData.map((item, rowIndex) => `
            <tr data-category="${item.category}" data-type="${item.type}">
                <td>${item.category}</td>
                <td>
                    <input type="number" 
                           class="budget-input" 
                           value="${item.budget.toFixed(2)}" 
                           data-field="budget"
                           step="0.01">
                </td>
                <td>
                    <input type="number" 
                           class="actual-input" 
                           value="${item.actual.toFixed(2)}" 
                           data-field="actual"
                           step="0.01">
                </td>
                <td class="${getDifferenceClass(item.difference, item.type)}">${formatCurrency(item.difference)}</td>
            </tr>
        `).join('');

        // Add input listeners
        tableBody.querySelectorAll('input').forEach(input => {
            input.addEventListener('change', handleInputChange);
            input.addEventListener('focus', (e) => e.target.select());
        });
    });
}

function handleInputChange(e) {
    const row = e.target.closest('tr');
    const category = row.dataset.category;
    const type = row.dataset.type;
    const field = e.target.dataset.field;
    const value = parseFloat(e.target.value) || 0;

    // Update weeklyData
    const item = weeklyData.find(i => i.category === category && i.type === type);
    if (item) {
        item[field] = value;

        // Recalculate difference
        if (type === 'Income') {
            item.difference = item.actual - item.budget;
        } else {
            item.difference = item.budget - item.actual;
        }

        // Update difference cell
        const diffCell = row.cells[3];
        diffCell.textContent = formatCurrency(item.difference);
        diffCell.className = getDifferenceClass(item.difference, type);
    }

    updateMetrics();
}

function updateMetrics() {
    const income = weeklyData
        .filter(i => i.type === 'Income')
        .reduce((sum, i) => sum + i.actual, 0);

    const bills = weeklyData
        .filter(i => i.type === 'Bills')
        .reduce((sum, i) => sum + i.actual, 0);

    const expenses = weeklyData
        .filter(i => i.type === 'Expenses')
        .reduce((sum, i) => sum + i.actual, 0);

    const savings = weeklyData
        .filter(i => i.type === 'Savings')
        .reduce((sum, i) => sum + i.actual, 0);

    const debt = weeklyData
        .filter(i => i.type === 'Debt')
        .reduce((sum, i) => sum + i.actual, 0);

    const totalExpenses = bills + expenses;
    const netBalance = income - totalExpenses - savings - debt;

    document.getElementById('total-income').textContent = formatCurrency(income);
    document.getElementById('total-expenses').textContent = formatCurrency(totalExpenses);
    document.getElementById('total-savings').textContent = formatCurrency(savings);

    const balanceEl = document.getElementById('net-balance');
    balanceEl.textContent = formatCurrency(netBalance);
    balanceEl.classList.toggle('positive', netBalance >= 0);
    balanceEl.classList.toggle('negative', netBalance < 0);
}

// ========================================
// SAVE FUNCTIONALITY
// ========================================
function initSaveButtons() {
    document.getElementById('save-btn').addEventListener('click', saveDashboardData);
    document.getElementById('save-budget-btn').addEventListener('click', saveBudgetConfig);
    document.getElementById('apply-dates-btn').addEventListener('click', applyDatesToAll);
}

async function saveDashboardData() {
    try {
        const response = await fetch(`${API_BASE}/transactions/weekly/${currentWeekStart}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(weeklyData)
        });

        if (response.ok) {
            showToast('Changes saved successfully!', 'success');
        } else {
            throw new Error('Save failed');
        }
    } catch (error) {
        console.error('Error saving data:', error);
        showToast('Failed to save changes', 'error');
    }
}

// ========================================
// STATISTICS
// ========================================
function initDateInputs() {
    // Initialize default dates (current week/month)
    const today = new Date();

    // Default to current week for weekly view
    const dayOfWeek = today.getDay();
    const monday = new Date(today);
    if (dayOfWeek === 0) {
        monday.setDate(today.getDate() - 6);
    } else {
        monday.setDate(today.getDate() - (dayOfWeek - 1));
    }
    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);

    // Set global date variables
    const fmtDate = (d) => {
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    window.statsStartDate = fmtDate(monday);
    window.statsEndDate = fmtDate(sunday);

    // Set inputs
    document.getElementById('stats-week-start').value = window.statsStartDate;
    document.getElementById('stats-week-end').textContent = window.statsEndDate;

    // Initial month value
    const monthStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    document.getElementById('stats-month').value = monthStr;
}

function initViewToggle() {
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;

            // Update active button
            document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Toggle date pickers
            const weeklyPicker = document.getElementById('weekly-date-picker');
            const monthlyPicker = document.getElementById('monthly-date-picker');

            if (view === 'weekly') {
                weeklyPicker.classList.remove('hidden');
                monthlyPicker.classList.add('hidden');

                // Reset to current week logic or keep existing if populated
                // For simplicity, let's refresh to current week if needed or just use current picker values
                const startVal = document.getElementById('stats-week-start').value;
                const endVal = document.getElementById('stats-week-end').textContent;

                if (startVal && endVal !== 'Select week') {
                    window.statsStartDate = startVal;
                    window.statsEndDate = endVal;
                }
            } else {
                weeklyPicker.classList.add('hidden');
                monthlyPicker.classList.remove('hidden');

                // Set to selected month range
                const monthVal = document.getElementById('stats-month').value;
                if (monthVal) {
                    const [year, month] = monthVal.split('-').map(Number);
                    const firstDay = new Date(year, month - 1, 1);
                    const lastDay = new Date(year, month, 0); // Last day of month

                    const fmtDate = (d) => {
                        const y = d.getFullYear();
                        const m = String(d.getMonth() + 1).padStart(2, '0');
                        const day = String(d.getDate()).padStart(2, '0');
                        return `${y}-${m}-${day}`;
                    };

                    window.statsStartDate = fmtDate(firstDay);
                    window.statsEndDate = fmtDate(lastDay);
                }
            }

            loadStatisticsData();
        });
    });
}

async function loadStatisticsData() {
    const startDate = window.statsStartDate;
    const endDate = window.statsEndDate;
    const groupBy = document.querySelector('.toggle-btn.active')?.dataset.view || 'weekly';

    if (!startDate || !endDate) return;

    try {
        // Load summary
        const summaryRes = await fetch(`${API_BASE}/stats/summary?start_date=${startDate}&end_date=${endDate}`);
        const summaryData = await summaryRes.json();

        const metrics = summaryData.metrics;
        document.getElementById('stats-income').textContent = formatCurrency(metrics.total_income);
        document.getElementById('stats-expenses').textContent = formatCurrency(metrics.total_bills + metrics.total_expenses);
        document.getElementById('stats-savings').textContent = formatCurrency(metrics.total_savings);
        document.getElementById('stats-balance').textContent = formatCurrency(metrics.net_balance);

        // Load chart data
        const chartRes = await fetch(`${API_BASE}/stats/chart-data?start_date=${startDate}&end_date=${endDate}&group_by=${groupBy === 'weekly' ? 'week' : 'month'}`);
        const chartData = await chartRes.json();

        // Load spending by category
        const spendingRes = await fetch(`${API_BASE}/stats/spending-by-category?start_date=${startDate}&end_date=${endDate}`);
        const spendingData = await spendingRes.json();

        // Load budget vs actual
        const budgetRes = await fetch(`${API_BASE}/stats/budget-vs-actual?start_date=${startDate}&end_date=${endDate}`);
        const budgetData = await budgetRes.json();

        // Render charts
        renderIncomeExpenseChart(chartData.data);
        renderSpendingChart(spendingData.data);
        renderTrendChart(chartData.data);
        renderBudgetActualChart(budgetData.data);
        renderTopSpendingChart(spendingData.data);

    } catch (error) {
        console.error('Error loading statistics:', error);
        showToast('Failed to load statistics', 'error');
    }
}

function renderIncomeExpenseChart(data) {
    const ctx = document.getElementById('income-expense-chart').getContext('2d');

    if (charts.incomeExpense) {
        charts.incomeExpense.destroy();
    }

    charts.incomeExpense = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.period),
            datasets: [
                {
                    label: 'Income',
                    data: data.map(d => d.income),
                    backgroundColor: '#22c55e',
                    borderRadius: 4
                },
                {
                    label: 'Expenses',
                    data: data.map(d => d.bills + d.expenses),
                    backgroundColor: '#ef4444',
                    borderRadius: 4
                }
            ]
        },
        options: getChartOptions()
    });
}

function renderSpendingChart(data) {
    const ctx = document.getElementById('spending-chart').getContext('2d');

    if (charts.spending) {
        charts.spending.destroy();
    }

    const colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#22c55e', '#14b8a6', '#ef4444', '#6366f1'];

    charts.spending = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.category),
            datasets: [{
                data: data.map(d => d.amount),
                backgroundColor: colors.slice(0, data.length),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#a1a1aa',
                        font: { size: 11 },
                        padding: 10
                    }
                }
            },
            cutout: '60%'
        }
    });
}

function renderTrendChart(data) {
    const ctx = document.getElementById('trend-chart').getContext('2d');

    if (charts.trend) {
        charts.trend.destroy();
    }

    charts.trend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.period),
            datasets: [
                {
                    label: 'Income',
                    data: data.map(d => d.income),
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Expenses',
                    data: data.map(d => d.bills + d.expenses),
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Savings',
                    data: data.map(d => d.savings),
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: getChartOptions()
    });
}

function renderBudgetActualChart(data) {
    const ctx = document.getElementById('budget-actual-chart').getContext('2d');

    if (charts.budgetActual) {
        charts.budgetActual.destroy();
    }

    charts.budgetActual = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.category),
            datasets: [
                {
                    label: 'Budget',
                    data: data.map(d => d.budget),
                    backgroundColor: '#3b82f6',
                    borderRadius: 4
                },
                {
                    label: 'Actual',
                    data: data.map(d => d.actual),
                    backgroundColor: '#22c55e',
                    borderRadius: 4
                }
            ]
        },
        options: getChartOptions()
    });
}

function renderTopSpendingChart(data) {
    const ctx = document.getElementById('top-spending-chart').getContext('2d');

    if (charts.topSpending) {
        charts.topSpending.destroy();
    }

    // Sort and take top 5
    const topData = [...data].sort((a, b) => b.amount - a.amount).slice(0, 5);

    charts.topSpending = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topData.map(d => d.category),
            datasets: [{
                data: topData.map(d => d.amount),
                backgroundColor: ['#ef4444', '#f59e0b', '#eab308', '#22c55e', '#3b82f6'],
                borderRadius: 4
            }]
        },
        options: {
            ...getChartOptions(),
            indexAxis: 'y',
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function getChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#a1a1aa',
                    font: { size: 11 }
                }
            }
        },
        scales: {
            x: {
                grid: { color: '#27272a' },
                ticks: { color: '#71717a' }
            },
            y: {
                grid: { color: '#27272a' },
                ticks: {
                    color: '#71717a',
                    callback: function (value) {
                        return '$' + value.toLocaleString();
                    }
                }
            }
        }
    };
}

// ========================================
// BUDGET CONFIG
// ========================================
function initBudgetDateInputs() {
    // Set current week as default
    const today = new Date();
    const dayOfWeek = today.getDay();
    const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // Get Monday
    const monday = new Date(today);
    monday.setDate(today.getDate() + diff);

    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);

    document.getElementById('budget-start-date').value = formatDate(monday);
    document.getElementById('budget-end-date').value = formatDate(sunday);
    document.getElementById('budget-end-display').textContent = formatDate(sunday);
}

async function loadBudgetConfig() {
    try {
        const response = await fetch(`${API_BASE}/budget/`);
        const data = await response.json();

        budgetItems = data.items;
        renderBudgetConfig(data.items);

        // Update date inputs from first item's date range
        if (data.items.length > 0 && data.items[0].start_date) {
            const startDate = data.items[0].start_date;
            const endDate = data.items[0].end_date;

            document.getElementById('budget-start-date').value = startDate;
            document.getElementById('budget-end-date').value = endDate;
            document.getElementById('budget-end-display').textContent = endDate;

            // Re-initialize flatpickr with new dates
            const startPicker = document.getElementById('budget-start-date')._flatpickr;
            if (startPicker) startPicker.setDate(startDate, false);
        }
    } catch (error) {
        console.error('Error loading budget config:', error);
        showToast('Failed to load budget configuration', 'error');
    }
}

function renderBudgetConfig(items) {
    const types = ['Income', 'Bills', 'Expenses', 'Savings', 'Debt'];
    const containerIds = ['budget-income', 'budget-bills', 'budget-expenses', 'budget-savings', 'budget-debt'];

    types.forEach((type, index) => {
        const container = document.getElementById(containerIds[index]);
        const typeItems = items.filter(item => item.type === type);

        container.innerHTML = typeItems.map(item => `
            <div class="budget-item" data-category="${item.category}" data-type="${item.type}">
                <label>${item.category}</label>
                <input type="number" value="${item.budget.toFixed(2)}" step="0.01">
            </div>
        `).join('');
    });
}

async function saveBudgetConfig() {
    const startDate = document.getElementById('budget-start-date').value;
    const endDate = document.getElementById('budget-end-date').value;

    const items = [];

    document.querySelectorAll('.budget-item').forEach(item => {
        items.push({
            category: item.dataset.category,
            type: item.dataset.type,
            budget: parseFloat(item.querySelector('input').value) || 0,
            start_date: startDate,
            end_date: endDate
        });
    });

    try {
        const response = await fetch(`${API_BASE}/budget/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ items })
        });

        if (response.ok) {
            showToast('Budget configuration saved! Dashboard will reflect changes.', 'success');
        } else {
            throw new Error('Save failed');
        }
    } catch (error) {
        console.error('Error saving budget config:', error);
        showToast('Failed to save budget configuration', 'error');
    }
}

async function applyDatesToAll() {
    const startDate = document.getElementById('budget-start-date').value;
    const endDate = document.getElementById('budget-end-date').value;

    if (!startDate || !endDate) {
        showToast('Please select both start and end dates', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/budget/apply-dates?start_date=${startDate}&end_date=${endDate}`, {
            method: 'PUT'
        });

        if (response.ok) {
            showToast(`Date range ${startDate} to ${endDate} applied to all categories!`, 'success');
            // Reload budget config to reflect changes
            await loadBudgetConfig();
        } else {
            throw new Error('Apply failed');
        }
    } catch (error) {
        console.error('Error applying dates:', error);
        showToast('Failed to apply date range', 'error');
    }
}

// ========================================
// TRANSACTIONS
// ========================================
function initTransactionModal() {
    const modal = document.getElementById('transaction-modal');
    const addBtn = document.getElementById('add-transaction-btn');
    const closeBtns = document.querySelectorAll('.close-modal, .close-modal-btn');
    const form = document.getElementById('transaction-form');

    // Open Modal
    addBtn.addEventListener('click', () => {
        // Reset form
        form.reset();
        // Set default date to today
        document.getElementById('txn-date')._flatpickr.setDate(new Date());
        modal.classList.remove('hidden');
    });

    // Close Modal
    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            modal.classList.add('hidden');
        });
    });

    // Close on click outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });

    // Initialize Modal Date Picker
    flatpickr("#txn-date", {
        dateFormat: "Y-m-d",
        theme: "dark",
        disableMobile: true,
        defaultDate: new Date()
    });

    // Form Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const transaction = {
            date: document.getElementById('txn-date').value,
            type: document.getElementById('txn-type').value,
            category: document.getElementById('txn-category').value,
            actual: parseFloat(document.getElementById('txn-amount').value),
            note: document.getElementById('txn-note').value
        };

        await addTransaction(transaction);
        modal.classList.add('hidden');
    });
}

async function addTransaction(transaction) {
    try {
        const response = await fetch(`${API_BASE}/transactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(transaction)
        });

        if (response.ok) {
            showToast('Transaction added successfully!', 'success');
            await loadTransactionHistory();
            // Also refresh dashboard if the date falls in the current view
            const txnDate = new Date(transaction.date);
            // Simple check: just reload dashboard to be safe if on dashboard page
            if (document.getElementById('page-dashboard').classList.contains('active')) {
                loadDashboardData();
            }
        } else {
            throw new Error('Failed to add transaction');
        }
    } catch (error) {
        console.error('Error adding transaction:', error);
        showToast('Failed to add transaction', 'error');
    }
}

async function deleteTransaction(id) {
    if (!confirm('Are you sure you want to delete this transaction?')) return;

    try {
        const response = await fetch(`${API_BASE}/transactions/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Transaction deleted successfully!', 'success');
            await loadTransactionHistory();
            // Refresh dashboard if needed
            if (document.getElementById('page-dashboard').classList.contains('active')) {
                loadDashboardData();
            }
        } else {
            throw new Error('Failed to delete transaction');
        }
    } catch (error) {
        console.error('Error deleting transaction:', error);
        showToast('Failed to delete transaction', 'error');
    }
}

// ========================================
// MANAGER (Individual Transactions)
// ========================================
function initTransactionFilters() {
    const filterType = document.getElementById('manager-filter-type');
    const filterStart = document.getElementById('manager-filter-start');
    const filterEnd = document.getElementById('manager-filter-end');

    // Set default filters (current month)
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);

    filterStart.value = formatDate(firstDay);
    filterEnd.value = formatDate(today);

    // Add event listeners
    filterType.addEventListener('change', loadTransactionHistory);
    filterStart.addEventListener('change', loadTransactionHistory);
    filterEnd.addEventListener('change', loadTransactionHistory);

    // Initialize the Manager Calendar
    initManagerCalendar();
}

async function initManagerCalendar() {
    // Inject styles if missing
    if (!document.getElementById('calendar-highlights')) {
        const style = document.createElement('style');
        style.id = 'calendar-highlights';
        style.innerHTML = `
            .flatpickr-day.has-data {
                background: rgba(34, 197, 94, 0.2);
                border-color: #22c55e;
                font-weight: bold;
            }
            .flatpickr-day.has-data:hover {
                background: #22c55e;
                color: white;
            }
        `;
        document.head.appendChild(style);
    }

    try {
        // Fetch weeks with data to highlight
        const response = await fetch(`${API_BASE}/transactions/history/weeks`);
        const data = await response.json();
        const savedWeeks = data.weeks.map(w => w.week_start);

        flatpickr("#manager-calendar", {
            inline: true,
            dateFormat: "Y-m-d",
            theme: "dark",
            weekNumbers: true,
            locale: { firstDayOfWeek: 1 },

            // Highlight saved weeks
            onDayCreate: function (dObj, dStr, fp, dayElem) {
                const weekStart = getWeekStart(dayElem.dateObj);
                if (savedWeeks.includes(weekStart)) {
                    dayElem.classList.add("has-data");
                    dayElem.title = "Has transactions";
                }
            },

            // On click: Filter table to this week
            onChange: function (selectedDates, dateStr, instance) {
                if (selectedDates.length > 0) {
                    const date = selectedDates[0];
                    // Calculate Week Start (Monday) and End (Sunday)
                    const day = date.getDay();
                    const diff = date.getDate() - day + (day == 0 ? -6 : 1);
                    const monday = new Date(date);
                    monday.setDate(diff);

                    const sunday = new Date(monday);
                    sunday.setDate(monday.getDate() + 6);

                    // Store in global filter vars
                    managerFilterStart = formatDate(monday);
                    managerFilterEnd = formatDate(sunday);

                    // Update display
                    const displayEl = document.getElementById('selected-week-display');
                    if (displayEl) {
                        displayEl.innerHTML = `<span class="week-label">📅 ${managerFilterStart} – ${managerFilterEnd}</span>`;
                    }

                    // Trigger load
                    loadTransactionHistory();
                    showToast(`Viewing transactions for week of ${formatDate(monday)}`, 'success');
                }
            }
        });
    } catch (error) {
        console.error("Error initializing manager calendar:", error);
    }
}

function initExportButton() {
    document.getElementById('export-manager-btn').addEventListener('click', exportTransactions);
}

async function loadTransactionHistory() {
    try {
        const typeFilter = document.getElementById('manager-filter-type').value;

        let url = `${API_BASE}/transactions/all?`;
        if (typeFilter) url += `type_filter=${typeFilter}&`;
        if (managerFilterStart) url += `start_date=${managerFilterStart}&`;
        if (managerFilterEnd) url += `end_date=${managerFilterEnd}&`;

        const response = await fetch(url);
        const data = await response.json();

        renderTransactionTable(data.transactions);
    } catch (error) {
        console.error('Error loading transactions:', error);
        showToast('Failed to load transaction history', 'error');
    }
}

function renderTransactionTable(transactions) {
    const tableBody = document.querySelector('#manager-table tbody');

    if (transactions.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 40px;">
                    No transactions found for the selected filters.
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = transactions.map(txn => `
        <tr>
            <td>${txn.date}</td>
            <td>
                ${txn.category}
                ${txn.note ? `<br><small class="text-muted">${txn.note}</small>` : ''}
            </td>
            <td><span class="type-badge type-${txn.type.toLowerCase()}">${txn.type}</span></td>
            <td class="${txn.type === 'Income' ? 'difference-positive' : ''}">${formatCurrency(txn.amount)}</td>
            <td>
                <button class="btn btn-icon delete-txn-btn" data-id="${txn.id || ''}" title="Delete">
                    🗑️
                </button>
            </td>
        </tr>
    `).join('');

    // Add delete event listeners
    document.querySelectorAll('.delete-txn-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = e.target.closest('button').dataset.id;
            if (id) {
                deleteTransaction(id);
            } else {
                showToast('Cannot delete legacy transaction without ID', 'error');
            }
        });
    });
}

async function exportTransactions() {
    try {
        window.open(`${API_BASE}/transactions/export`, '_blank');
        showToast('Exporting transactions...', 'success');
    } catch (error) {
        console.error('Error exporting:', error);
        showToast('Failed to export transactions', 'error');
    }
}

// ========================================
// HISTORY (Saved Weeks)
// ========================================
async function loadHistoryWeeks() {
    try {
        const response = await fetch(`${API_BASE}/transactions/history/weeks`);
        const data = await response.json();
        renderHistoryCalendar(data.weeks);
    } catch (error) {
        console.error('Error loading history:', error);
        showToast('Failed to load history', 'error');
    }
}

function renderHistoryCalendar(weeks) {
    // Extract just the week start dates
    const savedDates = weeks.map(w => w.week_start);

    flatpickr("#history-calendar", {
        inline: true,
        dateFormat: "Y-m-d",
        theme: "dark",

        // Highlight weeks with data
        onDayCreate: function (dObj, dStr, fp, dayElem) {
            // Check if this date's week start is in our saved list
            const weekStart = getWeekStart(dayElem.dateObj);

            if (savedDates.includes(weekStart)) {
                dayElem.classList.add("has-data");
                dayElem.title = "Click to view this week";
            }
        },

        // Handle selection
        onChange: function (selectedDates, dateStr, instance) {
            if (selectedDates.length > 0) {
                const selectedDate = selectedDates[0];
                const weekStart = getWeekStart(selectedDate);

                // Load into dashboard
                loadWeekInDashboard(weekStart);

                // Show feedback
                showToast(`Loading data for week of ${weekStart}...`, 'success');
            }
        }
    });

    // Add custom styles for the calendar highlights dynamically
    if (!document.getElementById('calendar-highlights')) {
        const style = document.createElement('style');
        style.id = 'calendar-highlights';
        style.innerHTML = `
            .flatpickr-day.has-data {
                background: rgba(34, 197, 94, 0.2);
                border-color: #22c55e;
                font-weight: bold;
            }
            .flatpickr-day.has-data:hover {
                background: #22c55e;
                color: white;
            }
            .center-content {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 2rem;
            }
        `;
        document.head.appendChild(style);
    }
}

function getWeekStart(date) {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day == 0 ? -6 : 1); // adjust when day is sunday
    const monday = new Date(d.setDate(diff));
    return formatDate(monday);
}

function loadWeekInDashboard(weekStart) {
    currentWeekStart = weekStart;

    // Switch to Dashboard tab
    const dashboardNav = document.querySelector('.nav-item[data-page="dashboard"]');
    if (dashboardNav) {
        dashboardNav.click();
    }

    // Trigger load (dashboard logic listens to tab click generally, but we might need to force reload if already on dashboard)
    // Actually the tab click handler calls loadDashboardData()
    // Let's call it explicitly to be safe as the click might not trigger if already active (logic depends on implementation)
    // In our initNavigation:
    // item.addEventListener('click', (e) => { ... item.classList.add('active'); ... loadDashboardData() if needed ...})
    // If we click() the element, it triggers the event listener.
    // So currentWeekStart is updated, then click() happens, which calls loadDashboardData() with that currentWeekStart? 
    // Wait, loadDashboardData uses global `currentWeekStart`.
    // Yes.
}

// ========================================
// HISTORY TAB FUNCTIONS
// ========================================
async function loadHistoryWeeks() {
    try {
        const response = await fetch(`${API_BASE}/transactions/history/weeks`);
        const data = await response.json();

        const tbody = document.getElementById('history-weeks-body');
        const emptyState = document.getElementById('history-empty');

        if (!data.weeks || data.weeks.length === 0) {
            tbody.innerHTML = '';
            emptyState.classList.remove('hidden');
            return;
        }

        emptyState.classList.add('hidden');

        // We need to fetch transaction counts and totals for each week
        // For now, we'll display just the week info and fetch details on demand
        // Or we can make a simple display

        tbody.innerHTML = data.weeks.map(week => {
            return `
                <tr>
                    <td>${week.label}</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td>
                        <button class="action-btn view" onclick="loadWeekInDashboard('${week.week_start}')">
                            👁️ View
                        </button>
                        <button class="action-btn delete" onclick="deleteWeek('${week.week_start}')">
                            🗑️ Delete
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

    } catch (error) {
        console.error('Error loading saved weeks:', error);
        showToast('Error loading history', 'error');
    }
}

async function deleteWeek(weekStart) {
    if (!confirm(`Are you sure you want to delete all transactions for the week of ${weekStart}? This action cannot be undone.`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/transactions/week/${weekStart}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok) {
            showToast(result.message, 'success');
            loadHistoryWeeks(); // Refresh the list
        } else {
            showToast(result.detail || 'Error deleting week', 'error');
        }
    } catch (error) {
        console.error('Error deleting week:', error);
        showToast('Error deleting week', 'error');
    }
}

// ========================================
// UTILITY FUNCTIONS
// ========================================
function formatCurrency(value) {
    if (value === null || value === undefined || isNaN(value) || value === 'NaN') {
        return '$0.00';
    }
    const absValue = Math.abs(value);
    const formatted = '$' + absValue.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return value < 0 ? '-' + formatted : formatted;
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function getDifferenceClass(difference, type) {
    if (type === 'Income') {
        return difference >= 0 ? 'difference-positive' : 'difference-negative';
    } else {
        return difference >= 0 ? 'difference-positive' : 'difference-negative';
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = toast.querySelector('.toast-message');

    toast.className = `toast ${type}`;
    toastMessage.textContent = message;

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', async () => {
    console.log("🚀 Application initializing...");

    // Initialize Navigation
    if (typeof initNavigation === 'function') {
        initNavigation();
    } else {
        console.error("initNavigation function is missing!");
    }

    // Initialize Calendar Pickers
    if (typeof initCalendarPickers === 'function') {
        initCalendarPickers();
    } else {
        console.error("initCalendarPickers function is missing!");
    }

    // Initialize Week Navigation (Dashboard)
    if (typeof initWeekNavigation === 'function') {
        initWeekNavigation();
    }

    // Load initial data
    if (typeof loadCurrentWeek === 'function') {
        await loadCurrentWeek();
    }

    if (typeof loadDashboardData === 'function') {
        loadDashboardData();
    }

    // Initialize Buttons
    const saveBudgetBtn = document.getElementById('save-budget-btn');
    if (saveBudgetBtn && typeof saveBudgetConfig === 'function') {
        saveBudgetBtn.addEventListener('click', saveBudgetConfig);
    }

    const applyDatesBtn = document.getElementById('apply-dates-btn');
    if (applyDatesBtn && typeof applyDatesToAll === 'function') {
        applyDatesBtn.addEventListener('click', applyDatesToAll);
    }

    // Initialize Dashboard Save Button - try to find the saving function
    const saveDashboardBtn = document.getElementById('save-btn');
    if (saveDashboardBtn) {
        if (typeof saveDashboardChanges === 'function') {
            saveDashboardBtn.addEventListener('click', saveDashboardChanges);
        } else if (typeof updateMetrics === 'function') {
            // If explicit save function missing, maybe updateMetrics saves? Unlikely but fallback.
            // Just log warning if missing
            console.warn("Save dashboard function not found");
        }
    }

    // Initialize Modal
    const modal = document.getElementById('transaction-modal');
    const openBtn = document.getElementById('new-transaction-btn');
    const closeBtn = document.querySelector('.close-modal');
    const cancelBtn = document.querySelector('.close-modal-btn');

    if (modal && openBtn) {
        openBtn.addEventListener('click', () => {
            modal.style.display = 'block';
            // Small delay to allow display:block to apply before adding class for transition
            setTimeout(() => modal.classList.add('show'), 10);

            // Default date to today if empty
            const dateInput = document.getElementById('txn-date');
            if (dateInput && !dateInput.value) {
                dateInput.value = new Date().toISOString().split('T')[0];
            }
        });

        const closeModal = () => {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        };

        if (closeBtn) closeBtn.addEventListener('click', closeModal);
        if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

        // Outside click
        window.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
    }
});
