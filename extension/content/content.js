// Main dispatcher
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extract_email") {
        let data = { sender: "", receiver: "", subject: "", body: "" };
        
        try {
            if (window.location.hostname.includes("mail.google.com")) {
                data = window.GmailExtractor.extract();
            } else {
                data = window.GenericExtractor.extract();
            }
        } catch (e) {
            console.error("Extraction failed", e);
        }
        
        sendResponse({ success: true, data: data });
    }
    return true; // keep channel open for async response
});
