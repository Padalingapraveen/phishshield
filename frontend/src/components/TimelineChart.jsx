import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend
} from "recharts";

export default function TimelineChart({ data = [] }) {

    const chartData = data.map((item) => ({
        hour: item.hour ?? "",
        phishing: Number(item.phishing ?? 0),
        non_phishing: Number(item.non_phishing ?? 0)
    }));

    return (
        <div className="timeline-chart">

            <div className="chart-header">
                <h3>Detection Timeline</h3>
                <span>Last 24 Hours</span>
            </div>

            {chartData.length === 0 ? (

                <div className="empty-chart">
                    <p>No detection activity recorded.</p>
                </div>

            ) : (

                <ResponsiveContainer
                    width="100%"
                    height={350}
                >
                    <LineChart
                        data={chartData}
                        margin={{
                            top: 10,
                            right: 20,
                            left: 0,
                            bottom: 10
                        }}
                    >

                        <CartesianGrid
                            strokeDasharray="3 3"
                        />

                        <XAxis
                            dataKey="hour"
                            tick={{ fontSize: 12 }}
                        />

                        <YAxis
                            allowDecimals={false}
                            tick={{ fontSize: 12 }}
                        />

                        <Tooltip
                            formatter={(value, name) => [
                                value,
                                name === "phishing"
                                    ? "Phishing"
                                    : "Non-Phishing"
                            ]}
                        />

                        <Legend />

                        <Line
                            type="monotone"
                            dataKey="phishing"
                            name="Phishing"
                            dot={{ r: 3 }}
                            activeDot={{ r: 6 }}
                        />

                        <Line
                            type="monotone"
                            dataKey="non_phishing"
                            name="Non-Phishing"
                            dot={{ r: 3 }}
                            activeDot={{ r: 6 }}
                        />

                    </LineChart>
                </ResponsiveContainer>

            )}

        </div>
    );
}