import client from './client'

export default {
  getMatrix(projectId) { return client.get(`/projects/${projectId}/raci`) },
  create(projectId, data) { return client.post(`/projects/${projectId}/raci`, data) },
  update(entryId, data) { return client.put(`/raci/${entryId}`, data) },
  delete(entryId) { return client.delete(`/raci/${entryId}`) },
}
