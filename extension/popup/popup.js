document.addEventListener("DOMContentLoaded", () => {
    const loginSection = document.getElementById("login-section");
    const mainSection = document.getElementById("main-section");
    const analyzeBtn = document.getElementById("analyze-btn");
    const loginBtn = document.getElementById("login-btn");
    const logoutBtn = document.getElementById("logout-btn");
    const loadingDiv = document.getElementById("loading");
    const errorDiv = document.getElementById("error");
    const loginErrorDiv = document.getElementById("login-error");
    const resultDiv = document.getElementById("result");

    // Check initial auth state
    chrome.runtime.sendMessage({ action: "check_auth" }, (response) => {
        if (response && response.authorized) {
            showMain();
        } else {
            showLogin();
        }
    });

    function showLogin() {
        loginSection.classList.remove("hidden");
        mainSection.classList.add("hidden");
    }

    function showMain() {
        loginSection.classList.add("hidden");
        mainSection.classList.remove("hidden");
        errorDiv.classList.add("hidden");
        resultDiv.classList.add("hidden");
    }

    loginBtn.addEventListener("click", () => {
        const user = document.getElementById("login-username").value;
        const pass = document.getElementById("login-password").value;
        loginBtn.disabled = true;
        loginErrorDiv.classList.add("hidden");

        chrome.runtime.sendMessage({ action: "login", username: user, password: pass }, (res) => {
            loginBtn.disabled = false;
            if (res && res.success) {
                showMain();
            } else {
                loginErrorDiv.textContent = res ? res.error : "Login failed";
                loginErrorDiv.classList.remove("hidden");
            }
        });
    });

    logoutBtn.addEventListener("click", () => {
        chrome.runtime.sendMessage({ action: "logout" }, () => {
            showLogin();
        });
    });

    analyzeBtn.addEventListener("click", async () => {
        // Reset UI
        errorDiv.classList.add("hidden");
        resultDiv.classList.add("hidden");
        loadingDiv.classList.remove("hidden");
        analyzeBtn.disabled = true;

        try {
            // Get current active tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // Execute extractor content script manually if needed or just send message
            chrome.tabs.sendMessage(tab.id, { action: "extract_email" }, (response) => {
                if (chrome.runtime.lastError) {
                    showError("Could not connect to the page. Please refresh or make sure it's an email page.");
                    return;
                }

                if (response && response.success) {
                    const emailData = response.data;
                    
                    // Send to backend via background script
                    chrome.runtime.sendMessage(
                        { action: "predict", data: emailData }, 
                        (apiResponse) => {
                            if (apiResponse && apiResponse.success) {
                                renderResult(apiResponse.result);
                            } else {
                                if (apiResponse && apiResponse.error && apiResponse.error.includes("Session expired")) {
                                    showLogin();
                                } else {
                                    showError(apiResponse ? apiResponse.error : "Unknown error connecting to backend.");
                                }
                            }
                        }
                    );
                } else {
                    showError("Failed to extract email data from this page.");
                }
            });
        } catch (e) {
            showError("An unexpected error occurred.");
        }
    });

    function showError(msg) {
        loadingDiv.classList.add("hidden");
        errorDiv.textContent = msg;
        errorDiv.classList.remove("hidden");
        analyzeBtn.disabled = false;
    }

    function renderResult(data) {
        loadingDiv.classList.add("hidden");
        analyzeBtn.disabled = false;
        
        // Label
        const badge = document.getElementById("classification-badge");
        if (data.label === "PHISHING" || data.predicted_class === 1) {
            badge.textContent = "PHISHING";
            badge.className = "badge phishing";
        } else {
            badge.textContent = "NON-PHISHING";
            badge.className = "badge safe";
        }

        // Stats
        document.getElementById("val-prob").textContent = (data.phishing_probability * 100).toFixed(2) + "%";
        document.getElementById("val-score").textContent = data.risk_score.toFixed(1);
        document.getElementById("val-level").textContent = data.risk_level;
        document.getElementById("val-neighbors").textContent = data.graph_neighbors || 0;

        // Details
        document.getElementById("val-sender-entity").textContent = data.sender_entity ? data.sender_entity.substring(0, 20) : "N/A";
        document.getElementById("val-receiver-entity").textContent = data.receiver_entity ? data.receiver_entity.substring(0, 20) : "N/A";

        resultDiv.classList.remove("hidden");
    }
});
