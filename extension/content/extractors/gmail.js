class GmailExtractor {
    static extract() {
        // Gmail DOM Selectors
        let sender = "";
        let receiver = "";
        let subject = "";
        let body = "";

        try {
            // Subject: typically an h2 with data-thread-perm-id or class hP
            const subjectEl = document.querySelector('h2.hP');
            if (subjectEl) subject = subjectEl.innerText.trim();

            // Sender: usually an element with class gD (has email attribute)
            const senderEl = document.querySelector('.gD');
            if (senderEl) {
                sender = senderEl.getAttribute('email') || senderEl.innerText.trim();
            }

            // Receiver: class g2 or span with dir="ltr"
            const receiverEl = document.querySelector('.g2 span');
            if (receiverEl) {
                receiver = receiverEl.getAttribute('email') || receiverEl.innerText.trim();
            }

            // Body: div with dir="ltr" usually holds the main email body
            // Alternative: class 'a3s aiL'
            const bodyEls = document.querySelectorAll('.a3s.aiL');
            if (bodyEls && bodyEls.length > 0) {
                // Get the last one in case of threaded emails
                body = bodyEls[bodyEls.length - 1].innerText.trim();
            }
        } catch (e) {
            console.error("GmailExtractor error:", e);
        }

        return { sender, receiver, subject, body };
    }
}
window.GmailExtractor = GmailExtractor;
