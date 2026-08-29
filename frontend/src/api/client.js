import axios from 'axios'

export const API_BASE = import.meta.env.VITE_API_URL || ''

const client = axios.create({ baseURL: API_BASE, timeout: 30000 })

export const thumbnailUrl = (path) => (path ? `${API_BASE}${path}` : '')

export const analyzeImage = (file, onProgress) => {
  const form = new FormData()
  form.append('file', file)
  return client.post('/analyze', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: e => onProgress && onProgress(Math.round((e.loaded / e.total) * 100)),
  })
}

export const getResults = (skip = 0, limit = 50) =>
  client.get('/results', { params: { skip, limit } })

export const getResult = (id) =>
  client.get(`/results/${id}`)

export const getHealth = () =>
  client.get('/health')
