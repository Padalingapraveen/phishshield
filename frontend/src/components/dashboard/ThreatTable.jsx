import EmptyState from "../EmptyState";

export default function ThreatTable({ events, onRowClick, loading = false }) {
    
    if (loading) {
        return (
            <div className="glass-card" style={{ padding: "0", overflow: "hidden" }}>
                <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--border-subtle)" }}>
                    <div className="skeleton skeleton-text medium" style={{ margin: 0 }}></div>
                </div>
                <div style={{ padding: "24px" }}>
                    {[1, 2, 3, 4, 5].map(i => (
                        <div key={i} className="skeleton skeleton-table-row"></div>
                    ))}
                </div>
            </div>
        );
    }

    if (!events || events.length === 0) {
        return (
            <div className="glass-card" style={{ padding: 0 }}>
                <EmptyState 
                    title="No recent threats"
                    description="There are no recent detection events to display at this time."
                    compact={true}
                />
            </div>
        );
    }

    const getRiskBadge = (level) => {
        const lower = String(level).toLowerCase();
        return <span className={`badge badge-${lower}`}>{level}</span>;
    };

    return (
        <div className="glass-card" style={{ padding: "0", overflow: "hidden" }}>
            <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--border-subtle)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3 style={{ margin: 0, fontSize: "16px" }}>Recent Detections</h3>
            </div>
            <div className="detection-table-wrapper" style={{ overflowX: "auto" }}>
                <table className="detection-table" style={{ marginTop: 0 }}>
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Sender</th>
                            <th>Subject</th>
                            <th>Prediction</th>
                            <th>Risk</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {events.map(event => (
                            <tr 
                                key={event.id} 
                                onClick={() => onRowClick && onRowClick(event)}
                                style={{ cursor: "pointer" }}
                            >
                                <td>{new Date(event.timestamp.endsWith('Z') ? event.timestamp : event.timestamp + 'Z').toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                                <td style={{ maxWidth: "150px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={event.sender}>{event.sender}</td>
                                <td style={{ maxWidth: "250px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={event.subject}>{event.subject}</td>
                                <td>
                                    {event.predicted_class === 1 
                                        ? <span className="badge badge-phishing">PHISHING</span> 
                                        : <span className="badge badge-safe">SAFE</span>}
                                </td>
                                <td>{getRiskBadge(event.risk_level)}</td>
                                <td>{Number(event.risk_score).toFixed(1)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
