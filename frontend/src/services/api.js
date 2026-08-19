const API_BASE_URL = "http://127.0.0.1:8000";

async function request(url, options = {}) {
    const response = await fetch(
        `${API_BASE_URL}${url}`,
        options
    );

    if (!response.ok) {
        let message = `Request failed: ${response.status}`;

        try {
            const errorData = await response.json();

            if (errorData.detail) {
                message = errorData.detail;
            }
        } catch {
            try {
                const text = await response.text();

                if (text) {
                    message = text;
                }
            } catch {
                // Keep default message
            }
        }

        throw new Error(message);
    }

    return await response.json();
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

export async function getEvents(limit = 100) {
    return request(
        `/events?limit=${limit}`
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

