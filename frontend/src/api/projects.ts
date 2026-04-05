import api from './axios'

export const getProjects = async () => {
  const res = await api.get('/projects/my-projects')
  return res.data
}

export const createProject = async (name: string, description?: string) => {
  const res = await api.post('/projects/', { name, description })
  return res.data
}

export const getActivity = async (projectId: number) => {
  const res = await api.get(`/projects/${projectId}/activity`)
  return res.data
}

export const deleteProject = async (projectId: number) => {
  const res = await api.delete(`/projects/${projectId}`)
  return res.data
}