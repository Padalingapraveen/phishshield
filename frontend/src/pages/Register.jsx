import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register } from "../services/api";

export default function Register() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            setLoading(false);
            return;
        }

        try {
            await register(username, password);
            navigate("/login", { replace: true });
        } catch (err) {
            setError(err.message || "Registration failed.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="glass-card login-card">
                <h1>Sign Up</h1>
                <p style={{ textAlign: "center", color: "var(--text-secondary)", marginBottom: "24px" }}>
                    Create a new PhishGuard AI account
                </p>

                {error && <div className="error-box">{error}</div>}

                <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                    <div className="form-group">
                        <label className="form-label">Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            className="input-field"
                            placeholder="username"
                        />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="input-field"
                            placeholder="••••••••"
                        />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Confirm Password</label>
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            className="input-field"
                            placeholder="••••••••"
                        />
                    </div>
                    <button type="submit" disabled={loading} className="btn btn-primary" style={{ marginTop: "8px" }}>
                        {loading ? "Creating account..." : "Register"}
                    </button>
                    <div style={{ textAlign: "center", marginTop: "16px", color: "var(--text-secondary)" }}>
                        Already have an account? <Link to="/login" style={{ color: "var(--brand-primary)", textDecoration: "none" }}>Sign In</Link>
                    </div>
                </form>
            </div>
        </div>
    );
}
