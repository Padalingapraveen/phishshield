import { useState } from "react";
import { predictEmail } from "../services/api";

export default function ScanEmail() {
    const [form, setForm] = useState({
        sender: "",
        receiver: "",
        subject: "",
        body: ""
    });

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    function handleChange(e) {
        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    }

    async function handleSubmit(e) {
        e.preventDefault();

        setLoading(true);
        setError("");
        setResult(null);

        try {
            const data = await predictEmail({
                sender: form.sender,
                receiver: form.receiver,
                subject: form.subject,
                body: form.body
            });

            setResult(data);

        } catch (err) {
            console.error("Prediction error:", err);

            setError(
                err.message || "Prediction failed"
            );

        } finally {
            setLoading(false);
        }
    }

    function formatProbability(value) {
        return (
            Number(value || 0) * 100
        ).toFixed(2);
    }

    function formatRiskScore(value) {
        return Number(value || 0).toFixed(2);
    }

    function getRiskClass(level) {
        return `risk-${String(level || "LOW").toLowerCase()}`;
    }

    return (
        <div className="scan-page">

            <h1>Scan Email</h1>

            <p>
                Analyze an email using
                DistilBERT + Graph Attention Network.
            </p>

            {/* ================================
                EMAIL FORM
            ================================= */}

            <form
                className="scan-form"
                onSubmit={handleSubmit}
            >

                <input
                    type="text"
                    name="sender"
                    placeholder="Sender"
                    value={form.sender}
                    onChange={handleChange}
                    required
                />

                <input
                    type="email"
                    name="receiver"
                    placeholder="Receiver"
                    value={form.receiver}
                    onChange={handleChange}
                    required
                />

                <input
                    type="text"
                    name="subject"
                    placeholder="Subject"
                    value={form.subject}
                    onChange={handleChange}
                    required
                />

                <textarea
                    name="body"
                    placeholder="Email body"
                    value={form.body}
                    onChange={handleChange}
                    rows="10"
                    required
                />

                <button
                    type="submit"
                    disabled={loading}
                >
                    {loading
                        ? "Analyzing..."
                        : "Scan Email"
                    }
                </button>

            </form>

            {/* ================================
                ERROR
            ================================= */}

            {error && (
                <div className="error-box">
                    {error}
                </div>
            )}

            {/* ================================
                RESULT
            ================================= */}

            {result && (
                <div className="prediction-result">

                    <h2>
                        Detection Result
                    </h2>

                    {/* Classification */}

                    <div className="result-item">
                        <strong>
                            Classification:
                        </strong>

                        <span
                            className={
                                result.predicted_class === 1
                                    ? "classification-phishing"
                                    : "classification-safe"
                            }
                        >
                            {result.label}
                        </span>
                    </div>

                    {/* Predicted class */}

                    <div className="result-item">
                        <strong>
                            Predicted Class:
                        </strong>

                        <span>
                            {result.predicted_class}
                        </span>
                    </div>

                    {/* Threshold */}

                    <div className="result-item">
                        <strong>
                            Classification Threshold:
                        </strong>

                        <span>
                            {(
                                Number(
                                    result.classification_threshold
                                ) * 100
                            ).toFixed(0)}%
                        </span>
                    </div>

                    {/* Phishing probability */}

                    <div className="result-item">
                        <strong>
                            Phishing Probability:
                        </strong>

                        <span>
                            {formatProbability(
                                result.phishing_probability
                            )}%
                        </span>
                    </div>

                    {/* Non phishing probability */}

                    <div className="result-item">
                        <strong>
                            Non-Phishing Probability:
                        </strong>

                        <span>
                            {formatProbability(
                                result.non_phishing_probability
                            )}%
                        </span>
                    </div>

                    {/* Risk score */}

                    <div className="result-item">
                        <strong>
                            Risk Score:
                        </strong>

                        <span>
                            {formatRiskScore(
                                result.risk_score
                            )}%
                        </span>
                    </div>

                    {/* Backend risk level */}

                    <div className="result-item">
                        <strong>
                            Risk Level:
                        </strong>

                        <span
                            className={
                                getRiskClass(
                                    result.risk_level
                                )
                            }
                        >
                            {result.risk_level}
                        </span>
                    </div>

                    {/* Graph neighbors */}

                    <div className="result-item">
                        <strong>
                            Graph Neighbors:
                        </strong>

                        <span>
                            {result.graph_neighbors ?? 0}
                        </span>
                    </div>

                    {/* Sender */}

                    <div className="result-item">
                        <strong>
                            Sender Entity:
                        </strong>

                        <span>
                            {result.sender_entity || "-"}
                        </span>
                    </div>

                    {/* Receiver */}

                    <div className="result-item">
                        <strong>
                            Receiver Entity:
                        </strong>

                        <span>
                            {result.receiver_entity || "-"}
                        </span>
                    </div>

                    {/* Domains */}

                    <div className="result-item">
                        <strong>
                            Domains:
                        </strong>

                        <span>
                            {result.domain_entities?.length
                                ? result.domain_entities.join(", ")
                                : "-"
                            }
                        </span>
                    </div>

                    {/* Graph edge types */}

                    <div className="result-item">
                        <strong>
                            Graph Edge Types:
                        </strong>

                        <span>
                            {result.graph_edge_types?.length
                                ? result.graph_edge_types.join(", ")
                                : "-"
                            }
                        </span>
                    </div>

                </div>
            )}

        </div>
    );
}