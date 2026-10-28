import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

export default function Settings() {
    const { user } = useContext(AuthContext);

    return (
        <div>
            <div style={{ marginBottom: "24px" }}>
                <h1 style={{ fontSize: "24px", marginBottom: "8px" }}>Settings</h1>
                <p style={{ color: "var(--text-secondary)", margin: 0 }}>Manage your profile and dashboard preferences.</p>
            </div>

            <div className="glass-card" style={{ maxWidth: "600px", marginBottom: "24px" }}>
                <h2 style={{ fontSize: "18px", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "16px", marginBottom: "24px" }}>Profile Information</h2>
                
                <div style={{ display: "grid", gap: "20px" }}>
                    <div>
                        <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "4px" }}>Username</div>
                        <div style={{ fontSize: "16px", fontWeight: "500" }}>{user?.username || "Unknown"}</div>
                    </div>
                    <div>
                        <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "4px" }}>Role</div>
                        <span className={`badge ${user?.role === 'admin' ? 'badge-high' : 'badge-safe'}`}>{user?.role || "user"}</span>
                    </div>
                </div>
            </div>

            <div className="glass-card" style={{ maxWidth: "600px", opacity: 0.7 }}>
                <h2 style={{ fontSize: "18px", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "16px", marginBottom: "24px" }}>Dashboard Preferences</h2>
                <div style={{ fontSize: "14px", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                    User-specific settings (like theme overrides, default analytics period, and custom notification webhooks) are not currently persisted by the database. 
                    <br/><br/>
                    The UI uses the global <strong>Deep Slate</strong> theme by default.
                </div>
            </div>
        </div>
    );
}
