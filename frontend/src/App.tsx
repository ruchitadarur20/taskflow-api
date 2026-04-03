import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useAuthStore } from './store/authStore'
import { getMe } from './api/auth'
import { useWebSocket } from './hooks/useWebSocket'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProjectsPage from './pages/ProjectsPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import TaskDetailPage from './pages/TaskDetailPage'

const queryClient = new QueryClient()

function AppInner() {
  const { user, token, setAuth, clearAuth } = useAuthStore()
  useWebSocket(user?.id ?? null)

  useEffect(() => {
    if (token && !user) {
      getMe()
        .then((u) => setAuth(u, token, localStorage.getItem('refresh_token') ?? ''))
        .catch(() => clearAuth())
    }
  }, [token])

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/projects" element={<ProtectedRoute><ProjectsPage /></ProtectedRoute>} />
      <Route path="/projects/:id" element={<ProtectedRoute><ProjectDetailPage /></ProtectedRoute>} />
      <Route path="/projects/:id/tasks/:taskId" element={<ProtectedRoute><TaskDetailPage /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/projects" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppInner />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
