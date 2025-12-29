/**
 * ABKBet JavaScript Client Library
 * Simple client for interacting with the ABKBet API
 */

class ABKBetClient {
    constructor(baseURL = null) {
        // Auto-detect the correct API URL based on current page
        if (!baseURL) {
            // Use relative URL to work on any domain (localhost, ngrok, PythonAnywhere)
            baseURL = '/api';
        }
        this.baseURL = baseURL;
        this.token = localStorage.getItem('abkbet_token'); // Restore token from localStorage
        this.user = null;
        
        // If token exists, restore user session
        if (this.token) {
            this.restoreSession();
        }
    }

    /**
     * Set authentication token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('abkbet_token', token);
    }

    /**
     * Get authentication token
     */
    getToken() {
        return this.token || localStorage.getItem('abkbet_token');
    }

    /**
     * Make API request
     * Supports two calling conventions:
     * 1. request(endpoint, options) - Standard fetch options
     * 2. request(endpoint, method, data) - Simplified API
     */
    async request(endpoint, methodOrOptions = {}, data = null) {
        const url = `${this.baseURL}${endpoint}`;
        
        // Determine if using simplified API (endpoint, method, data)
        let options = {};
        if (typeof methodOrOptions === 'string') {
            // Simplified API: request(endpoint, 'GET') or request(endpoint, 'POST', {...})
            options.method = methodOrOptions;
            if (data) {
                options.body = JSON.stringify(data);
            }
        } else {
            // Standard API: request(endpoint, {method, body, headers, ...})
            options = methodOrOptions;
        }
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.getToken()) {
            headers['Authorization'] = `Bearer ${this.getToken()}`;
        }

        const response = await fetch(url, {
            ...options,
            headers
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: `HTTP ${response.status}: ${response.statusText}` }));
            throw new Error(error.message || error.error || 'API Error');
        }

        return response.json();
    }

    /**
     * Authentication Methods
     */

    async register(username, email, password) {
        const data = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
        this.setToken(data.access_token);
        this.user = data.user;
        return data;
    }

    async login(username, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        this.setToken(data.access_token);
        this.user = data.user;
        return data;
    }

    async restoreSession() {
        try {
            const response = await this.getProfile();
            this.user = response.user; // Extract user from nested response
            return this.user;
        } catch (error) {
            // Token is invalid, clear it
            this.logout();
            return null;
        }
    }

    async getProfile() {
        return this.request('/auth/profile');
    }

    async changePassword(currentPassword, newPassword) {
        return this.request('/auth/change-password', {
            method: 'POST',
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
    }

    /**
     * Payment Methods
     */

    async getWallet() {
        return this.request('/payment/wallet');
    }

    async getBalance() {
        return this.request('/payment/balance');
    }

    async deposit(txHash, amount) {
        return this.request('/payment/deposit', {
            method: 'POST',
            body: JSON.stringify({ tx_hash: txHash, amount })
        });
    }

    async withdraw(toAddress, amount) {
        return this.request('/payment/withdraw', {
            method: 'POST',
            body: JSON.stringify({ to_address: toAddress, amount })
        });
    }

    async getTransactions(limit = 50) {
        return this.request(`/payment/transactions?limit=${limit}`);
    }

    async getFeeEstimate() {
        return this.request('/payment/fee-estimate');
    }

    /**
     * Betting Methods
     */

    async createBet(amount, odds, betType, eventDescription, market_type = null, selection = null, booking_code = null, match_id = null) {
        const payload = {
            amount,
            odds,
            bet_type: betType,
            event_description: eventDescription
        };
        if (market_type) payload.market_type = market_type;
        if (selection) payload.selection = selection;
        if (booking_code) payload.booking_code = booking_code;
        if (match_id) payload.match_id = match_id;

        return this.request('/bets', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    }

    async getBet(betId) {
        return this.request(`/bets/${betId}`);
    }

    async getUserBets(status = null) {
        const url = status ? `/bets/user/all?status=${status}` : '/bets/user/all';
        return this.request(url);
    }

    async getActiveBets() {
        return this.request('/bets/active');
    }

    async getStatistics() {
        return this.request('/bets/statistics');
    }

    async cancelBet(betId) {
        return this.request(`/bets/${betId}/cancel`, {
            method: 'POST'
        });
    }

    async cashoutBet(betId) {
        return this.request(`/bets/${betId}/cashout`, {
            method: 'POST'
        });
    }

    async getCashoutValue(betId) {
        return this.request(`/bets/${betId}/cashout-value`);
    }

    /**
     * Admin Methods
     */

    async settleBet(betId, result, payout = null) {
        return this.request(`/admin/bets/${betId}/settle`, {
            method: 'POST',
            body: JSON.stringify({ result, payout })
        });
    }

    async listUsers(page = 1, perPage = 20) {
        return this.request(`/admin/users?page=${page}&per_page=${perPage}`);
    }

    async getUserDetails(userId) {
        return this.request(`/admin/users/${userId}`);
    }

    async listTransactions(page = 1, perPage = 50, status = null) {
        const url = status 
            ? `/admin/transactions?page=${page}&per_page=${perPage}&status=${status}`
            : `/admin/transactions?page=${page}&per_page=${perPage}`;
        return this.request(url);
    }

    async getPlatformStatistics() {
        return this.request('/admin/statistics');
    }

    /**
     * Booking Code Methods
     */

    async generateBookingCode(betData) {
        return this.request('/booking/generate', {
            method: 'POST',
            body: JSON.stringify({ bet_data: JSON.stringify(betData) })
        });
    }

    async loadBookingCode(code) {
        return this.request(`/booking/${code}`);
    }

    /**
     * Utility Methods
     */

    isLoggedIn() {
        return !!this.getToken();
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('abkbet_token');
    }
}

// Export for use in Node.js or as module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ABKBetClient;
}
function openModal(id) {
  document.getElementById(id).style.display = "block";
}

function closeModal(id) {
  document.getElementById(id).style.display = "none";
}

// Optional: close when clicking outside
window.onclick = function(event) {
  const modals = document.getElementsByClassName("modal");
  for (let modal of modals) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  }
};