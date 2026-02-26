import client from './client'

export default {
  list(projectId) { return client.get(`/projects/${projectId}/risks`) },
  create(projectId, data) { return client.post(`/projects/${projectId}/risks`, data) },
  update(riskId, data) { return client.put(`/risks/${riskId}`, data) },
  delete(riskId) { return client.delete(`/risks/${riskId}`) },
  matrix(projectId) { return client.get(`/projects/${projectId}/risks/matrix`) },
  listChangeRequests(projectId) { return client.get(`/projects/${projectId}/change-requests`) },
  createChangeRequest(projectId, data) { return client.post(`/projects/${projectId}/change-requests`, data) },
  updateChangeRequest(crId, data) { return client.put(`/change-requests/${crId}`, data) },
}
