export default function StatCard({ title, value, subtitle }) {
  return (
    <div className="glass-card">
      <div className="stat-card-header">{title}</div>
      <div className="stat-card-value">{value}</div>
      {subtitle && <div className="stat-card-subtitle">{subtitle}</div>}
    </div>
  );
}
