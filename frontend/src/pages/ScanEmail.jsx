import { useState } from "react";
import { predictEmail } from "../services/api";

export default function ScanEmail() {

    const [sender, setSender] = useState("");
    const [receiver, setReceiver] = useState("");
    const [subject, setSubject] = useState("");
    const [body, setBody] = useState("");

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    async function handleScan(e) {
        e.preventDefault();

        setLoading(true);
        setResult(null);
        setError("");

        try {
            const data = await predictEmail({
                sender,
                receiver,
                subject,
                body
            });
            setResult(data);
        } catch (err) {
            console.error("Scan error:", err);
            setError(err.message || "Prediction failed. Check console or API.");
        } finally {
            setLoading(false);
        }
    }

    function getRiskClass(level) {
        return `badge-${String(level || "LOW").toLowerCase()}`;
    }

    return (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "32px", height: "calc(100vh - 140px)" }}>
            
            {/* Left Column: Input Form */}
            <div className="glass-card" style={{ display: "flex", flexDirection: "column", height: "100%" }}>
                <div style={{ borderBottom: "1px solid var(--border-subtle)", paddingBottom: "16px", marginBottom: "24px" }}>
                    <h2 style={{ fontSize: "18px", margin: 0 }}>Email Input Workspace</h2>
                    <p style={{ color: "var(--text-secondary)", fontSize: "14px", margin: "4px 0 0 0" }}>Enter raw email data for DistilBERT + GAT inference.</p>
                </div>

                <form onSubmit={handleScan} style={{ flex: 1, display: "flex", flexDirection: "column", gap: "16px", overflowY: "auto", paddingRight: "8px" }}>
                    
                    <div className="form-group" style={{ margin: 0 }}>
                        <label className="form-label">Sender Address</label>
                        <input
                            type="email"
                            className="input-field"
                            placeholder="attacker@malicious.com"
                            value={sender}
                            onChange={(e) => setSender(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group" style={{ margin: 0 }}>
                        <label className="form-label">Receiver Address</label>
                        <input
                            type="email"
                            className="input-field"
                            placeholder="employee@company.com"
                            value={receiver}
                            onChange={(e) => setReceiver(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group" style={{ margin: 0 }}>
                        <label className="form-label">Subject</label>
                        <input
                            type="text"
                            className="input-field"
                            placeholder="URGENT: Password Reset Required"
                            value={subject}
                            onChange={(e) => setSubject(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group" style={{ margin: 0, flex: 1, display: "flex", flexDirection: "column" }}>
                        <label className="form-label">Email Body & URLs</label>
                        <textarea
                            className="textarea-field"
                            placeholder="Please click here to reset your password..."
                            style={{ flex: 1, resize: "none" }}
                            value={body}
                            onChange={(e) => setBody(e.target.value)}
                            required
                        ></textarea>
                    </div>

                    {error && (
                        <div className="error-box" style={{ margin: 0 }}>
                            {error}
                        </div>
                    )}

                    <div style={{ marginTop: "8px", paddingTop: "16px", borderTop: "1px solid var(--border-subtle)" }}>
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={loading}
                            style={{ width: "100%", padding: "12px", fontSize: "16px" }}
                        >
                            {loading ? "Running Neural Network Inference..." : "Analyze Email"}
                        </button>
                    </div>
                </form>
            </div>

            {/* Right Column: AI Detection Result */}
            <div className="glass-card" style={{ display: "flex", flexDirection: "column", height: "100%", overflowY: "auto", background: "rgba(15, 23, 42, 0.8)" }}>
                <div style={{ borderBottom: "1px solid var(--border-subtle)", paddingBottom: "16px", marginBottom: "24px" }}>
                    <h2 style={{ fontSize: "18px", margin: 0 }}>AI Detection Result</h2>
                    <p style={{ color: "var(--text-secondary)", fontSize: "14px", margin: "4px 0 0 0" }}>Real-time model evaluation and explainability.</p>
                </div>

                {!result && !loading && (
                    <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", flexDirection: "column", gap: "16px" }}>
                        <div style={{ fontSize: "48px", opacity: 0.2 }}>🤖</div>
                        Waiting for email input...
                    </div>
                )}

                {loading && (
                    <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--brand-primary)", flexDirection: "column", gap: "16px" }}>
                        <div className="spinner" style={{ width: "40px", height: "40px", border: "3px solid rgba(59, 130, 246, 0.3)", borderTopColor: "var(--brand-primary)", borderRadius: "50%", animation: "spin 1s linear infinite" }}></div>
                        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
                        Computing DistilBERT embeddings...
                    </div>
                )}

                {result && !loading && (
                    <div style={{ animation: "slideIn 0.3s ease" }}>
                        
                        <div style={{ textAlign: "center", padding: "32px 0", borderBottom: "1px solid var(--border-subtle)", marginBottom: "24px" }}>
                            <div style={{ fontSize: "14px", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "8px" }}>Prediction</div>
                            {result.predicted_class === 1 ? (
                                <div style={{ fontSize: "36px", fontWeight: "800", color: "var(--status-danger)", letterSpacing: "0.05em", textShadow: "0 0 20px rgba(239, 68, 68, 0.3)" }}>PHISHING</div>
                            ) : (
                                <div style={{ fontSize: "36px", fontWeight: "800", color: "var(--status-safe)", letterSpacing: "0.05em", textShadow: "0 0 20px rgba(16, 185, 129, 0.3)" }}>SAFE</div>
                            )}
                            <div style={{ marginTop: "16px" }}>
                                <span className={`badge ${getRiskClass(result.risk_level)}`} style={{ padding: "6px 16px", fontSize: "14px" }}>
                                    {result.risk_level} RISK
                                </span>
                            </div>
                        </div>

                        <div className="result-grid" style={{ marginTop: 0 }}>
                            <div className="result-item">
                                <strong>Risk Score</strong>
                                <span>{Number(result.risk_score).toFixed(1)}</span>
                            </div>

                            <div className="result-item">
                                <strong>Phishing Prob.</strong>
                                <span>{(result.phishing_probability * 100).toFixed(1)}%</span>
                            </div>

                            <div className="result-item">
                                <strong>Clean Prob.</strong>
                                <span>{(result.non_phishing_probability * 100).toFixed(1)}%</span>
                            </div>

                            <div className="result-item">
                                <strong>Graph Neighbors</strong>
                                <span>{result.graph_neighbors}</span>
                            </div>
                        </div>

                        <div style={{ marginTop: "32px", padding: "20px", background: "rgba(59, 130, 246, 0.05)", border: "1px solid rgba(59, 130, 246, 0.2)", borderRadius: "var(--radius-md)" }}>
                            <h3 style={{ fontSize: "14px", color: "var(--brand-primary)", marginTop: 0, marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Detection Explanation</h3>
                            <p style={{ color: "var(--text-secondary)", fontSize: "14px", lineHeight: 1.6, margin: 0 }}>
                                {result.predicted_class === 1 
                                    ? `This email exhibits structural and semantic similarities to known phishing campaigns. The Graph Attention Network identified ${result.graph_neighbors} related malicious entities in the reference graph.`
                                    : `This email's DistilBERT embeddings strongly align with benign corporate communication patterns. No significant malicious graph neighbor relationships were detected.`
                                }
                            </p>
                        </div>

                        <div style={{ marginTop: "24px", fontSize: "12px", color: "var(--text-muted)", textAlign: "center" }}>
                            Event ID: {result.event_id || "Live Scan"} &bull; Timestamp: {new Date().toLocaleTimeString()}
                        </div>
                    </div>
                )}
            </div>

        </div>
    );
}