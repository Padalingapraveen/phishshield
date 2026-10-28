import { useState, useEffect } from "react";
import { getHealth } from "../services/api";

export default function SystemHealth() {
    const [healthData, setHealthData] = useState({
        api: "checking",
        predictor: "checking",
        database: "checking",
        extension: "checking"
    });
    const [lastChecked, setLastChecked] = useState("");

    useEffect(() => {
        async function check() {
            try {
                const data = await getHealth();
                setHealthData({
                    api: data.api || "online",
                    predictor: data.predictor || "online",
                    database: data.database || "online",
                    extension: data.extension || "online"
                });
            } catch (e) {
                setHealthData({
                    api: "offline",
                    predictor: "offline",
                    database: "offline",
                    extension: "offline"
                });
            }
            setLastChecked(new Date().toLocaleTimeString());
        }
        check();
        const interval = setInterval(check, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div>
            <div style={{ marginBottom: "24px" }}>
                <h1 style={{ fontSize: "24px", marginBottom: "8px" }}>System Health</h1>
                <p style={{ color: "var(--text-secondary)", margin: 0 }}>Enterprise SOC infrastructure monitoring.</p>
            </div>

            <div className="content-grid">
                
                <div className="glass-card">
                    <h3 style={{ fontSize: "16px", marginBottom: "16px", color: "var(--text-primary)" }}>API Gateway</h3>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Status</span>
                        {healthData.api === "online" ? (
                            <span className="badge badge-safe">ONLINE</span>
                        ) : healthData.api === "offline" ? (
                            <span className="badge badge-critical">OFFLINE</span>
                        ) : (
                            <span className="badge badge-medium">CHECKING</span>
                        )}
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "12px" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Last Checked</span>
                        <span style={{ fontSize: "14px", fontWeight: "500" }}>{lastChecked || "..."}</span>
                    </div>
                </div>

                <div className="glass-card">
                    <h3 style={{ fontSize: "16px", marginBottom: "16px", color: "var(--text-primary)" }}>ML Inference Engine</h3>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Predictor Status</span>
                        {healthData.predictor === "online" ? (
                            <span className="badge badge-safe">LOADED</span>
                        ) : healthData.predictor === "offline" ? (
                            <span className="badge badge-critical">UNREACHABLE</span>
                        ) : (
                            <span className="badge badge-medium">CHECKING</span>
                        )}
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "12px" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Active Models</span>
                        <span style={{ fontSize: "14px", fontWeight: "500" }}>DistilBERT, GAT</span>
                    </div>
                </div>

                <div className="glass-card">
                    <h3 style={{ fontSize: "16px", marginBottom: "16px", color: "var(--text-primary)" }}>Database</h3>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Connection</span>
                        {healthData.database === "online" ? (
                            <span className="badge badge-safe">ONLINE</span>
                        ) : healthData.database === "offline" ? (
                            <span className="badge badge-critical">OFFLINE</span>
                        ) : (
                            <span className="badge badge-medium">CHECKING</span>
                        )}
                    </div>
                </div>

                <div className="glass-card">
                    <h3 style={{ fontSize: "16px", marginBottom: "16px", color: "var(--text-primary)" }}>Chrome Extension</h3>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Sync Status</span>
                        {healthData.extension === "online" ? (
                            <span className="badge badge-safe">ONLINE</span>
                        ) : healthData.extension === "offline" ? (
                            <span className="badge badge-critical">OFFLINE</span>
                        ) : (
                            <span className="badge badge-medium">CHECKING</span>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
