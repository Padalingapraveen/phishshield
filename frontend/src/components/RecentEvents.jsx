export default function RecentEvents({ events = [] }) {

    return (

        <div className="recent-events">

            <h3>
                Recent Events
            </h3>


            {events.length === 0 ? (

                <p>
                    No detection events yet.
                </p>

            ) : (

                <ul>

                    {events.map((event) => (

                        <li key={event.id}>

                            <div>

                                <strong>
                                    {event.label}
                                </strong>

                                <p>
                                    {event.subject ||
                                        "No subject"}
                                </p>

                            </div>


                            <span>

                                {Number(
                                    event.risk_score ?? 0
                                ).toFixed(2)}%

                            </span>

                        </li>

                    ))}

                </ul>

            )}

        </div>
    );
}