export interface User {
  id: number
  full_name: string
  email: string
  is_active: boolean
  role_id: number
  created_at: string
}

export interface Project {
  id: number
  name: string
  description?: string
  owner_id: number
}

export interface Task {
  id: number
  title: string
  description?: string
  status: 'todo' | 'in_progress' | 'done'
  project_id: number
  assigned_to?: number
  created_by: number
  due_date?: string
  created_at?: string
}

export interface Comment {
  id: number
  content: string
  task_id: number
  author_id: number
  created_at: string
}

export interface ActivityLog {
  id: number
  project_id: number
  task_id?: number
  user_id: number
  action: string
  detail?: string
  created_at: string
}

export interface Notification {
  id: string
  message: string
  timestamp: string
  read: boolean
}
