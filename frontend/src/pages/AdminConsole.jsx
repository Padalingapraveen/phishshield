import { useState, useEffect } from "react";
import { getUsers } from "../services/api";

export default function AdminConsole() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function load() {
            try {
                const data = await getUsers();
                setUsers(data);
            } catch (err) {
                setError(err.message || "Failed to load users. Are you an admin?");
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    if (loading) return <div style={{ padding: "32px", color: "var(--text-muted)" }}>Loading Users...</div>;

    return (
        <div>
            <div style={{ marginBottom: "24px" }}>
                <h1 style={{ fontSize: "24px", marginBottom: "8px" }}>Admin Console</h1>
                <p style={{ color: "var(--text-secondary)", margin: 0 }}>Manage users and role-based access.</p>
            </div>
            
            {error && <div className="error-box" style={{ marginBottom: "24px" }}>{error}</div>}

            {!error && (
                <div className="glass-card" style={{ padding: 0, overflow: "hidden" }}>
                    <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--border-subtle)" }}>
                        <h3 style={{ margin: 0, fontSize: "16px" }}>Registered Users</h3>
                    </div>
                    <table className="detection-table" style={{ marginTop: 0 }}>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Username</th>
                                <th>Role</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(u => (
                                <tr key={u.id}>
                                    <td>{u.id}</td>
                                    <td>{u.username}</td>
                                    <td>
                                        {u.role === "admin" ? (
                                            <span className="badge badge-critical">ADMIN</span>
                                        ) : (
                                            <span className="badge badge-safe">USER</span>
                                        )}
                                    </td>
                                    <td>
                                        {u.is_active ? (
                                            <span style={{ color: "var(--status-safe)", fontSize: "12px", fontWeight: "600" }}>Active</span>
                                        ) : (
                                            <span style={{ color: "var(--status-danger)", fontSize: "12px", fontWeight: "600" }}>Disabled</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
