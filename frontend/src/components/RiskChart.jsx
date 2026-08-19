import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend
} from "recharts";


export default function RiskChart({ data }) {

    if (!data) {

        return (

            <div className="risk-chart">

                <h3>
                    Risk Distribution
                </h3>

                <p>
                    Loading...
                </p>

            </div>
        );
    }


    const labels =
        Array.isArray(data.labels)
            ? data.labels
            : [];


    const values =
        Array.isArray(data.values)
            ? data.values
            : [];


    const chartData =
        labels.map((label, index) => ({

            name: label,

            value:
                Number(values[index] ?? 0)

        }));


    const total =
        chartData.reduce(
            (sum, item) =>
                sum + item.value,
            0
        );


    return (

        <div className="risk-chart">

            <h3>
                Risk Distribution
            </h3>


            {total === 0 ? (

                <p>
                    No risk events recorded.
                </p>

            ) : (

                <ResponsiveContainer
                    width="100%"
                    height={300}
                >

                    <PieChart>

                        <Pie
                            data={chartData}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            label
                        >

                            {chartData.map(
                                (entry, index) => (

                                    <Cell
                                        key={`risk-${index}`}
                                    />

                                )
                            )}

                        </Pie>


                        <Tooltip />


                        <Legend />

                    </PieChart>

                </ResponsiveContainer>

            )}

        </div>
    );
}