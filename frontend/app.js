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
    flatpickr("#stats-week-start", {
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

    // Statistics page - Monthly picker (year and month only)
    flatpickr("#stats-month", {
        dateFormat: "Y-m",
        theme: "dark",
        disableMobile: true,
        animate: true,
        plugins: [new monthSelectPlugin({
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

    // Budget config - Week picker with auto end date and week highlighting
    flatpickr("#budget-start-date", {
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

    // Transaction filters date pickers with week highlighting
    flatpickr("#filter-start", {
        ...baseConfig,
        ...weekHighlightConfig,
        onChange: function () { loadTransactionHistory(); }
    });

    flatpickr("#filter-end", {
        ...baseConfig,
        ...weekHighlightConfig,
        onChange: function () { loadTransactionHistory(); }
    });

    // Dashboard week picker - click to select any week
    flatpickr("#dashboard-week-picker", {
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
            } else if (page === 'transactions') {
                loadTransactionHistory();
            }
        });
    });
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
function initTransactionFilters() {
    const filterType = document.getElementById('filter-type');
    const filterStart = document.getElementById('filter-start');
    const filterEnd = document.getElementById('filter-end');

    // Set default dates
    const today = new Date();
    const threeMonthsAgo = new Date(today);
    threeMonthsAgo.setMonth(today.getMonth() - 3);

    filterStart.value = formatDate(threeMonthsAgo);
    filterEnd.value = formatDate(today);

    // Add event listeners
    filterType.addEventListener('change', loadTransactionHistory);
    filterStart.addEventListener('change', loadTransactionHistory);
    filterEnd.addEventListener('change', loadTransactionHistory);
}

function initExportButton() {
    document.getElementById('export-btn').addEventListener('click', exportTransactions);
}

async function loadTransactionHistory() {
    try {
        const typeFilter = document.getElementById('filter-type').value;
        const startDate = document.getElementById('filter-start').value;
        const endDate = document.getElementById('filter-end').value;

        let url = `${API_BASE}/transactions/all?`;
        if (typeFilter) url += `type_filter=${typeFilter}&`;
        if (startDate) url += `start_date=${startDate}&`;
        if (endDate) url += `end_date=${endDate}&`;

        const response = await fetch(url);
        const data = await response.json();

        renderTransactionTable(data.transactions);
    } catch (error) {
        console.error('Error loading transactions:', error);
        showToast('Failed to load transaction history', 'error');
    }
}

function renderTransactionTable(transactions) {
    const tableBody = document.querySelector('#transactions-log-table tbody');

    if (transactions.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 40px;">
                    No transactions found for the selected filters.
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = transactions.map(txn => `
        <tr>
            <td>${txn.date}</td>
            <td>${txn.category}</td>
            <td><span class="type-badge type-${txn.type.toLowerCase()}">${txn.type}</span></td>
            <td class="${txn.type === 'Income' ? 'difference-positive' : ''}">${formatCurrency(txn.amount)}</td>
        </tr>
    `).join('');
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
// UTILITY FUNCTIONS
// ========================================
function formatCurrency(value) {
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
