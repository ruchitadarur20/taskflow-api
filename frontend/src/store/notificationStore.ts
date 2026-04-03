import { create } from 'zustand'
import type { Notification } from '../types'

interface NotificationState {
  notifications: Notification[]
  addNotification: (n: Notification) => void
  markAllRead: () => void
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  addNotification: (n) => set((s) => ({ notifications: [n, ...s.notifications].slice(0, 20) })),
  markAllRead: () => set((s) => ({
    notifications: s.notifications.map((n) => ({ ...n, read: true })),
  })),
}))
