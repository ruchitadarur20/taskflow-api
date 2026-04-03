import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { useNotificationStore } from '../store/notificationStore'
import { logout } from '../api/auth'

export default function Navbar() {
  const { user, clearAuth } = useAuthStore()
  const { notifications, markAllRead } = useNotificationStore()
  const [showNotifications, setShowNotifications] = useState(false)
  const navigate = useNavigate()

  const unread = notifications.filter((n) => !n.read).length

  const handleLogout = async () => {
    try { await logout() } catch {}
    clearAuth()
    navigate('/login')
  }

  return (
    <nav className="bg-gray-900 text-white px-6 py-4 flex items-center justify-between shadow-lg">
      <Link to="/projects" className="text-xl font-bold tracking-tight text-indigo-400">
        TaskFlow
      </Link>
      <div className="flex items-center gap-4">
        {user && <span className="text-sm text-gray-400">Hi, {user.full_name}</span>}

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => { setShowNotifications(!showNotifications); markAllRead() }}
            className="relative p-2 rounded-full hover:bg-gray-700 transition"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-5-5.917V4a1 1 0 10-2 0v1.083A6 6 0 006 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            {unread > 0 && (
              <span className="absolute top-1 right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                {unread}
              </span>
            )}
          </button>
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-72 bg-white text-gray-800 rounded-lg shadow-xl z-50 max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <p className="p-4 text-sm text-gray-500">No notifications</p>
              ) : (
                notifications.map((n) => (
                  <div key={n.id} className="px-4 py-3 border-b text-sm hover:bg-gray-50">
                    <p>{n.message}</p>
                    <p className="text-xs text-gray-400 mt-1">{new Date(n.timestamp).toLocaleTimeString()}</p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        <button onClick={handleLogout} className="text-sm text-gray-400 hover:text-white transition">
          Logout
        </button>
      </div>
    </nav>
  )
}
