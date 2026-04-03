import api from './axios'

export const getComments = async (taskId: number) => {
  const res = await api.get(`/tasks/${taskId}/comments`)
  return res.data
}

export const addComment = async (taskId: number, content: string) => {
  const res = await api.post(`/tasks/${taskId}/comments`, { content })
  return res.data
}

export const deleteComment = async (taskId: number, commentId: number) => {
  await api.delete(`/tasks/${taskId}/comments/${commentId}`)
}
