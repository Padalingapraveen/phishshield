import { useEffect, useState } from "react";

import StatCard from "../components/StatCard";
import RiskChart from "../components/RiskChart";
import DetectionTable from "../components/DetectionTable";
import RecentEvents from "../components/RecentEvents";
import TimelineChart from "../components/TimelineChart";

import {
    getDashboardOverview,
    getRecentEvents,
    getRiskDistribution,
    getTimeline
} from "../services/api";


export default function Dashboard() {

    const [overview, setOverview] = useState(null);
    const [events, setEvents] = useState([]);
    const [riskDistribution, setRiskDistribution] = useState(null);
    const [timeline, setTimeline] = useState([]);

    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState("");


    async function loadDashboard(showLoading = false) {

        try {

            if (showLoading) {
                setLoading(true);
            }

            setRefreshing(true);
            setError("");

            const [
                overviewData,
                eventsData,
                riskData,
                timelineData
            ] = await Promise.all([

                getDashboardOverview(),

                getRecentEvents(10),

                getRiskDistribution(),

                getTimeline(24)

            ]);


            setOverview(
                overviewData
            );

            setEvents(
                Array.isArray(eventsData)
                    ? eventsData
                    : []
            );

            setRiskDistribution(
                riskData
            );

            setTimeline(
                Array.isArray(timelineData)
                    ? timelineData
                    : []
            );

        } catch (err) {

            console.error(
                "Dashboard loading error:",
                err
            );

            setError(
                err.message ||
                "Unable to load dashboard data."
            );

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
            <div className="dashboard">

                <h1>
                    PhishGuard Dashboard
                </h1>

                <p>
                    Loading real SOC data...
                </p>

            </div>
        );
    }


    if (error && !overview) {

        return (
            <div className="dashboard">

                <h1>
                    PhishGuard Dashboard
                </h1>

                <div className="error-box">
                    {error}
                </div>

                <button
                    onClick={() =>
                        loadDashboard(true)
                    }
                >
                    Retry
                </button>

            </div>
        );
    }


    return (

        <div className="dashboard">

            {/* ==================================================
                HEADER
            ================================================== */}

            <div className="dashboard-header">

                <div>

                    <h1>
                        PhishGuard Dashboard
                    </h1>

                    <p>
                        Real-time phishing detection
                        and SOC monitoring
                    </p>

                </div>


                <button
                    onClick={() =>
                        loadDashboard(false)
                    }
                    disabled={refreshing}
                >

                    {refreshing
                        ? "Refreshing..."
                        : "Refresh"
                    }

                </button>

            </div>


            {error && (

                <div className="error-box">
                    {error}
                </div>

            )}


            {/* ==================================================
                STATISTICS
            ================================================== */}

            <div className="stats-grid">

                <StatCard
                    title="Total Scans"
                    value={
                        overview?.total_events ?? 0
                    }
                    subtitle="Total analyzed emails"
                />


                <StatCard
                    title="Average Risk"
                    value={
                        `${Number(
                            overview?.average_risk_score ?? 0
                        ).toFixed(2)}%`
                    }
                    subtitle="Average detection risk"
                />


                <StatCard
                    title="Phishing Detected"
                    value={
                        overview?.phishing_events ?? 0
                    }
                    subtitle={
                        `${Number(
                            overview?.phishing_percentage ?? 0
                        ).toFixed(2)}% of scans`
                    }
                />


                <StatCard
                    title="Non-Phishing"
                    value={
                        overview?.non_phishing_events ?? 0
                    }
                    subtitle={
                        `${Number(
                            overview?.non_phishing_percentage ?? 0
                        ).toFixed(2)}% of scans`
                    }
                />

            </div>


            {/* ==================================================
                RISK + RECENT EVENTS
            ================================================== */}

            <div className="content-grid">

                <RiskChart
                    data={riskDistribution}
                />


                <RecentEvents
                    events={events}
                />

            </div>


            {/* ==================================================
                TIMELINE
            ================================================== */}

            <TimelineChart
                data={timeline}
            />


            {/* ==================================================
                DETECTION TABLE
            ================================================== */}

            <DetectionTable
                events={events}
            />

        </div>
    );
}

