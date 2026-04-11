import axios from 'axios'

/**
 * Axios instance — baseURL points to FastAPI via Vite proxy.
 * In dev: Vite proxies /api → http://localhost:8000
 * In prod: serve from same origin, no proxy needed.
 */
const client = axios.create({
  baseURL: '/api/v1',
  timeout: 12_000,
  headers: { 'Content-Type': 'application/json' },
})

// Response interceptor — surface upstream errors clearly
client.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail ?? err.message ?? 'Unknown error'
    console.error(`[API] ${err.config?.url} → ${err.response?.status}: ${msg}`)
    return Promise.reject(err)
  }
)

export default client
