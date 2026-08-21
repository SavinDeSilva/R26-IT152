import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { panel, T } from '../theme'

const PIE = [T.danger, T.success]

export default function StatsCharts({ stats, loading }) {
  const box = { ...panel, padding: '14px 10px 6px' }

  if (loading) {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 14 }}>
        {[1, 2, 3].map((i) => <div key={i} style={{ ...box, height: 240, background: T.lineSoft }} />)}
      </div>
    )
  }

  if (!stats || stats.total === 0) {
    return <div style={{ ...panel, padding: 28, textAlign: 'center', color: T.muted, borderStyle: 'dashed' }}>No historical incidents for this station yet.</div>
  }

  const statusPie = [
    { name: 'Active', value: stats.active || 0 },
    { name: 'Closed', value: stats.closed || 0 },
  ]

  const title = { margin: '0 0 8px 6px', fontSize: 13, color: T.muted, fontWeight: 600 }
  const tick = { fontSize: 11, fill: T.muted }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 14 }}>
      <div style={box}>
        <h3 style={title}>Incidents per day</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={stats.volume_by_day || []}>
            <CartesianGrid strokeDasharray="3 3" stroke={T.line} />
            <XAxis dataKey="day" tick={tick} />
            <YAxis allowDecimals={false} tick={tick} />
            <Tooltip />
            <Bar dataKey="count" fill={T.navy} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div style={box}>
        <h3 style={title}>Minutes to acknowledge</h3>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={stats.response_times || []}>
            <CartesianGrid strokeDasharray="3 3" stroke={T.line} />
            <XAxis dataKey="incident_id" tick={tick} />
            <YAxis tick={tick} />
            <Tooltip />
            <Line type="monotone" dataKey="minutes_to_ack" stroke={T.success} strokeWidth={2} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div style={box}>
        <h3 style={title}>Closed vs active</h3>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie data={statusPie} dataKey="value" nameKey="name" outerRadius={80} label>
              {statusPie.map((entry, i) => (
                <Cell key={entry.name} fill={PIE[i % PIE.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
