export default function ThreatDetailPanel({ event, onClose }) {
    if (!event) return null;

    const probabilityStr = (event.phishing_probability * 100).toFixed(2);
    const nonProbabilityStr = (event.non_phishing_probability * 100).toFixed(2);

    return (
        <div className="side-panel-overlay" onClick={onClose}>
            <div className="side-panel" onClick={(e) => e.stopPropagation()}>
                <div className="side-panel-header">
                    <h2 style={{ margin: 0, fontSize: "18px" }}>Threat Analysis Detail</h2>
                    <button onClick={onClose} style={{ background: "transparent", border: "none", color: "var(--text-secondary)", fontSize: "24px", cursor: "pointer" }}>&times;</button>
                </div>

                <div className="side-panel-content">
                    {/* Header Info */}
                    <div style={{ marginBottom: "24px" }}>
                        <div style={{ fontSize: "24px", fontWeight: "700", marginBottom: "8px" }}>
                            {event.predicted_class === 1 ? <span style={{ color: "var(--status-danger)" }}>PHISHING DETECTED</span> : <span style={{ color: "var(--status-safe)" }}>CLEAN EMAIL</span>}
                        </div>
                        <div style={{ color: "var(--text-secondary)", fontSize: "14px" }}>
                            Detected at {new Date(event.timestamp.endsWith('Z') ? event.timestamp : event.timestamp + 'Z').toLocaleString()}
                        </div>
                    </div>

                    {/* Email Headers */}
                    <div className="detail-section glass-card" style={{ padding: "16px" }}>
                        <h3>Email Metadata</h3>
                        <div style={{ display: "grid", gap: "12px", fontSize: "14px" }}>
                            <div>
                                <strong style={{ color: "var(--text-secondary)" }}>Sender:</strong>
                                <div style={{ wordBreak: "break-all" }}>{event.sender}</div>
                            </div>
                            <div>
                                <strong style={{ color: "var(--text-secondary)" }}>Receiver:</strong>
                                <div style={{ wordBreak: "break-all" }}>{event.receiver}</div>
                            </div>
                            <div>
                                <strong style={{ color: "var(--text-secondary)" }}>Subject:</strong>
                                <div>{event.subject}</div>
                            </div>
                        </div>
                    </div>

                    {/* ML Metrics */}
                    <div className="detail-section glass-card" style={{ padding: "16px" }}>
                        <h3>ML Pipeline Metrics</h3>
                        
                        <div style={{ marginBottom: "16px" }}>
                            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                                <span style={{ color: "var(--text-secondary)", fontSize: "14px" }}>Phishing Probability (DistilBERT + GAT)</span>
                                <strong>{probabilityStr}%</strong>
                            </div>
                            <div className="bar">
                                <div className="bar-fill high" style={{ width: `${probabilityStr}%` }}></div>
                            </div>
                        </div>

                        <div style={{ marginBottom: "16px" }}>
                            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                                <span style={{ color: "var(--text-secondary)", fontSize: "14px" }}>Clean Probability</span>
                                <strong>{nonProbabilityStr}%</strong>
                            </div>
                            <div className="bar">
                                <div className="bar-fill low" style={{ width: `${nonProbabilityStr}%` }}></div>
                            </div>
                        </div>

                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginTop: "24px" }}>
                            <div>
                                <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase" }}>Risk Score</div>
                                <div style={{ fontSize: "24px", fontWeight: "600" }}>{Number(event.risk_score).toFixed(1)}</div>
                            </div>
                            <div>
                                <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase" }}>Graph Neighbors</div>
                                <div style={{ fontSize: "24px", fontWeight: "600" }}>{event.graph_neighbors}</div>
                            </div>
                        </div>
                    </div>

                    {/* AI Detection Section */}
                    <div className="detail-section glass-card" style={{ padding: "16px", background: "rgba(59, 130, 246, 0.05)", border: "1px solid rgba(59, 130, 246, 0.2)" }}>
                        <h3 style={{ color: "var(--brand-primary)" }}>AI Analysis Summary</h3>
                        <p style={{ fontSize: "14px", lineHeight: 1.6, color: "var(--text-secondary)", margin: 0 }}>
                            This email was processed through the <strong>DistilBERT</strong> embedding layer and analyzed contextually via the <strong>Graph Attention Network (GAT)</strong> against historical threat patterns.
                            <br/><br/>
                            {event.predicted_class === 1 
                                ? `The model classified this as highly suspicious with a risk score of ${Number(event.risk_score).toFixed(1)}. It shares graph proximity with ${event.graph_neighbors} known nodes.`
                                : `The model determined this email is safe. The structural and semantic embeddings matched benign baselines with ${nonProbabilityStr}% confidence.`
                            }
                        </p>
                    </div>

                </div>
            </div>
        </div>
    );
}
