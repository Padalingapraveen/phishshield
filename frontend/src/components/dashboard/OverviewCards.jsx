export default function OverviewCards({ overview }) {
    if (!overview) return null;

    const highRiskThreats = (overview.risk_distribution?.critical || 0) + (overview.risk_distribution?.high || 0);

    return (
        <div className="stats-grid" style={{ marginTop: "0", marginBottom: "24px" }}>
            <div className="glass-card">
                <div className="stat-card-header">Total Analyzed</div>
                <div className="stat-card-value">{overview.total_events.toLocaleString()}</div>
                <div className="stat-card-subtitle">Processed by pipeline</div>
            </div>

            <div className="glass-card" style={{ borderTop: "3px solid var(--status-danger)" }}>
                <div className="stat-card-header">Phishing Detected</div>
                <div className="stat-card-value">{overview.phishing_events.toLocaleString()}</div>
                <div className="stat-card-subtitle" style={{ color: "var(--status-danger)" }}>
                    {overview.phishing_percentage}% detection rate
                </div>
            </div>

            <div className="glass-card" style={{ borderTop: "3px solid var(--status-safe)" }}>
                <div className="stat-card-header">Safe Emails</div>
                <div className="stat-card-value">{overview.non_phishing_events.toLocaleString()}</div>
                <div className="stat-card-subtitle" style={{ color: "var(--status-safe)" }}>
                    {overview.non_phishing_percentage}% clean rate
                </div>
            </div>

            <div className="glass-card" style={{ borderTop: "3px solid var(--status-warning)" }}>
                <div className="stat-card-header">High Risk Threats</div>
                <div className="stat-card-value">{highRiskThreats.toLocaleString()}</div>
                <div className="stat-card-subtitle">Critical & High combined</div>
            </div>

            <div className="glass-card" style={{ gridColumn: "span 2" }}>
                <div className="stat-card-header">Average Risk Score</div>
                <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                    <div className="stat-card-value" style={{ margin: 0 }}>{overview.average_risk_score.toFixed(1)}%</div>
                    <div style={{ flex: 1, height: "6px", background: "var(--bg-base)", borderRadius: "999px", overflow: "hidden" }}>
                        <div style={{ 
                            width: `${overview.average_risk_score}%`, 
                            height: "100%", 
                            background: overview.average_risk_score > 60 ? "var(--status-danger)" : overview.average_risk_score > 40 ? "var(--status-warning)" : "var(--status-safe)",
                            transition: "width 1s ease"
                        }}></div>
                    </div>
                </div>
                <div className="stat-card-subtitle" style={{ marginTop: "8px" }}>Network-wide average risk assessment</div>
            </div>
        </div>
    );
}
