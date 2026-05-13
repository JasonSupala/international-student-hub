import api from './axios'

export function listAdminRecords(endpoint, params = {}) {
  return api.get(`/admin-panel/${endpoint}/`, { params })
}

export function createAdminRecord(endpoint, data) {
  return api.post(`/admin-panel/${endpoint}/`, data)
}

export function updateAdminRecord(endpoint, id, data) {
  return api.patch(`/admin-panel/${endpoint}/${id}/`, data)
}

export function deleteAdminRecord(endpoint, id) {
  return api.delete(`/admin-panel/${endpoint}/${id}/`)
}
