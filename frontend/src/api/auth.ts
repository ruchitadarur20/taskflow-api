import api from './axios'

export const login = async (email: string, password: string) => {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const res = await api.post('/auth/login', form)
  return res.data
}

export const register = async (full_name: string, email: string, password: string) => {
  const res = await api.post('/auth/register', null, {
    params: { full_name, email, password },
  })
  return res.data
}

export const logout = async () => {
  await api.post('/auth/logout')
}

export const getMe = async () => {
  const res = await api.get('/users/me')
  return res.data
}
