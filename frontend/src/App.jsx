import {
    BrowserRouter,
    Routes,
    Route
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import ScanEmail from "./pages/ScanEmail";
import Login from "./pages/Login";
import Register from "./pages/Register";
import History from "./pages/History";
import ExtensionSync from "./pages/ExtensionSync";
import Reports from "./pages/Reports";
import SystemHealth from "./pages/SystemHealth";
import Settings from "./pages/Settings";
import AdminConsole from "./pages/AdminConsole";
import ModelPerformance from "./pages/ModelPerformance";

import Layout from "./components/layout/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";

export default function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />

                    <Route path="/" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
                    <Route path="/scan" element={<ProtectedRoute><Layout><ScanEmail /></Layout></ProtectedRoute>} />
                    <Route path="/history" element={<ProtectedRoute><Layout><History /></Layout></ProtectedRoute>} />
                    <Route path="/extension" element={<ProtectedRoute><Layout><ExtensionSync /></Layout></ProtectedRoute>} />
                    <Route path="/reports" element={<ProtectedRoute><Layout><Reports /></Layout></ProtectedRoute>} />
                    <Route path="/health" element={<ProtectedRoute><Layout><SystemHealth /></Layout></ProtectedRoute>} />
                    <Route path="/settings" element={<ProtectedRoute><Layout><Settings /></Layout></ProtectedRoute>} />
                    <Route path="/admin" element={<ProtectedRoute requireAdmin={true}><Layout><AdminConsole /></Layout></ProtectedRoute>} />
                    <Route path="/performance" element={<ProtectedRoute requireAdmin={true}><Layout><ModelPerformance /></Layout></ProtectedRoute>} />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}