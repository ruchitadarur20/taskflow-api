import api from './axios'

export const getTasks = async (projectId: number) => {
  const res = await api.get(`/projects/${projectId}/tasks`)
  return res.data
}

export const getTask = async (taskId: number) => {
  const res = await api.get(`/tasks/${taskId}`)
  return res.data
}

export const createTask = async (projectId: number, data: {
  title: string
  description?: string
  assigned_to?: number
  due_date?: string
}) => {
  const res = await api.post(`/projects/${projectId}/tasks`, { ...data, project_id: projectId })
  return res.data
}

export const updateTaskStatus = async (taskId: number, status: string) => {
  const res = await api.patch(`/tasks/${taskId}/status`, { status })
  return res.data
}

export const deleteTask = async (taskId: number) => {
  const res = await api.delete(`/tasks/${taskId}`)
  return res.data
}
