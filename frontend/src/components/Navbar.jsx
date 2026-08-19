import { Link, useLocation } from "react-router-dom";

export default function Navbar() {

    const location = useLocation();

    return (
        <nav className="navbar">

            <div className="navbar-brand">
                <Link to="/">
                    PhishGuard AI
                </Link>
            </div>

            <div className="navbar-links">

                <Link
                    to="/"
                    className={
                        location.pathname === "/"
                            ? "active"
                            : ""
                    }
                >
                    Dashboard
                </Link>

                <Link
                    to="/scan"
                    className={
                        location.pathname === "/scan"
                            ? "active"
                            : ""
                    }
                >
                    Scan Email
                </Link>

            </div>

        </nav>
    );
}