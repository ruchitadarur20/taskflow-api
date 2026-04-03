import { useEffect, useRef } from 'react'
import { useNotificationStore } from '../store/notificationStore'

export const useWebSocket = (userId: number | null) => {
  const ws = useRef<WebSocket | null>(null)
  const addNotification = useNotificationStore((s) => s.addNotification)

  useEffect(() => {
    if (!userId) return
    ws.current = new WebSocket(`ws://127.0.0.1:8000/ws/${userId}`)
    ws.current.onmessage = (event) => {
      addNotification({
        id: crypto.randomUUID(),
        message: event.data,
        timestamp: new Date().toISOString(),
        read: false,
      })
    }
    return () => ws.current?.close()
  }, [userId])
}
