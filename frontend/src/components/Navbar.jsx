import { Link, useLocation, useNavigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

export default function Navbar() {
    const location = useLocation();
    const navigate = useNavigate();
    const { user, isAuthenticated, logout } = useContext(AuthContext);

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <nav className="navbar">
            <div className="container">
                <div className="navbar-brand">
                    <Link to="/">PhishGuard AI</Link>
                </div>

                <div className="navbar-links">
                    {user?.role === "admin" && (
                        <Link
                            to="/"
                            className={location.pathname === "/" ? "active" : ""}
                        >
                            Dashboard
                        </Link>
                    )}

                    {isAuthenticated && (
                        <Link
                            to="/scan"
                            className={location.pathname === "/scan" ? "active" : ""}
                        >
                            Scan Email
                        </Link>
                    )}

                    {isAuthenticated ? (
                        <div style={{ display: "flex", alignItems: "center", gap: "16px", marginLeft: "16px" }}>
                            <span style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                                {user?.username} <span style={{opacity: 0.5}}>({user?.role})</span>
                            </span>
                            <button onClick={handleLogout} className="btn btn-secondary">
                                Logout
                            </button>
                        </div>
                    ) : (
                        <Link to="/login" className={location.pathname === "/login" ? "active" : ""}>
                            Login
                        </Link>
                    )}
                </div>
            </div>
        </nav>
    );
}