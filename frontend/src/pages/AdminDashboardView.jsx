import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import OverviewCards from "../components/dashboard/OverviewCards";
import ThreatAnalytics from "../components/dashboard/ThreatAnalytics";
import ThreatDetailPanel from "../components/dashboard/ThreatDetailPanel";
import EmptyState from "../components/EmptyState";

import {
    getDashboardOverview,
    getRiskDistribution,
    getDistribution,
    getTimeline
} from "../services/api";

export default function AdminDashboardView() {
    const { logout } = useContext(AuthContext);
    const [overview, setOverview] = useState(null);
    const [riskDistribution, setRiskDistribution] = useState(null);
    const [distribution, setDistribution] = useState(null);
    const [timeline, setTimeline] = useState([]);
    const [selectedEvent, setSelectedEvent] = useState(null);
    
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState("");

    function getThreatLevel(score) {
        if (score >= 80) return "CRITICAL";
        if (score >= 60) return "HIGH";
        if (score >= 47) return "MEDIUM";
        return "LOW";
    }

    function getThreatColor(score) {
        if (score >= 80) return "var(--status-critical)";
        if (score >= 60) return "var(--status-danger)";
        if (score >= 47) return "var(--status-warning)";
        return "var(--status-safe)";
    }

    async function loadDashboard(showLoading = false) {
        try {
            if (showLoading) setLoading(true);
            setRefreshing(true);
            setError("");

            const [overviewData, timelineData, distData, riskData] = await Promise.all([
                getDashboardOverview(),
                getTimeline(24),
                getDistribution(),
                getRiskDistribution()
            ]);

            setOverview(overviewData);
            setTimeline(Array.isArray(timelineData) ? timelineData : []);
            setDistribution(distData);
            setRiskDistribution(riskData);

        } catch (err) {
            console.error("Dashboard loading error:", err);
            
            // Handle unauthorized access
            if (err.message && (err.message.includes("401") || err.message.includes("403") || err.message.includes("Unauthorized"))) {
                logout();
                return;
            }

            setError(err.message || "Unable to load dashboard data.");
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }

    useEffect(() => {
        loadDashboard(true);
    }, []);

    if (loading) {
            return (
                <div>
                    <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "24px" }}>
                        <div className="skeleton skeleton-text short" style={{ width: "120px", height: "36px", margin: 0, borderRadius: "var(--radius-sm)" }}></div>
                    </div>
                    
                    <div className="skeleton skeleton-card" style={{ height: "80px", marginBottom: "24px" }}></div>
                    
                    <div className="stats-grid" style={{ marginTop: 0, marginBottom: "24px" }}>
                        <div className="skeleton skeleton-card"></div>
                        <div className="skeleton skeleton-card"></div>
                        <div className="skeleton skeleton-card"></div>
                        <div className="skeleton skeleton-card"></div>
                    </div>
                    
                    <div className="content-grid" style={{ marginTop: 0, marginBottom: "24px" }}>
                        <div className="skeleton skeleton-chart"></div>
                        <div className="skeleton skeleton-chart" style={{ gridColumn: "span 2" }}></div>
                    </div>
                </div>
            );
        }

    if (error && !overview) {
        return (
            <div style={{ padding: "40px" }}>
                <EmptyState 
                    icon={
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--status-danger)" strokeWidth="2">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                    }
                    title="Connection Error"
                    description={error}
                    actionButton={<button className="btn btn-primary" onClick={() => loadDashboard(true)}>Retry Connection</button>}
                />
            </div>
        );
    }

    return (
        <div>
            <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "24px" }}>
                <button
                    className="btn btn-primary"
                    onClick={() => loadDashboard(false)}
                    disabled={refreshing}
                >
                    {refreshing ? "Refreshing..." : "Refresh Data"}
                </button>
            </div>

            {error && <div className="error-box">{error}</div>}

            {overview && (
                <div className="glass-card" style={{ marginBottom: "24px", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 24px", borderLeft: `4px solid ${getThreatColor(overview.average_risk_score)}` }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
                        <div>
                            <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "4px" }}>Current Threat Level</div>
                            <div style={{ fontSize: "24px", fontWeight: "700", color: getThreatColor(overview.average_risk_score) }}>
                                {getThreatLevel(overview.average_risk_score)}
                            </div>
                        </div>
                        <div style={{ height: "40px", width: "1px", background: "var(--border-subtle)" }}></div>
                        <div style={{ display: "flex", gap: "24px" }}>
                            <div>
                                <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>Total Threats</div>
                                <div style={{ fontSize: "18px", fontWeight: "600" }}>{overview.phishing_events}</div>
                            </div>
                            <div>
                                <div style={{ fontSize: "12px", color: "var(--status-critical)" }}>Critical</div>
                                <div style={{ fontSize: "18px", fontWeight: "600" }}>{overview.risk_distribution?.critical || 0}</div>
                            </div>
                            <div>
                                <div style={{ fontSize: "12px", color: "var(--status-danger)" }}>High</div>
                                <div style={{ fontSize: "18px", fontWeight: "600" }}>{overview.risk_distribution?.high || 0}</div>
                            </div>
                            <div>
                                <div style={{ fontSize: "12px", color: "var(--status-warning)" }}>Medium</div>
                                <div style={{ fontSize: "18px", fontWeight: "600" }}>{overview.risk_distribution?.medium || 0}</div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <OverviewCards overview={overview} />
            
            <ThreatAnalytics 
                riskData={riskDistribution} 
                distributionData={distribution} 
                timelineData={timeline} 
            />

            {selectedEvent && (
                <ThreatDetailPanel event={selectedEvent} onClose={() => setSelectedEvent(null)} />
            )}


        </div>
    );
}
