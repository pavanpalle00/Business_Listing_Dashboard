// Thin wrapper around fetch() for the FastAPI backend.
const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

async function get(path, params = {}) {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== ''),
  )
  const url = `${API_URL}${path}${query.size ? `?${query}` : ''}`

  const response = await fetch(url)
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed (${response.status})`)
  }
  return response.json()
}

export const api = {
  summary: (filters) => get('/api/dashboard/summary', filters),
  cityCount: (filters) => get('/api/dashboard/city-count', filters),
  categoryCount: (filters) => get('/api/dashboard/category-count', filters),
  sourceCount: (filters) => get('/api/dashboard/source-count', filters),
  listings: (params) => get('/api/listings', params),
}
