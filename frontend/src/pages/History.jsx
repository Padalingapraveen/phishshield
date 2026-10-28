import { useState, useEffect } from "react";
import { getEvents } from "../services/api";
import ThreatTable from "../components/dashboard/ThreatTable";
import ThreatDetailPanel from "../components/dashboard/ThreatDetailPanel";

export default function History() {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const limit = 10;

    useEffect(() => {
        async function fetchHistory() {
            setLoading(true);
            try {
                const data = await getEvents(limit, (page - 1) * limit);
                setEvents(data);
                setHasMore(data.length === limit);
            } catch (err) {
                setError(err.message || "Failed to load history.");
            } finally {
                setLoading(false);
            }
        }
        fetchHistory();
    }, [page]);



    if (error) {
        return <div className="error-box">{error}</div>;
    }

    return (
        <div>
            <div style={{ marginBottom: "24px" }}>
                <h1 style={{ fontSize: "24px", marginBottom: "8px" }}>Detection History</h1>
                <p style={{ color: "var(--text-secondary)", margin: 0 }}>Showing your email scans and their threat classifications.</p>
            </div>

            <ThreatTable events={events} onRowClick={setSelectedEvent} loading={loading} />
            
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "24px" }}>
                <button 
                    className="btn btn-secondary" 
                    disabled={page === 1 || loading}
                    onClick={() => setPage(p => p - 1)}
                >
                    Previous Page
                </button>
                <span style={{ color: "var(--text-secondary)", fontSize: "14px" }}>Page {page}</span>
                <button 
                    className="btn btn-secondary" 
                    disabled={!hasMore || loading}
                    onClick={() => setPage(p => p + 1)}
                >
                    Next Page
                </button>
            </div>

            {selectedEvent && (
                <ThreatDetailPanel event={selectedEvent} onClose={() => setSelectedEvent(null)} />
            )}
        </div>
    );
}
