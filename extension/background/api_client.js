// Centralized API configuration
const API_URL = "http://127.0.0.1:8000";

let authToken = null;

// Initialize token from storage
chrome.storage.local.get(['token'], function(result) {
    if (result.token) {
        authToken = result.token;
    }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "login") {
        const formData = new URLSearchParams();
        formData.append("username", request.username);
        formData.append("password", request.password);

        fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString()
        })
        .then(async response => {
            if (!response.ok) {
                throw new Error("Invalid username or password");
            }
            return response.json();
        })
        .then(data => {
            authToken = data.access_token;
            chrome.storage.local.set({ token: authToken });
            sendResponse({ success: true });
        })
        .catch(error => {
            sendResponse({ success: false, error: error.message });
        });
        return true;
    }

    if (request.action === "logout") {
        authToken = null;
        chrome.storage.local.remove('token');
        sendResponse({ success: true });
        return true;
    }

    if (request.action === "check_auth") {
        sendResponse({ authorized: !!authToken });
        return true;
    }

    if (request.action === "predict") {
        if (!authToken) {
            sendResponse({ success: false, error: "Not authorized. Please login first." });
            return true;
        }
        
        // Ensure strictly schema fields
        const payload = {
            sender: request.data.sender || "",
            receiver: request.data.receiver || "",
            subject: request.data.subject || "",
            body: request.data.body || "",
            source: "extension"
        };

        fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(payload)
        })
        .then(async response => {
            if (response.status === 401) {
                // Token expired or invalid
                authToken = null;
                chrome.storage.local.remove('token');
                throw new Error("Session expired. Please login again.");
            }
            if (!response.ok) {
                throw new Error(`API returned status ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            sendResponse({ success: true, result: data });
        })
        .catch(error => {
            console.error("PhishGuard API Error:", error);
            sendResponse({ success: false, error: error.message || "PhishGuard API is unavailable." });
        });

        return true; // keep channel open for async response
    }
});
