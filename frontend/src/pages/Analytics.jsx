import EmptyState from "../components/EmptyState";

export default function Analytics() {
    return (
        <div>
            <div style={{ marginBottom: "24px" }}>
                <h1 style={{ fontSize: "24px", marginBottom: "8px" }}>Security Analytics</h1>
                <p style={{ color: "var(--text-secondary)", margin: 0 }}>Deep dive into detection statistics and risk analysis.</p>
            </div>
            <div className="glass-card">
                <EmptyState 
                    title="Analytics Data Unavailable" 
                    icon="📊"
                    description="Advanced analytics metrics such as Precision, Recall, F1 Score, and ROC-AUC are not dynamically tracked or exposed by the production database. N/A."
                />
            </div>
        </div>
    );
}
