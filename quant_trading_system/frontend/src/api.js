import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_VERSION = 'v1'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Health API
export const healthApi = {
  getHealth: () => api.get('/health'),
  getDetailedHealth: () => api.get('/health/detailed'),
  getMetrics: () => api.get('/health/metrics'),
}

// Strategy API
export const strategyApi = {
  getStrategies: () => api.get('/strategies'),
  getStrategy: (id) => api.get(`/strategies/${id}`),
  startStrategy: (id) => api.post(`/strategies/${id}/start`),
  stopStrategy: (id) => api.post(`/strategies/${id}/stop`),
}

// Position API
export const positionApi = {
  getPositions: () => api.get('/positions'),
  getPosition: (market) => api.get(`/positions/${market}`),
}

// Trade API
export const tradeApi = {
  getTrades: (limit = 20, offset = 0) => 
    api.get('/trades', { params: { limit, offset } }),
  getTrade: (id) => api.get(`/trades/${id}`),
}

// Log API
export const logApi = {
  getLogs: (params = {}) => api.get('/logs', { params }),
}

// Upbit API
export const upbitApi = {
  getAccounts: () => api.get('/upbit/accounts'),
  getBalance: (currency) => api.get(`/upbit/balance/${currency}`),
  getTicker: (markets) => api.get('/upbit/ticker', { params: { markets } }),
  getOrders: (params = {}) => api.get('/upbit/orders', { params }),
}

// Virtual Account API
export const virtualAccountApi = {
  getBalance: (strategyId = null) => api.get('/virtual-account/balance', { params: strategyId ? { strategy_id: strategyId } : {} }),
  getSummary: (strategyId = null) => api.get('/virtual-account/summary', { params: strategyId ? { strategy_id: strategyId } : {} }),
  getTrades: (limit = 50, strategyId = null) => api.get('/virtual-account/trades', { params: { limit, ...(strategyId ? { strategy_id: strategyId } : {}) } }),
  getStrategies: () => api.get('/virtual-account/strategies'),
  resetAccount: (strategyId = null) => api.post('/virtual-account/reset', null, { params: strategyId ? { strategy_id: strategyId } : {} }),
}

export default api

