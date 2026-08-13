import client from './client'

export default {
  list(projectId) { return client.get(`/projects/${projectId}/milestones`) },
  create(projectId, data) { return client.post(`/projects/${projectId}/milestones`, data) },
  update(milestoneId, data) { return client.put(`/milestones/${milestoneId}`, data) },
  delete(milestoneId) { return client.delete(`/milestones/${milestoneId}`) },
  addDependency(milestoneId, data) { return client.post(`/milestones/${milestoneId}/dependencies`, data) },
  reorder(projectId, data) { return client.put(`/projects/${projectId}/milestones/reorder`, data) },
}
