import { Link, useLocation } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../../context/AuthContext";

export default function Sidebar() {
    const location = useLocation();
    const { user } = useContext(AuthContext);

    return (
        <aside className="soc-sidebar">
            <div className="sidebar-header">
                PhishGuard SOC
            </div>

            <div className="sidebar-nav">
                
                <div className="sidebar-section-title">Main</div>
                <Link to="/" className={`nav-item ${location.pathname === "/" ? "active" : ""}`}>
                    Dashboard Overview
                </Link>

                <div className="sidebar-section-title">Detection</div>
                <Link to="/scan" className={`nav-item ${location.pathname === "/scan" ? "active" : ""}`}>
                    Email Scanner
                </Link>
                <Link to="/history" className={`nav-item ${location.pathname === "/history" ? "active" : ""}`}>
                    Detection History
                </Link>
                <Link to="/extension" className={`nav-item ${location.pathname === "/extension" ? "active" : ""}`}>
                    Extension Sync
                </Link>

                <div className="sidebar-section-title">Security Analytics</div>
                <Link to="/reports" className={`nav-item ${location.pathname === "/reports" ? "active" : ""}`}>
                    Threat Reports
                </Link>

                <div className="sidebar-section-title">System</div>
                <Link to="/health" className={`nav-item ${location.pathname === "/health" ? "active" : ""}`}>
                    System Health
                </Link>
                <Link to="/settings" className={`nav-item ${location.pathname === "/settings" ? "active" : ""}`}>
                    Settings
                </Link>

                {user?.role === "admin" && (
                    <>
                        <div className="sidebar-section-title">Administration</div>
                        <Link to="/admin" className={`nav-item ${location.pathname === "/admin" ? "active" : ""}`}>
                            Admin Console
                        </Link>
                        <Link to="/performance" className={`nav-item ${location.pathname === "/performance" ? "active" : ""}`}>
                            Model Performance
                        </Link>
                    </>
                )}
            </div>
        </aside>
    );
}
