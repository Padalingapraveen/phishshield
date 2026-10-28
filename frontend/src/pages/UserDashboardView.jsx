import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import OverviewCards from "../components/dashboard/OverviewCards";
import ThreatAnalytics from "../components/dashboard/ThreatAnalytics";
import ThreatDetailPanel from "../components/dashboard/ThreatDetailPanel";
import EmptyState from "../components/EmptyState";
import { getEvents } from "../services/api";

export default function UserDashboardView() {
    const { logout } = useContext(AuthContext);
    const [overview, setOverview] = useState(null);
    const [riskDistribution, setRiskDistribution] = useState(null);
    const [distribution, setDistribution] = useState(null);
    const [timeline, setTimeline] = useState([]);
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadDashboard = async () => {
        try {
            setLoading(true);
            setError("");
            
            const events = await getEvents(100, 0);

            const total = events.length;
            let phishing = 0;
            let safe = 0;
            let sumRisk = 0;
            const riskCounts = { critical: 0, high: 0, medium: 0, low: 0 };
            
            const timelineMap = {};
            const now = new Date();
            for(let i=0; i<24; i++) {
                const d = new Date(now - i * 60 * 60 * 1000);
                const k = d.toISOString().substring(0, 13) + ":00";
                timelineMap[k] = { hour: k, total: 0, phishing: 0, non_phishing: 0 };
            }

            events.forEach(e => {
                if (e.predicted_class === 1) phishing++;
                else safe++;

                sumRisk += e.risk_score;

                if (e.risk_score >= 80) riskCounts.critical++;
                else if (e.risk_score >= 60) riskCounts.high++;
                else if (e.risk_score >= 47) riskCounts.medium++;
                else riskCounts.low++;

                const k = e.timestamp.substring(0, 13) + ":00";
                if (timelineMap[k]) {
                    timelineMap[k].total++;
                    if (e.predicted_class === 1) timelineMap[k].phishing++;
                    else timelineMap[k].non_phishing++;
                }
            });

            const avgRisk = total > 0 ? sumRisk / total : 0;

            setOverview({
                total_events: total,
                phishing_events: phishing,
                non_phishing_events: safe,
                average_risk_score: avgRisk,
                risk_distribution: riskCounts
            });

            setDistribution({
                labels: ["Phishing", "Non-Phishing"],
                values: [phishing, safe]
            });

            setRiskDistribution({
                labels: ["Critical", "High", "Medium", "Low"],
                values: [riskCounts.critical, riskCounts.high, riskCounts.medium, riskCounts.low]
            });

            const sortedTimeline = Object.values(timelineMap).sort((a, b) => a.hour.localeCompare(b.hour));
            setTimeline(sortedTimeline);

        } catch (err) {
            // Handle unauthorized access
            if (err.message && (err.message.includes("401") || err.message.includes("403") || err.message.includes("Unauthorized"))) {
                logout();
                return;
            }
            setError(err.message || "Unable to load personal dashboard data.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadDashboard();
    }, []);

    if (loading) {
            return (
                <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
                        <h1 style={{ fontSize: "24px", margin: 0 }}>My Dashboard</h1>
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

    if (error) {
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
                    actionButton={<button className="btn btn-primary" onClick={() => loadDashboard()}>Retry Connection</button>}
                />
            </div>
        );
    }

    if (overview && overview.total_events === 0) {
        return (
            <div style={{ padding: "40px" }}>
                <EmptyState 
                    title="Welcome to PhishGuard AI"
                    description="No scans yet. Submit an email to get started and see your personal metrics here."
                    icon={
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                            <polyline points="22,6 12,13 2,6"></polyline>
                        </svg>
                    }
                />
            </div>
        );
    }

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

    return (
        <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
                <h1 style={{ fontSize: "24px", margin: 0 }}>My Dashboard</h1>
                <button className="btn btn-primary" onClick={() => loadDashboard()}>Refresh Data</button>
            </div>
            
            {overview && (
                <div className="glass-card" style={{ marginBottom: "24px", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 24px", borderLeft: `4px solid ${getThreatColor(overview.average_risk_score)}` }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
                        <div>
                            <div style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "4px" }}>Average Risk Level</div>
                            <div style={{ fontSize: "24px", fontWeight: "700", color: getThreatColor(overview.average_risk_score) }}>
                                {getThreatLevel(overview.average_risk_score)}
                            </div>
                        </div>
                        <div style={{ height: "40px", width: "1px", background: "var(--border-subtle)" }}></div>
                        <div style={{ display: "flex", gap: "24px" }}>
                            <div>
                                <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>My Total Scans</div>
                                <div style={{ fontSize: "18px", fontWeight: "600" }}>{overview.total_events}</div>
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
