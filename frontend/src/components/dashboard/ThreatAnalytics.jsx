import { 
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
    BarChart, Bar, Cell,
    PieChart, Pie
} from 'recharts';

export default function ThreatAnalytics({ riskData, distributionData, timelineData }) {
    
    // Format timeline data for Recharts
    const chartData = timelineData?.map(item => ({
        time: item.hour.split(' ')[1], // Get just the time e.g. "14:00"
        total: item.total,
        phishing: item.phishing,
        safe: item.non_phishing
    })) || [];

    // Format risk data for BarChart
    const riskColors = {
        "Critical": "var(--status-critical)",
        "High": "var(--status-danger)",
        "Medium": "var(--status-warning)",
        "Low": "var(--status-safe)"
    };
    
    const riskChartData = riskData?.labels?.map((label, i) => ({
        name: label,
        value: riskData.values[i]
    })) || [];

    // Format distribution data for PieChart
    const distChartData = distributionData?.labels?.map((label, i) => ({
        name: label,
        value: distributionData.values[i]
    })) || [];
    const distColors = {
        "Phishing": "var(--status-danger)",
        "Non-Phishing": "var(--status-safe)"
    };

    // Custom Tooltip for Timeline
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div style={{ backgroundColor: "rgba(15, 23, 42, 0.9)", border: "1px solid var(--border-strong)", padding: "12px", borderRadius: "8px", boxShadow: "0 4px 12px rgba(0,0,0,0.5)" }}>
                    <p style={{ margin: "0 0 8px 0", fontWeight: "600", color: "var(--text-primary)" }}>{label}</p>
                    <p style={{ margin: 0, color: "var(--status-danger)", fontSize: "13px" }}>Phishing: {payload[0].value}</p>
                    <p style={{ margin: 0, color: "var(--status-safe)", fontSize: "13px" }}>Safe: {payload[1].value}</p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="content-grid" style={{ marginBottom: "24px" }}>
            
            {/* Risk Distribution Bar Chart */}
            <div className="glass-card" style={{ display: "flex", flexDirection: "column" }}>
                <h3 style={{ fontSize: "16px", marginBottom: "24px", color: "var(--text-primary)" }}>Risk Distribution</h3>
                <div style={{ flex: 1, minHeight: "250px" }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={riskChartData} layout="vertical" margin={{ top: 0, right: 30, left: 0, bottom: 0 }}>
                            <XAxis type="number" hide />
                            <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: 'var(--text-secondary)', fontSize: 13 }} width={70} />
                            <RechartsTooltip 
                                cursor={{ fill: 'rgba(255,255,255,0.05)' }} 
                                contentStyle={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border-strong)', borderRadius: '8px' }}
                                itemStyle={{ color: 'var(--text-primary)' }}
                            />
                            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
                                {riskChartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={riskColors[entry.name] || 'var(--brand-primary)'} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Distribution Pie Chart */}
            <div className="glass-card" style={{ display: "flex", flexDirection: "column" }}>
                <h3 style={{ fontSize: "16px", marginBottom: "24px", color: "var(--text-primary)" }}>Threat Distribution</h3>
                <div style={{ flex: 1, minHeight: "250px" }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={distChartData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {distChartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={distColors[entry.name] || 'var(--brand-primary)'} />
                                ))}
                            </Pie>
                            <RechartsTooltip 
                                contentStyle={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border-strong)', borderRadius: '8px' }}
                                itemStyle={{ color: 'var(--text-primary)' }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
                <div style={{ display: "flex", justifyContent: "center", gap: "16px", marginTop: "16px", fontSize: "12px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <div style={{ width: "10px", height: "10px", borderRadius: "2px", background: "var(--status-danger)" }}></div>
                        <span style={{ color: "var(--text-secondary)" }}>Phishing</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <div style={{ width: "10px", height: "10px", borderRadius: "2px", background: "var(--status-safe)" }}></div>
                        <span style={{ color: "var(--text-secondary)" }}>Non-Phishing</span>
                    </div>
                </div>
            </div>

            {/* Timeline Area Chart */}
            <div className="glass-card" style={{ display: "flex", flexDirection: "column", gridColumn: "span 2" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
                    <h3 style={{ fontSize: "16px", margin: 0, color: "var(--text-primary)" }}>Detection Timeline (24h)</h3>
                    <div style={{ display: "flex", gap: "16px", fontSize: "12px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                            <div style={{ width: "10px", height: "10px", borderRadius: "2px", background: "var(--status-danger)" }}></div>
                            <span style={{ color: "var(--text-secondary)" }}>Phishing</span>
                        </div>
                        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                            <div style={{ width: "10px", height: "10px", borderRadius: "2px", background: "var(--status-safe)" }}></div>
                            <span style={{ color: "var(--text-secondary)" }}>Safe</span>
                        </div>
                    </div>
                </div>
                
                <div style={{ flex: 1, minHeight: "250px" }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                            <defs>
                                <linearGradient id="colorPhish" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="var(--status-danger)" stopOpacity={0.3}/>
                                    <stop offset="95%" stopColor="var(--status-danger)" stopOpacity={0}/>
                                </linearGradient>
                                <linearGradient id="colorSafe" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="var(--status-safe)" stopOpacity={0.3}/>
                                    <stop offset="95%" stopColor="var(--status-safe)" stopOpacity={0}/>
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-subtle)" />
                            <XAxis 
                                dataKey="time" 
                                stroke="var(--text-muted)" 
                                fontSize={12} 
                                tickLine={false} 
                                axisLine={false} 
                                tickMargin={10} 
                            />
                            <YAxis 
                                stroke="var(--text-muted)" 
                                fontSize={12} 
                                tickLine={false} 
                                axisLine={false} 
                                tickFormatter={(val) => val === 0 ? '' : val}
                            />
                            <RechartsTooltip content={<CustomTooltip />} />
                            <Area type="monotone" dataKey="phishing" stroke="var(--status-danger)" strokeWidth={2} fillOpacity={1} fill="url(#colorPhish)" />
                            <Area type="monotone" dataKey="safe" stroke="var(--status-safe)" strokeWidth={2} fillOpacity={1} fill="url(#colorSafe)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
