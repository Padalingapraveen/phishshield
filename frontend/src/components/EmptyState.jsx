export default function EmptyState({ title, description, icon, actionButton, compact = false }) {
    return (
        <div style={{ 
            display: "flex", 
            flexDirection: "column", 
            alignItems: "center", 
            justifyContent: "center", 
            height: compact ? "100%" : "60vh",
            padding: compact ? "40px 20px" : "20px",
            textAlign: "center"
        }}>
            <div style={{ 
                width: "64px", 
                height: "64px", 
                borderRadius: "50%", 
                background: "rgba(148, 163, 184, 0.1)", 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "center",
                fontSize: "24px",
                color: "var(--text-muted)",
                marginBottom: "24px"
            }}>
                {icon || (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                )}
            </div>
            <h2 style={{ fontSize: "20px", marginBottom: "8px", color: "var(--text-primary)" }}>{title}</h2>
            <p style={{ color: "var(--text-secondary)", maxWidth: "400px", lineHeight: "1.6", marginBottom: actionButton ? "24px" : "0" }}>
                {description || "No data available."}
            </p>
            {actionButton}
        </div>
    );
}
