import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

export default function OpsDashboard() {
  const { data } = useQuery(['sites'], async () => (await axios.get('/api/sites')).data)
  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Ops Dashboard</h2>
      <table className="min-w-full text-left">
        <thead><tr><th>Site</th><th>Country</th><th>Uptime</th></tr></thead>
        <tbody>
          {data?.map((s:any)=> (
            <tr key={s.id}><td>{s.name}</td><td>{s.country}</td><td>{s.kpis.uptime_pct.toFixed(2)}%</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
