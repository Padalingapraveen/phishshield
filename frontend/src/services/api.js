// With Vite proxy, all API calls go to the same origin → no CORS issues.
// VITE_API_BASE_URL can still override this for production deployments.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function request(url, options = {}) {
    options.credentials = "include";

    const token = localStorage.getItem("access_token");
    if (token) {
        options.headers = {
            ...options.headers,
            "Authorization": `Bearer ${token}`
        };
    }

    const response = await fetch(
        `${API_BASE_URL}${url}`,
        options
    );

    if (!response.ok) {
        let message = `Request failed: ${response.status}`;

        try {
            const errorData = await response.json();

            if (errorData.detail) {
                message = `[${response.status}] ${errorData.detail}`;
            }
        } catch {
            try {
                const text = await response.text();

                if (text) {
                    message = `[${response.status}] ${text}`;
                }
            } catch {
                // Keep default message
            }
        }

        const error = new Error(message);
        error.status = response.status;
        throw error;
    }

    return await response.json();
}


// ==================================================
// AUTHENTICATION
// ==================================================
export async function register(username, password) {
    return request(
        "/auth/register",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, password })
        }
    );
}

export async function logout() {
    return request(
        "/auth/logout",
        {
            method: "POST"
        }
    );
}

// ==================================================
// EMAIL PREDICTION
// ==================================================

export async function predictEmail(email) {
    return request(
        "/predict",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(email)
        }
    );
}


// ==================================================
// EVENTS
// ==================================================

export async function getEvents(limit = 100, offset = 0) {
    return request(
        `/events?limit=${limit}&offset=${offset}`
    );
}


// ==================================================
// STATISTICS
// ==================================================

export async function getStatistics() {
    return request(
        "/statistics"
    );
}


// ==================================================
// HEALTH
// ==================================================

export async function getHealth() {
    return request(
        "/health"
    );
}


// ==================================================
// DASHBOARD OVERVIEW
// ==================================================

export async function getDashboardOverview() {
    return request(
        "/dashboard/overview"
    );
}


// ==================================================
// RECENT EVENTS
// ==================================================

export async function getRecentEvents(limit = 10) {
    return request(
        `/dashboard/recent?limit=${limit}`
    );
}


// ==================================================
// PHISHING DISTRIBUTION
// ==================================================

export async function getDistribution() {
    return request(
        "/dashboard/distribution"
    );
}


// ==================================================
// RISK DISTRIBUTION
// ==================================================

export async function getRiskDistribution() {
    return request(
        "/dashboard/risk-distribution"
    );
}


// ==================================================
// DETECTION TIMELINE
// ==================================================

export async function getTimeline(hours = 24) {
    return request(
        `/dashboard/timeline?hours=${hours}`
    );
}

// ==================================================
// EXTENSION MANAGEMENT
// ==================================================

export async function getExtensionStatus() {
    return request("/extension/status");
}

export async function toggleExtension() {
    return request("/extension/toggle", { method: "POST" });
}

// ==================================================
// REPORTS
// ==================================================

export async function generateReport(days = 7) {
    return request(
        `/reports/generate?days=${days}`
    );
}

// ==================================================
// ADMIN CONSOLE
// ==================================================

export async function getUsers() {
    return request(
        "/admin/users"
    );
}

export async function getAdminScans(limit = 100, offset = 0) {
    return request(
        `/admin/scans?limit=${limit}&offset=${offset}`
    );
}

// ==================================================
// MODEL PERFORMANCE (ADMIN ONLY)
// ==================================================

export async function getModelPerformance() {
    return request("/model/performance");
}

export async function regenerateModelCharts() {
    return request("/model/performance/generate-charts", {
        method: "POST"
    });
}

export function getModelChartUrl(chartName) {
    const token = localStorage.getItem("access_token");
    const baseUrl = `${API_BASE_URL}/model/performance/charts/${chartName}`;
    return token ? `${baseUrl}?token=${encodeURIComponent(token)}` : baseUrl;
}

