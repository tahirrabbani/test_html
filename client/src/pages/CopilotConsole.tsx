import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'

export default function CopilotConsole() {
  const qc = useQueryClient()
  const { data } = useQuery(['suggest'], async () => (await axios.post('/api/agent/suggest')).data)
  const exec = useMutation((id:string)=>axios.post('/api/agent/execute?action_id='+id), {
    onSuccess: ()=> qc.invalidateQueries(['suggest'])
  })
  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Copilot Console</h2>
      <ul className="space-y-2">
        {data?.map((a:any)=>(
          <li key={a.id} className="border p-2">
            <div className="font-medium">{a.proposed_action}</div>
            <button className="mt-2 px-2 py-1 bg-green-500 text-white" onClick={()=>exec.mutate(a.id)}>Execute</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
