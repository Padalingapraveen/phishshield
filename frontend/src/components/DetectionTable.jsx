export default function DetectionTable({ events = [] }) {

    function getRisk(riskScore) {

    const score = Number(riskScore) || 0;

    if (score >= 80) {
        return "Critical";
    }

    if (score >= 60) {
        return "High";
    }

    if (score >= 47) {
        return "Medium";
    }

    return "Low";
}


    function getStatus(predictedClass) {

        return Number(predictedClass) === 1
            ? "Blocked"
            : "Allowed";
    }


    return (

        <div className="detection-table">

            <div className="table-header">

                <div>

                    <h3>
                        Recent Detections
                    </h3>

                    <p>
                        Latest emails analyzed by
                        DistilBERT + GAT
                    </p>

                </div>


                <span className="event-count">

                    {events.length} events

                </span>

            </div>


            {events.length === 0 ? (

                <div className="empty-table">

                    <p>
                        No detections available.
                    </p>

                </div>

            ) : (

                <div className="table-wrapper">

                    <table>

                        <thead>

                            <tr>

                                <th>
                                    Email
                                </th>

                                <th>
                                    Subject
                                </th>

                                <th>
                                    Risk
                                </th>

                                <th>
                                    Probability
                                </th>

                                <th>
                                    Status
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            {events.map((event) => {

                                const risk =
                                    getRisk(event);


                                const status =
                                    getStatus(
                                        event.predicted_class
                                    );


                                const probability =
                                    (
                                        Number(
                                            event.phishing_probability ?? 0
                                        ) * 100
                                    ).toFixed(2);


                                return (

                                    <tr
                                        key={event.id}
                                    >

                                        <td
                                            title={
                                                event.sender
                                            }
                                        >
                                            {
                                                event.sender ||
                                                "-"
                                            }
                                        </td>


                                        <td
                                            title={
                                                event.subject
                                            }
                                        >
                                            {
                                                event.subject ||
                                                "-"
                                            }
                                        </td>


                                        <td>

                                            <span
                                                className={
                                                    `risk-badge risk-${risk.toLowerCase()}`
                                                }
                                            >
                                                {risk}
                                            </span>


                                            <span className="risk-score">

                                                {" "}

                                                {Number(
                                                    event.risk_score ?? 0
                                                ).toFixed(2)}

                                                %

                                            </span>

                                        </td>


                                        <td>

                                            {probability}%

                                        </td>


                                        <td>

                                            <span
                                                className={
                                                    `status-badge status-${status.toLowerCase()}`
                                                }
                                            >
                                                {status}
                                            </span>

                                        </td>

                                    </tr>

                                );

                            })}

                        </tbody>

                    </table>

                </div>

            )}

        </div>
    );
}