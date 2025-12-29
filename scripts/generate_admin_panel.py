"""
Generate improved admin panel HTML with sidebar navigation
"""

html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - ABKBet</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            display: flex;
            min-height: 100vh;
        }

        /* ===== SIDEBAR ===== */
        .admin-sidebar {
            width: 260px;
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            border-right: 2px solid #334155;
            height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            overflow-y: auto;
            z-index: 100;
        }

        .sidebar-header {
            padding: 24px 20px;
            border-bottom: 1px solid #334155;
        }

        .sidebar-logo {
            color: #3b82f6;
            font-size: 22px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .sidebar-logo i { font-size: 28px; }

        .sidebar-nav { padding: 20px 0; }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 20px;
            color: #94a3b8;
            cursor: pointer;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
        }

        .nav-item:hover {
            background: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
        }

        .nav-item.active {
            background: rgba(59, 130, 246, 0.15);
            color: #3b82f6;
            border-left-color: #3b82f6;
        }

        .nav-item i {
            font-size: 18px;
            width: 24px;
        }

        .sidebar-footer {
            padding: 20px;
            border-top: 1px solid #334155;
            margin-top: auto;
        }

        .admin-logout {
            width: 100%;
            background: #dc2626;
            color: white;
            border: none;
            padding: 12px 16px;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .admin-logout:hover {
            background: #b91c1c;
            transform: translateY(-2px);
        }

        /* ===== MAIN CONTENT ===== */
        .admin-main {
            margin-left: 260px;
            flex: 1;
            min-height: 100vh;
        }

        .admin-header {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-bottom: 2px solid #3b82f6;
            padding: 20px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 90;
        }

        .admin-header h1 {
            color: #3b82f6;
            font-size: 26px;
        }

        .admin-user-info {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #94a3b8;
        }

        .admin-user-avatar {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: white;
        }

        .admin-container {
            padding: 32px;
            max-width: 1600px;
        }

        /* ===== STATS GRID ===== */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 24px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
            border-color: #3b82f6;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        }

        .stat-icon {
            width: 50px;
            height: 50px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-bottom: 16px;
        }

        .stat-icon.blue { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
        .stat-icon.green { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .stat-icon.purple { background: rgba(139, 92, 246, 0.2); color: #8b5cf6; }
        .stat-icon.orange { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
        .stat-icon.red { background: rgba(220, 38, 38, 0.2); color: #dc2626; }

        .stat-value {
            font-size: 36px;
            font-weight: 700;
            color: #3b82f6;
            margin-bottom: 8px;
            line-height: 1;
        }

        .stat-label {
            font-size: 14px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }

        /* ===== SECTIONS ===== */
        .admin-section {
            display: none;
        }

        .admin-section.active {
            display: block;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }

        .section-title {
            font-size: 22px;
            font-weight: 700;
            color: #e2e8f0;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .section-title i { color: #3b82f6; }

        /* ===== TABLES ===== */
        .data-table {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 24px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            background: #0f172a;
            color: #3b82f6;
            padding: 14px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        td {
            padding: 14px 16px;
            border-top: 1px solid #334155;
            font-size: 14px;
            color: #cbd5e1;
        }

        tr:hover {
            background: rgba(59, 130, 246, 0.08);
        }

        /* ===== BUTTONS ===== */
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-primary {
            background: #3b82f6;
            color: white;
        }

        .btn-primary:hover {
            background: #2563eb;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }

        .btn-approve {
            background: #10b981;
            color: white;
        }

        .btn-approve:hover {
            background: #059669;
        }

        .btn-reject, .btn-danger {
            background: #dc2626;
            color: white;
        }

        .btn-reject:hover, .btn-danger:hover {
            background: #b91c1c;
        }

        .btn-edit {
            background: #8b5cf6;
            color: white;
        }

        .btn-edit:hover {
            background: #7c3aed;
        }

        .btn-secondary {
            background: #475569;
            color: white;
        }

        /* ===== BADGES ===== */
        .badge {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .badge-pending {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .badge-completed {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .badge-failed {
            background: rgba(220, 38, 38, 0.2);
            color: #dc2626;
            border: 1px solid rgba(220, 38, 38, 0.3);
        }

        .badge-scheduled {
            background: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        .badge-live {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
            animation: pulse 2s infinite;
        }

        .badge-finished {
            background: rgba(100, 116, 139, 0.2);
            color: #64748b;
            border: 1px solid rgba(100, 116, 139, 0.3);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        /* ===== MODALS ===== */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(4px);
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 28px;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }

        .modal-header {
            font-size: 20px;
            font-weight: 700;
            color: #3b82f6;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            color: #94a3b8;
            margin-bottom: 8px;
            font-size: 14px;
            font-weight: 600;
        }

        .form-control, .form-select {
            width: 100%;
            background: #0f172a;
            border: 1px solid #334155;
            color: #e2e8f0;
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        .form-control:focus, .form-select:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }

        .form-row-3 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 12px;
        }

        .modal-footer {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            margin-top: 24px;
            padding-top: 20px;
            border-top: 1px solid #334155;
        }

        /* ===== MESSAGES ===== */
        .message {
            padding: 14px 18px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
            align-items: center;
            gap: 10px;
            font-weight: 500;
        }

        .message.active {
            display: flex;
        }

        .message.success {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid #10b981;
            color: #10b981;
        }

        .message.error {
            background: rgba(220, 38, 38, 0.15);
            border: 1px solid #dc2626;
            color: #dc2626;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #64748b;
        }

        .empty-state i {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }

        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {
            .admin-sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }

            .admin-sidebar.open {
                transform: translateX(0);
            }

            .admin-main {
                margin-left: 0;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }

            .form-row, .form-row-3 {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- SIDEBAR -->
    <div class="admin-sidebar">
        <div class="sidebar-header">
            <div class="sidebar-logo">
                <i class="fas fa-shield-alt"></i>
                <span>ABKBet Admin</span>
            </div>
        </div>
        
        <div class="sidebar-nav">
            <div class="nav-item active" onclick="showSection('dashboard')">
                <i class="fas fa-chart-line"></i>
                <span>Dashboard</span>
            </div>
            <div class="nav-item" onclick="showSection('matches')">
                <i class="fas fa-futbol"></i>
                <span>Manual Matches</span>
            </div>
            <div class="nav-item" onclick="showSection('deposits')">
                <i class="fas fa-arrow-down"></i>
                <span>Deposits</span>
            </div>
            <div class="nav-item" onclick="showSection('withdrawals')">
                <i class="fas fa-arrow-up"></i>
                <span>Withdrawals</span>
            </div>
            <div class="nav-item" onclick="showSection('users')">
                <i class="fas fa-users"></i>
                <span>Users</span>
            </div>
            <div class="nav-item" onclick="showSection('bets')">
                <i class="fas fa-ticket-alt"></i>
                <span>All Bets</span>
            </div>
            <div class="nav-item" onclick="showSection('transactions')">
                <i class="fas fa-list"></i>
                <span>Transactions</span>
            </div>
        </div>
        
        <div class="sidebar-footer">
            <button class="admin-logout" onclick="logout()">
                <i class="fas fa-sign-out-alt"></i>
                <span>Logout</span>
            </button>
        </div>
    </div>

    <!-- MAIN CONTENT -->
    <div class="admin-main">
        <div class="admin-header">
            <h1>Admin Dashboard</h1>
            <div class="admin-user-info">
                <div class="admin-user-avatar">A</div>
                <span id="adminUsername">Admin</span>
            </div>
        </div>

        <div class="admin-container">
            <div id="message" class="message"></div>

            <!-- DASHBOARD SECTION -->
            <div id="dashboard-section" class="admin-section active">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon blue">
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="stat-value" id="totalUsers">0</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon green">
                            <i class="fas fa-ticket-alt"></i>
                        </div>
                        <div class="stat-value" id="activeBets">0</div>
                        <div class="stat-label">Active Bets</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon orange">
                            <i class="fas fa-arrow-down"></i>
                        </div>
                        <div class="stat-value" id="pendingDeposits">0</div>
                        <div class="stat-label">Pending Deposits</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon red">
                            <i class="fas fa-arrow-up"></i>
                        </div>
                        <div class="stat-value" id="pendingWithdrawals">0</div>
                        <div class="stat-label">Pending Withdrawals</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon purple">
                            <i class="fas fa-coins"></i>
                        </div>
                        <div class="stat-value" id="totalVolume">₿0.00</div>
                        <div class="stat-label">Total Volume</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon green">
                            <i class="fas fa-trophy"></i>
                        </div>
                        <div class="stat-value" id="totalPayouts">₿0.00</div>
                        <div class="stat-label">Total Payouts</div>
                    </div>
                </div>

                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-clock"></i>
                        Recent Activity
                    </h2>
                </div>

                <div class="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Type</th>
                                <th>User</th>
                                <th>Amount</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="recentActivityTable">
                            <tr>
                                <td colspan="5" class="empty-state">
                                    <i class="fas fa-history"></i>
                                    <h3>No recent activity</h3>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- MATCHES SECTION -->
            <div id="matches-section" class="admin-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-futbol"></i>
                        Manual Matches Management
                    </h2>
                    <button class="btn btn-primary" onclick="openCreateMatchModal()">
                        <i class="fas fa-plus"></i>
                        Create New Match
                    </button>
                </div>

                <div class="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Match</th>
                                <th>League</th>
                                <th>Date</th>
                                <th>Status</th>
                                <th>Score</th>
                                <th>Odds (H/D/A)</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="matchesTable">
                            <tr>
                                <td colspan="8" class="empty-state">
                                    <i class="fas fa-futbol"></i>
                                    <h3>No matches yet</h3>
                                    <p>Create your first manual match</p>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- DEPOSITS SECTION -->
            <div id="deposits-section" class="admin-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-arrow-down"></i>
                        Pending Deposits
                    </h2>
                </div>

                <div class="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>User</th>
                                <th>Amount (BTC)</th>
                                <th>Method</th>
                                <th>Reference</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="depositsTable">
                            <tr>
                                <td colspan="7" class="empty-state">
                                    <i class="fas fa-inbox"></i>
                                    <h3>No pending deposits</h3>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- WITHDRAWALS SECTION -->
            <div id="withdrawals-section" class="admin-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-arrow-up"></i>
                        Pending Withdrawals
                    </h2>
                </div>

                <div class="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>User</th>
                                <th>Amount (BTC)</th>
                                <th>Method</th>
                                <th>Address</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="withdrawalsTable">
                            <tr>
                                <td colspan="7" class="empty-state">
                                    <i class="fas fa-inbox"></i>
                                    <h3>No pending withdrawals</h3>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- USERS SECTION -->
            <div id="users-section" class="admin-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-users"></i>
                        All Users
                    </h2>
                </div>

                <div class="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Balance</th>
                                <th>Is Admin</th>
                                <th>Registered</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="usersTable">
                            <tr>
                                <td colspan="7" class="empty-state">
                                    <i class="fas fa-users"></i>
                                    <h3>Loading users...</h3>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- BETS SECTION -->
            <div id="bets-section" class="admin-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-ticket-alt"></i>
                        All Bets
                    </h2>
                </div>

                <div class="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>User</th>
                                <th>Match/Event</th>
                                <th>Selection</th>
                                <th>Amount</th>
                                <th>Odds</th>
                                <th>Potential Payout</th>
                                <th>Status</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody id="betsTable">
                            <tr>
                                <td colspan="9" class="empty-state">
                                    <i class="fas fa-ticket-alt"></i>
                                    <h3>Loading bets...</h3>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- TRANSACTIONS SECTION -->
            <div id="transactions-section" class="admin-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-list"></i>
                        All Transactions
                    </h2>
                </div>

                <div class="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>User</th>
                                <th>Type</th>
                                <th>Amount</th>
                                <th>Status</th>
                                <th>Reference</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody id="transactionsTable">
                            <tr>
                                <td colspan="7" class="empty-state">
                                    <i class="fas fa-list"></i>
                                    <h3>Loading transactions...</h3>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- MATCH MODAL -->
    <div id="matchModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <i class="fas fa-futbol"></i>
                <span id="matchModalTitle">Create New Match</span>
            </div>
            <form id="matchForm">
                <input type="hidden" id="matchId">
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Home Team *</label>
                        <input type="text" class="form-control" id="homeTeam" required>
                    </div>
                    <div class="form-group">
                        <label>Away Team *</label>
                        <input type="text" class="form-control" id="awayTeam" required>
                    </div>
                </div>

                <div class="form-group">
                    <label>League *</label>
                    <input type="text" class="form-control" id="league" required placeholder="e.g., Premier League">
                </div>

                <div class="form-group">
                    <label>Match Date & Time *</label>
                    <input type="datetime-local" class="form-control" id="matchDate" required>
                </div>

                <div class="form-row-3">
                    <div class="form-group">
                        <label>Home Odds *</label>
                        <input type="number" step="0.01" class="form-control" id="homeOdds" required placeholder="1.50">
                    </div>
                    <div class="form-group">
                        <label>Draw Odds *</label>
                        <input type="number" step="0.01" class="form-control" id="drawOdds" required placeholder="3.50">
                    </div>
                    <div class="form-group">
                        <label>Away Odds *</label>
                        <input type="number" step="0.01" class="form-control" id="awayOdds" required placeholder="2.80">
                    </div>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeMatchModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i>
                        Save Match
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- RESULT MODAL -->
    <div id="resultModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <i class="fas fa-flag-checkered"></i>
                <span>Update Match Result</span>
            </div>
            <form id="resultForm">
                <input type="hidden" id="resultMatchId">
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Home Score *</label>
                        <input type="number" class="form-control" id="homeScore" min="0" required>
                    </div>
                    <div class="form-group">
                        <label>Away Score *</label>
                        <input type="number" class="form-control" id="awayScore" min="0" required>
                    </div>
                </div>

                <div class="form-group">
                    <label>Match Status *</label>
                    <select class="form-select" id="matchStatus" required>
                        <option value="scheduled">Scheduled</option>
                        <option value="live">Live</option>
                        <option value="finished">Finished</option>
                        <option value="cancelled">Cancelled</option>
                    </select>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeResultModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-check"></i>
                        Update Result
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- WITHDRAWAL MODAL -->
    <div id="withdrawalModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <i class="fas fa-money-bill-wave"></i>
                <span>Process Withdrawal</span>
            </div>
            <form id="withdrawalForm">
                <input type="hidden" id="withdrawalId">
                
                <div class="form-group">
                    <label>Transaction Reference *</label>
                    <input type="text" class="form-control" id="withdrawalTxRef" required placeholder="Enter blockchain transaction ID">
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeWithdrawalModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-check"></i>
                        Confirm Processing
                    </button>
                </div>
            </form>
        </div>
    </div>

    <script src="/static/abkbet-client.js"></script>
    <script>
        const client = new ABKBetClient();
        let currentEditMatchId = null;

        // Navigation
        function showSection(section) {
            // Update nav
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.closest('.nav-item').classList.add('active');

            // Update sections
            document.querySelectorAll('.admin-section').forEach(sec => {
                sec.classList.remove('active');
            });
            document.getElementById(section + '-section').classList.add('active');

            // Load data
            switch(section) {
                case 'dashboard':
                    loadDashboard();
                    break;
                case 'matches':
                    loadMatches();
                    break;
                case 'deposits':
                    loadDeposits();
                    break;
                case 'withdrawals':
                    loadWithdrawals();
                    break;
                case 'users':
                    loadUsers();
                    break;
                case 'bets':
                    loadAllBets();
                    break;
                case 'transactions':
                    loadTransactions();
                    break;
            }
        }

        // Messages
        function showMessage(text, type = 'success') {
            const msg = document.getElementById('message');
            msg.textContent = text;
            msg.className = `message ${type} active`;
            setTimeout(() => {
                msg.classList.remove('active');
            }, 5000);
        }

        // ===== DASHBOARD =====
        async function loadDashboard() {
            try {
                const stats = await client.request('/admin/statistics');
                document.getElementById('totalUsers').textContent = stats.total_users || 0;
                document.getElementById('activeBets').textContent = stats.active_bets || 0;
                document.getElementById('pendingDeposits').textContent = stats.pending_deposits || 0;
                document.getElementById('pendingWithdrawals').textContent = stats.pending_withdrawals || 0;
                document.getElementById('totalVolume').textContent = `₿${(stats.total_volume || 0).toFixed(8)}`;
                document.getElementById('totalPayouts').textContent = `₿${(stats.total_payouts || 0).toFixed(8)}`;
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }

        // ===== MATCHES =====
        async function loadMatches() {
            try {
                const response = await client.request('/admin/matches');
                const tbody = document.getElementById('matchesTable');
                
                if (!response.matches || response.matches.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="8" class="empty-state">
                                <i class="fas fa-futbol"></i>
                                <h3>No matches yet</h3>
                                <p>Create your first manual match</p>
                            </td>
                        </tr>`;
                    return;
                }

                tbody.innerHTML = response.matches.map(match => `
                    <tr>
                        <td>${match.id}</td>
                        <td>${match.home_team} vs ${match.away_team}</td>
                        <td>${match.league}</td>
                        <td>${new Date(match.match_date).toLocaleString()}</td>
                        <td><span class="badge badge-${match.status}">${match.status}</span></td>
                        <td>${match.home_score || 0} - ${match.away_score || 0}</td>
                        <td>${match.home_odds} / ${match.draw_odds} / ${match.away_odds}</td>
                        <td>
                            <button class="btn btn-edit" onclick="openEditMatchModal(${match.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-primary" onclick="openResultModal(${match.id})">
                                <i class="fas fa-flag-checkered"></i>
                            </button>
                            <button class="btn btn-danger" onclick="deleteMatch(${match.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
            } catch (error) {
                showMessage('Error loading matches: ' + error.message, 'error');
            }
        }

        function openCreateMatchModal() {
            document.getElementById('matchModalTitle').textContent = 'Create New Match';
            document.getElementById('matchForm').reset();
            document.getElementById('matchId').value = '';
            document.getElementById('matchModal').classList.add('active');
        }

        async function openEditMatchModal(id) {
            try {
                const match = await client.request(`/admin/matches/${id}`);
                document.getElementById('matchModalTitle').textContent = 'Edit Match';
                document.getElementById('matchId').value = match.id;
                document.getElementById('homeTeam').value = match.home_team;
                document.getElementById('awayTeam').value = match.away_team;
                document.getElementById('league').value = match.league;
                document.getElementById('matchDate').value = new Date(match.match_date).toISOString().slice(0, 16);
                document.getElementById('homeOdds').value = match.home_odds;
                document.getElementById('drawOdds').value = match.draw_odds;
                document.getElementById('awayOdds').value = match.away_odds;
                document.getElementById('matchModal').classList.add('active');
            } catch (error) {
                showMessage('Error loading match: ' + error.message, 'error');
            }
        }

        function closeMatchModal() {
            document.getElementById('matchModal').classList.remove('active');
        }

        document.getElementById('matchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const matchId = document.getElementById('matchId').value;
            const data = {
                home_team: document.getElementById('homeTeam').value,
                away_team: document.getElementById('awayTeam').value,
                league: document.getElementById('league').value,
                match_date: new Date(document.getElementById('matchDate').value).toISOString(),
                home_odds: parseFloat(document.getElementById('homeOdds').value),
                draw_odds: parseFloat(document.getElementById('drawOdds').value),
                away_odds: parseFloat(document.getElementById('awayOdds').value)
            };

            try {
                if (matchId) {
                    await client.request(`/admin/matches/${matchId}`, 'PUT', data);
                    showMessage('Match updated successfully!');
                } else {
                    await client.request('/admin/matches', 'POST', data);
                    showMessage('Match created successfully!');
                }
                closeMatchModal();
                loadMatches();
            } catch (error) {
                showMessage('Error saving match: ' + error.message, 'error');
            }
        });

        async function openResultModal(id) {
            try {
                const match = await client.request(`/admin/matches/${id}`);
                document.getElementById('resultMatchId').value = match.id;
                document.getElementById('homeScore').value = match.home_score || 0;
                document.getElementById('awayScore').value = match.away_score || 0;
                document.getElementById('matchStatus').value = match.status;
                document.getElementById('resultModal').classList.add('active');
            } catch (error) {
                showMessage('Error loading match: ' + error.message, 'error');
            }
        }

        function closeResultModal() {
            document.getElementById('resultModal').classList.remove('active');
        }

        document.getElementById('resultForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const matchId = document.getElementById('resultMatchId').value;
            const data = {
                home_score: parseInt(document.getElementById('homeScore').value),
                away_score: parseInt(document.getElementById('awayScore').value),
                status: document.getElementById('matchStatus').value
            };

            try {
                await client.request(`/admin/matches/${matchId}/result`, 'POST', data);
                showMessage('Match result updated! Bets settled automatically.');
                closeResultModal();
                loadMatches();
            } catch (error) {
                showMessage('Error updating result: ' + error.message, 'error');
            }
        });

        async function deleteMatch(id) {
            if (!confirm('Are you sure you want to delete this match?')) return;
            
            try {
                await client.request(`/admin/matches/${id}`, 'DELETE');
                showMessage('Match deleted successfully!');
                loadMatches();
            } catch (error) {
                showMessage('Error deleting match: ' + error.message, 'error');
            }
        }

        // ===== DEPOSITS =====
        async function loadDeposits() {
            try {
                const response = await client.request('/admin/deposits/pending');
                const tbody = document.getElementById('depositsTable');
                
                if (!response.deposits || response.deposits.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="7" class="empty-state">
                                <i class="fas fa-inbox"></i>
                                <h3>No pending deposits</h3>
                            </td>
                        </tr>`;
                    return;
                }

                tbody.innerHTML = response.deposits.map(deposit => `
                    <tr>
                        <td>${deposit.id}</td>
                        <td>${deposit.username}</td>
                        <td>₿${deposit.amount.toFixed(8)}</td>
                        <td>${deposit.payment_method || 'N/A'}</td>
                        <td>${deposit.reference || 'N/A'}</td>
                        <td>${new Date(deposit.created_at).toLocaleString()}</td>
                        <td>
                            <button class="btn btn-approve" onclick="approveDeposit(${deposit.id})">
                                <i class="fas fa-check"></i> Approve
                            </button>
                            <button class="btn btn-reject" onclick="rejectDeposit(${deposit.id})">
                                <i class="fas fa-times"></i> Reject
                            </button>
                        </td>
                    </tr>
                `).join('');
            } catch (error) {
                showMessage('Error loading deposits: ' + error.message, 'error');
            }
        }

        async function approveDeposit(id) {
            if (!confirm('Approve this deposit?')) return;
            
            try {
                await client.request(`/admin/deposits/${id}/approve`, 'POST');
                showMessage('Deposit approved successfully!');
                loadDeposits();
                loadDashboard();
            } catch (error) {
                showMessage('Error approving deposit: ' + error.message, 'error');
            }
        }

        async function rejectDeposit(id) {
            if (!confirm('Reject this deposit?')) return;
            
            try {
                await client.request(`/admin/deposits/${id}/reject`, 'POST');
                showMessage('Deposit rejected successfully!');
                loadDeposits();
                loadDashboard();
            } catch (error) {
                showMessage('Error rejecting deposit: ' + error.message, 'error');
            }
        }

        // ===== WITHDRAWALS =====
        async function loadWithdrawals() {
            try {
                const response = await client.request('/admin/withdrawals/pending');
                const tbody = document.getElementById('withdrawalsTable');
                
                if (!response.withdrawals || response.withdrawals.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="7" class="empty-state">
                                <i class="fas fa-inbox"></i>
                                <h3>No pending withdrawals</h3>
                            </td>
                        </tr>`;
                    return;
                }

                tbody.innerHTML = response.withdrawals.map(withdrawal => `
                    <tr>
                        <td>${withdrawal.id}</td>
                        <td>${withdrawal.username}</td>
                        <td>₿${withdrawal.amount.toFixed(8)}</td>
                        <td>${withdrawal.payment_method || 'N/A'}</td>
                        <td>${withdrawal.bitcoin_address || 'N/A'}</td>
                        <td>${new Date(withdrawal.created_at).toLocaleString()}</td>
                        <td>
                            <button class="btn btn-primary" onclick="openWithdrawalModal(${withdrawal.id})">
                                <i class="fas fa-paper-plane"></i> Process
                            </button>
                        </td>
                    </tr>
                `).join('');
            } catch (error) {
                showMessage('Error loading withdrawals: ' + error.message, 'error');
            }
        }

        function openWithdrawalModal(id) {
            document.getElementById('withdrawalId').value = id;
            document.getElementById('withdrawalTxRef').value = '';
            document.getElementById('withdrawalModal').classList.add('active');
        }

        function closeWithdrawalModal() {
            document.getElementById('withdrawalModal').classList.remove('active');
        }

        document.getElementById('withdrawalForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('withdrawalId').value;
            const txRef = document.getElementById('withdrawalTxRef').value;

            try {
                await client.request(`/admin/withdrawals/${id}/process`, 'POST', {
                    transaction_reference: txRef
                });
                showMessage('Withdrawal processed successfully!');
                closeWithdrawalModal();
                loadWithdrawals();
                loadDashboard();
            } catch (error) {
                showMessage('Error processing withdrawal: ' + error.message, 'error');
            }
        });

        // ===== USERS =====
        async function loadUsers() {
            try {
                const response = await client.request('/admin/users');
                const tbody = document.getElementById('usersTable');
                
                if (!response.users || response.users.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="7" class="empty-state">
                                <i class="fas fa-users"></i>
                                <h3>No users found</h3>
                            </td>
                        </tr>`;
                    return;
                }

                tbody.innerHTML = response.users.map(user => `
                    <tr>
                        <td>${user.id}</td>
                        <td>${user.username}</td>
                        <td>${user.email}</td>
                        <td>₿${user.balance ? user.balance.toFixed(8) : '0.00000000'}</td>
                        <td>${user.is_admin ? '<span class="badge badge-completed">Yes</span>' : '<span class="badge badge-pending">No</span>'}</td>
                        <td>${new Date(user.created_at).toLocaleDateString()}</td>
                        <td>
                            <button class="btn btn-primary" onclick="viewUser(${user.id})">
                                <i class="fas fa-eye"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
            } catch (error) {
                showMessage('Error loading users: ' + error.message, 'error');
            }
        }

        async function viewUser(id) {
            try {
                const user = await client.request(`/admin/users/${id}`);
                alert(`User Details:\n\nID: ${user.id}\nUsername: ${user.username}\nEmail: ${user.email}\nBalance: ₿${user.balance || 0}\nAdmin: ${user.is_admin ? 'Yes' : 'No'}`);
            } catch (error) {
                showMessage('Error loading user: ' + error.message, 'error');
            }
        }

        // ===== BETS =====
        async function loadAllBets() {
            try {
                const response = await client.request('/admin/users');
                const tbody = document.getElementById('betsTable');
                tbody.innerHTML = `
                    <tr>
                        <td colspan="9" class="empty-state">
                            <i class="fas fa-ticket-alt"></i>
                            <h3>Bet viewing coming soon</h3>
                            <p>This feature is under development</p>
                        </td>
                    </tr>`;
            } catch (error) {
                showMessage('Error loading bets: ' + error.message, 'error');
            }
        }

        // ===== TRANSACTIONS =====
        async function loadTransactions() {
            try {
                const response = await client.request('/admin/transactions');
                const tbody = document.getElementById('transactionsTable');
                
                if (!response.transactions || response.transactions.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="7" class="empty-state">
                                <i class="fas fa-list"></i>
                                <h3>No transactions found</h3>
                            </td>
                        </tr>`;
                    return;
                }

                tbody.innerHTML = response.transactions.map(tx => `
                    <tr>
                        <td>${tx.id}</td>
                        <td>${tx.username}</td>
                        <td>${tx.transaction_type}</td>
                        <td>₿${tx.amount.toFixed(8)}</td>
                        <td><span class="badge badge-${tx.status}">${tx.status}</span></td>
                        <td>${tx.reference || 'N/A'}</td>
                        <td>${new Date(tx.created_at).toLocaleString()}</td>
                    </tr>
                `).join('');
            } catch (error) {
                showMessage('Error loading transactions: ' + error.message, 'error');
            }
        }

        // Logout
        function logout() {
            localStorage.removeItem('token');
            window.location.href = '/';
        }

        // Init
        loadDashboard();
    </script>
</body>
</html>
'''

# Write to file
output_path = 'templates/admin_new.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Generated new admin panel: {output_path}")
print("📝 This file is ready to replace templates/admin.html")
