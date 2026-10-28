class GenericExtractor {
    static extract() {
        let sender = "";
        let receiver = "";
        let subject = "";
        let body = "";

        try {
            // Very generic fallbacks
            subject = document.title;
            
            // Just return the body text for now
            const bodyEl = document.querySelector('body');
            if (bodyEl) {
                body = bodyEl.innerText.trim().substring(0, 5000); // limit to first 5000 chars
            }
        } catch (e) {
            console.error("GenericExtractor error:", e);
        }

        return { sender, receiver, subject, body };
    }
}
window.GenericExtractor = GenericExtractor;
