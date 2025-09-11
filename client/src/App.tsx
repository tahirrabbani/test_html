import { Outlet, Link } from 'react-router-dom'

export default function App() {
  return (
    <div className="min-h-screen">
      <nav className="p-4 bg-blue-600 text-white flex gap-4">
        <Link to="/">Home</Link>
        <Link to="/dashboard">Ops Dashboard</Link>
        <Link to="/copilot">Copilot Console</Link>
      </nav>
      <main className="p-4">
        <Outlet />
      </main>
    </div>
  )
}
