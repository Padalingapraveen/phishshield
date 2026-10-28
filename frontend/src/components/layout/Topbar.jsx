import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/AuthContext";
import { getHealth } from "../../services/api";

export default function Topbar({ pageTitle = "Dashboard" }) {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();
    const [health, setHealth] = useState("checking");

    useEffect(() => {
        async function checkHealth() {
            try {
                await getHealth();
                setHealth("healthy");
            } catch (e) {
                setHealth("offline");
            }
        }
        checkHealth();
        const interval = setInterval(checkHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <header className="soc-topbar">
            <div>
                <h2 style={{ margin: 0, fontSize: "18px" }}>{pageTitle}</h2>
            </div>

            <div className="topbar-actions">
                <div className="search-bar">
                    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <input type="text" placeholder="Search events, IP, hash..." />
                </div>

                <div className="status-indicator" title="Predictor API Status">
                    <div className={`status-dot ${health === "offline" ? "offline" : ""}`}></div>
                    {health === "healthy" ? "API Online" : health === "offline" ? "API Offline" : "Checking..."}
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "16px", paddingLeft: "16px", borderLeft: "1px solid var(--border-subtle)" }}>
                    <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: "14px", fontWeight: "600", color: "var(--text-primary)" }}>{user?.username}</div>
                        <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase" }}>{user?.role}</div>
                    </div>
                    
                    <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: "12px" }}>
                        Logout
                    </button>
                </div>
            </div>
        </header>
    );
}
