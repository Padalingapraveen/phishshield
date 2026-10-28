import { useState, useEffect } from "react";
import { generateReport } from "../services/api";

export default function Reports() {
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);
    const [days, setDays] = useState(7);
    const [error, setError] = useState("");

    async function loadReport() {
        setLoading(true);
        setError("");
        try {
            const data = await generateReport(days);
            setReport(data);
        } catch (err) {
            setError(err.message || "Failed to generate report.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadReport();
    }, [days]);

    const handleDownload = () => {
        if (!report) return;
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href",     dataStr);
        downloadAnchorNode.setAttribute("download", `phishguard_report_${days}days.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    const handleCSVDownload = () => {
        if (!report) return;
        const headers = ["Period", "Total Scans", "Phishing Detected", "Safe Emails", "Detection Rate (%)"];
        const row = [report.period, report.total_scans, report.phishing_detected, report.safe_emails, report.detection_rate];
        const csvContent = "data:text/csv;charset=utf-8," + headers.join(",") + "\n" + row.join(",");
        
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", encodeURI(csvContent));
        downloadAnchorNode.setAttribute("download", `phishguard_report_${days}days.csv`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    return (
        <div>
            <div className="glass-card" style={{ marginBottom: "24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                    <h1 style={{ fontSize: "24px", marginBottom: "8px" }}>Threat Reports</h1>
                    <p style={{ color: "var(--text-secondary)", margin: 0 }}>Generate summary analytics over a specific period.</p>
                </div>
                <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                    <select 
                        value={days} 
                        onChange={(e) => setDays(Number(e.target.value))}
                        className="input-field" 
                        style={{ width: "150px" }}
                    >
                        <option value={1}>Last 24 Hours</option>
                        <option value={7}>Last 7 Days</option>
                        <option value={30}>Last 30 Days</option>
                    </select>
                    <button className="btn btn-secondary" onClick={handleDownload} disabled={!report || loading}>
                        Export JSON
                    </button>
                    <button className="btn btn-primary" onClick={handleCSVDownload} disabled={!report || loading}>
                        Export CSV
                    </button>
                </div>
            </div>

            {error && <div className="error-box">{error}</div>}

            {loading ? (
                <div style={{ padding: "32px", color: "var(--text-muted)" }}>Generating Report...</div>
            ) : report ? (
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
                    <div className="glass-card">
                        <h3 style={{ borderBottom: "1px solid var(--border-subtle)", paddingBottom: "12px", marginBottom: "16px" }}>Report Summary ({report.period})</h3>
                        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "var(--text-muted)" }}>Total Scans</span>
                                <span style={{ fontWeight: "600" }}>{report.total_scans}</span>
                            </div>
                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "var(--text-muted)" }}>Phishing Detected</span>
                                <span style={{ fontWeight: "600", color: "var(--status-danger)" }}>{report.phishing_detected}</span>
                            </div>
                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "var(--text-muted)" }}>Safe Emails</span>
                                <span style={{ fontWeight: "600", color: "var(--status-safe)" }}>{report.safe_emails}</span>
                            </div>
                            <div style={{ display: "flex", justifyContent: "space-between", borderTop: "1px solid var(--border-subtle)", paddingTop: "16px" }}>
                                <span style={{ color: "var(--text-primary)" }}>Detection Rate</span>
                                <span style={{ fontWeight: "700" }}>{report.detection_rate}%</span>
                            </div>
                        </div>
                    </div>
                </div>
            ) : null}
        </div>
    );
}
