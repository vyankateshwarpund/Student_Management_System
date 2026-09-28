/**
 * Centralized API & Authentication Client for Student Management System
 */

const API_BASE = '/api';

const auth = {
    getToken() {
        return localStorage.getItem('access_token');
    },
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },
    getUser() {
        const u = localStorage.getItem('user');
        return u ? JSON.parse(u) : null;
    },
    setSession(tokens, user) {
        if (tokens.access) localStorage.setItem('access_token', tokens.access);
        if (tokens.refresh) localStorage.setItem('refresh_token', tokens.refresh);
        if (user) localStorage.setItem('user', JSON.stringify(user));
    },
    clearSession() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },
    isAuthenticated() {
        return !!this.getToken();
    },
    getRole() {
        const u = this.getUser();
        return u ? u.role : null;
    },
    isAdmin() {
        return this.getRole() === 'admin';
    },
    isTeacher() {
        return this.getRole() === 'teacher';
    },
    isStudent() {
        return this.getRole() === 'student';
    },
    async refreshToken() {
        const refresh = this.getRefreshToken();
        if (!refresh) return null;
        try {
            const resp = await fetch(`${API_BASE}/auth/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh })
            });
            if (resp.ok) {
                const data = await resp.json();
                localStorage.setItem('access_token', data.access);
                if (data.refresh) localStorage.setItem('refresh_token', data.refresh);
                return data.access;
            }
        } catch (e) {
            console.error('Token refresh failed', e);
        }
        this.clearSession();
        return null;
    },
    logout() {
        const refresh = this.getRefreshToken();
        if (refresh) {
            fetch(`${API_BASE}/auth/logout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getToken()}`
                },
                body: JSON.stringify({ refresh })
            }).finally(() => {
                this.clearSession();
                window.location.href = '/login/';
            });
        } else {
            this.clearSession();
            window.location.href = '/login/';
        }
    },
    requireAuth(allowedRoles = null) {
        if (!this.isAuthenticated()) {
            window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
            return false;
        }
        if (allowedRoles && !allowedRoles.includes(this.getRole())) {
            showToast('Access denied for your role.', 'danger');
            // Redirect to appropriate dashboard
            setTimeout(() => {
                const role = this.getRole();
                if (role === 'admin') window.location.href = '/dashboard/admin/';
                else if (role === 'teacher') window.location.href = '/dashboard/teacher/';
                else window.location.href = '/dashboard/student/';
            }, 1000);
            return false;
        }
        return true;
    }
};

const api = {
    async request(endpoint, options = {}) {
        let token = auth.getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        let url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
        let resp = await fetch(url, { ...options, headers });

        // Handle 401 Unauthorized by attempting token refresh
        if (resp.status === 401 && auth.getRefreshToken() && !options._retry) {
            options._retry = true;
            token = await auth.refreshToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
                resp = await fetch(url, { ...options, headers });
            } else {
                auth.clearSession();
                window.location.href = '/login/';
                throw new Error('Session expired');
            }
        }

        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
            const errorMsg = data.message || (data.errors ? JSON.stringify(data.errors) : `Error: ${resp.status}`);
            const error = new Error(errorMsg);
            error.status = resp.status;
            error.data = data;
            throw error;
        }
        return data;
    },

    get(endpoint, params = {}) {
        const query = new URLSearchParams(params).toString();
        const url = query ? `${endpoint}${endpoint.includes('?') ? '&' : '?'}${query}` : endpoint;
        return this.request(url, { method: 'GET' });
    },

    post(endpoint, body = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body)
        });
    },

    put(endpoint, body = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body)
        });
    },

    patch(endpoint, body = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(body)
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
};

/**
 * Toast Notification Helper
 */
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toastId = 'toast-' + Math.random().toString(36).substr(2, 9);
    const bgClass = type === 'success' ? 'text-bg-success' : type === 'danger' ? 'text-bg-danger' : type === 'warning' ? 'text-bg-warning' : 'text-bg-primary';
    const icon = type === 'success' ? 'bi-check-circle' : type === 'danger' ? 'bi-exclamation-octagon' : 'bi-info-circle';

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center gap-2">
                    <i class="bi ${icon} fs-5"></i>
                    <span>${message}</span>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', toastHtml);
    const toastEl = document.getElementById(toastId);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 4000 });
    bsToast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

/**
 * Update UI for current authenticated user
 */
function initUserNavbar() {
    const user = auth.getUser();
    if (!user) return;

    const role = (user.role || 'student').toLowerCase();
    const fullName = user.full_name || (user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user.username);
    const profileInfo = user.profile_info || {};

    // 1. Update all user display name elements
    document.querySelectorAll('.user-display-name').forEach(el => {
        el.textContent = fullName;
    });

    // 2. Update user role subtitle in navbar button
    let subtitle = profileInfo.subtitle || (
        role === 'admin' ? 'System Administrator' :
        role === 'teacher' ? 'Faculty / Teacher' :
        'Student Portal'
    );
    // Compact long course or department titles for clean pill button presentation
    if (subtitle.includes('Computer Science & Engineering')) {
        subtitle = subtitle.replace('Computer Science & Engineering', 'CSE');
    }
    if (subtitle.includes('Electronics & Communication')) {
        subtitle = subtitle.replace('Electronics & Communication', 'ECE');
    }
    if (subtitle.includes('Information Technology')) {
        subtitle = subtitle.replace('Information Technology', 'IT');
    }
    document.querySelectorAll('.user-display-role-sub').forEach(el => {
        el.textContent = subtitle;
    });

    // 3. Update dropdown role badge
    const badgeEl = document.getElementById('navRoleBadge');
    if (badgeEl) {
        if (role === 'admin') {
            badgeEl.className = 'badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 mt-1';
            badgeEl.textContent = 'Administrator';
        } else if (role === 'teacher') {
            badgeEl.className = 'badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25 mt-1';
            badgeEl.textContent = profileInfo.department ? `Faculty • ${profileInfo.department}` : 'Teacher / Faculty';
        } else {
            badgeEl.className = 'badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 mt-1';
            badgeEl.textContent = profileInfo.subtitle || 'Student • Sem 3';
        }
    }

    // 4. Update avatar images if available
    const avatarImgs = document.querySelectorAll('.user-avatar-img');
    if (avatarImgs.length) {
        let avatarSrc = user.profile_photo;
        if (!avatarSrc) {
            if (role === 'teacher') {
                avatarSrc = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=120';
            } else if (role === 'admin') {
                avatarSrc = 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&q=80&w=120';
            } else {
                avatarSrc = 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=120';
            }
        }
        avatarImgs.forEach(img => {
            img.src = avatarSrc;
            img.alt = fullName;
        });
    }

    // 5. Update user-display-role badges if any
    const roleEls = document.querySelectorAll('.user-display-role');
    roleEls.forEach(el => {
        el.textContent = role.toUpperCase();
        el.className = `badge rounded-pill user-display-role ${
            role === 'admin' ? 'bg-danger' : role === 'teacher' ? 'bg-primary' : 'bg-success'
        }`;
    });

    // 6. Update Dashboard Link and Brand Link dynamically
    const targetDashboard = role === 'admin' ? '/dashboard/admin/' : (role === 'teacher' ? '/dashboard/teacher/' : '/dashboard/student/');
    const dashLink = document.getElementById('nav-dashboard-link');
    if (dashLink) dashLink.href = targetDashboard;

    const brandLink = document.getElementById('navBrandLink');
    if (brandLink) brandLink.href = targetDashboard;

    // 7. Hide or show elements with role classes
    document.querySelectorAll('[data-role]').forEach(el => {
        const allowed = el.getAttribute('data-role').split(',').map(r => r.trim().toLowerCase());
        if (!allowed.includes(role)) {
            el.style.setProperty('display', 'none', 'important');
        } else {
            el.style.removeProperty('display');
        }
    });

    // 8. Load database-driven notifications
    loadNavbarNotifications();
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

async function loadNavbarNotifications() {
    const badge = document.getElementById('navNotificationBadge');
    const container = document.getElementById('navNotificationItems');
    if (!container) return;

    try {
        const res = await api.get('/announcements/');
        const list = res.results || res.data || [];
        if (!list.length) {
            if (badge) badge.classList.add('d-none');
            container.innerHTML = `
                <li class="p-3 text-center text-secondary small">
                    No active notifications
                </li>
            `;
            return;
        }

        if (badge) {
            badge.textContent = Math.min(list.length, 99);
            badge.classList.remove('d-none');
        }

        container.innerHTML = list.slice(0, 3).map(item => {
            const dateStr = item.created_at ? new Date(item.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' }) : '';
            return `
                <li>
                    <a class="dropdown-item py-2 px-2 small rounded text-wrap d-block" href="/noticeboard/">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <strong class="text-dark text-truncate">${escapeHtml(item.title)}</strong>
                            <span class="badge bg-light text-secondary border font-monospace ms-2" style="font-size: 0.65rem;">${dateStr}</span>
                        </div>
                        <small class="text-secondary d-block text-truncate" style="max-width: 280px;">${escapeHtml(item.content || '').substring(0, 60)}...</small>
                    </a>
                </li>
            `;
        }).join('');
    } catch (e) {
        if (badge) badge.classList.add('d-none');
        container.innerHTML = `
            <li class="p-3 text-center text-secondary small">
                <a href="/noticeboard/" class="text-decoration-none">Open Noticeboard &rarr;</a>
            </li>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initUserNavbar();

    // Setup Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', (e) => {
            e.preventDefault();
            document.body.classList.toggle('sidebar-toggled');
        });
    }

    // Setup Global Logout buttons
    document.querySelectorAll('.btn-logout').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('Are you sure you want to log out?')) {
                auth.logout();
            }
        });
    });

    // Global Ctrl+K / Cmd+K Search focus
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            const searchInput = document.getElementById('searchInput') || document.getElementById('filterAttSearch');
            if (searchInput) {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        }
    });
});

/**
 * Export any HTML table to CSV file
 */
function exportTableToCSV(tableSelector, filename = 'export.csv') {
    const table = document.querySelector(tableSelector);
    if (!table) return;

    const rows = Array.from(table.querySelectorAll('tr'));
    const csvContent = rows.map(row => {
        const cols = Array.from(row.querySelectorAll('th, td'));
        return cols
            .filter(col => !col.classList.contains('no-export') && !col.querySelector('.btn-group') && !col.querySelector('button'))
            .map(col => {
                let text = col.innerText.replace(/"/g, '""').trim();
                return `"${text}"`;
            })
            .join(',');
    }).filter(line => line.length > 0).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    showToast(`Downloaded ${filename}`, 'success');
}

