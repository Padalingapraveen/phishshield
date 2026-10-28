import { useState, useEffect } from "react";
import { getExtensionStatus, toggleExtension } from "../services/api";

export default function ExtensionSync() {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    async function load() {
        try {
            const data = await getExtensionStatus();
            setStatus(data);
        } catch (err) {
            setError(err.message || "Failed to load extension status.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        load();
    }, []);

    const handleToggle = async () => {
        try {
            const data = await toggleExtension();
            setStatus(data);
        } catch (err) {
            alert(err.message || "Failed to toggle extension access.");
        }
    };

    if (loading) return <div style={{ padding: "32px", color: "var(--text-muted)" }}>Loading Extension Status...</div>;

    return (
        <div>
            <div className="glass-card" style={{ marginBottom: "24px" }}>
                <h1 style={{ fontSize: "28px", fontWeight: "700", marginBottom: "8px" }}>Extension Integration</h1>
                <p style={{ color: "var(--text-secondary)", fontSize: "15px" }}>Manage connection policies for the Chrome Extension</p>
            </div>

            {error && <div className="error-box" style={{ marginBottom: "24px" }}>{error}</div>}

            {status && (
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
                    <div className="glass-card" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
                        <div>
                            <h3 style={{ margin: "0 0 8px 0" }}>Connection Status</h3>
                            <div style={{ display: "flex", alignItems: "center", gap: "12px", marginTop: "12px" }}>
                                <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: status.enabled ? "var(--status-safe)" : "var(--status-danger)" }}></div>
                                <span style={{ fontSize: "16px", fontWeight: "600" }}>{status.enabled ? "Active / Listening" : "Disabled"}</span>
                            </div>
                        </div>
                        
                        <div>
                            <h3 style={{ margin: "0 0 12px 0", fontSize: "14px", color: "var(--text-secondary)" }}>Access Control</h3>
                            <button 
                                className={`btn ${status.enabled ? "btn-danger" : "btn-primary"}`} 
                                onClick={handleToggle}
                            >
                                {status.enabled ? "Disable Extension Access" : "Enable Extension Access"}
                            </button>
                        </div>
                    </div>

                    <div className="glass-card">
                        <h3 style={{ margin: "0 0 16px 0", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "12px" }}>Extension Traffic</h3>
                        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "var(--text-muted)" }}>Total Scans Submitted</span>
                                <span style={{ fontWeight: "600", fontSize: "18px" }}>{status.total_scans}</span>
                            </div>
                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "var(--text-muted)" }}>Last Connected</span>
                                <span style={{ fontWeight: "600" }}>
                                    {status.last_connected 
                                        ? new Date(status.last_connected).toLocaleString() 
                                        : "Never"}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
