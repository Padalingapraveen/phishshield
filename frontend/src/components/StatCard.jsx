export default function StatCard({ title, value, subtitle }) {
  return (
    <div className="stat-card">
      <h3>{title}</h3>
      <div className="stat-value">{value}</div>
      {subtitle && <p>{subtitle}</p>}
    </div>
  );
}
