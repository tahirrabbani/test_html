import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

export default function Home() {
  const [mode, setMode] = useState<'pre'|'with'>('pre')
  const { data } = useQuery(['summary', mode], async () => {
    const res = await axios.get(`/api/summary?mode=${mode}`)
    return res.data
  })
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Viztronics Chargepoint Copilot (Demo)</h1>
      <div className="flex items-center gap-2">
        <span>Mode:</span>
        <button className={`px-2 py-1 border ${mode==='pre'?'bg-blue-500 text-white':''}`} onClick={()=>setMode('pre')}>Pre-Copilot</button>
        <button className={`px-2 py-1 border ${mode==='with'?'bg-blue-500 text-white':''}`} onClick={()=>setMode('with')}>With-Copilot</button>
      </div>
      {data && (
        <ul className="mt-4">
          <li>Network Uptime: {data.uptime_pct.toFixed(2)}%</li>
          <li>Utilization: {data.utilization_pct.toFixed(2)}%</li>
          <li>Revenue: €{data.revenue_eur.toFixed(2)}</li>
        </ul>
      )}
    </div>
  )
}
