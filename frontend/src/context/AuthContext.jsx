import { createContext, useState, useEffect } from "react";
import * as api from "../services/api";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const checkAuth = async () => {
        try {
            // Fetch /auth/me to verify the HttpOnly cookie or Bearer token is valid
            const token = localStorage.getItem("access_token");
            const response = await fetch(`${api.API_BASE_URL}/auth/me`, {
                credentials: "include",
                headers: token ? { "Authorization": `Bearer ${token}` } : {}
            });
            if (response.ok) {
                const userData = await response.json();
                setUser({
                    username: userData.username,
                    role: userData.role,
                });
            } else {
                setUser(null);
            }
        } catch (error) {
            console.error("Auth check failed", error);
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkAuth();
    }, []);

    const login = async () => {
        await checkAuth(); // Refresh user state after successful login cookie is set
    };

    const logout = async () => {
        try {
            await api.logout();
        } catch (error) {
            console.error("Logout API failed", error);
        } finally {
            localStorage.removeItem("access_token");
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
}
