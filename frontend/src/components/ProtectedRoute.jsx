import { useContext } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function ProtectedRoute({ children, requireAdmin = false }) {
    const { user, isAuthenticated, loading } = useContext(AuthContext);
    const location = useLocation();

    if (loading) {
        return <div>Loading authentication...</div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    if (requireAdmin && user?.role !== "admin") {
        return (
            <div className="dashboard">
                <h1>Access Denied</h1>
                <p>You need administrator privileges to view this page.</p>
                <Navigate to="/scan" replace />
            </div>
        );
    }

    return children;
}
