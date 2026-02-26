import client from './client'

export default {
  list(projectId) { return client.get(`/projects/${projectId}/sla`) },
  create(projectId, data) { return client.post(`/projects/${projectId}/sla`, data) },
  update(slaId, data) { return client.put(`/sla/${slaId}`, data) },
  delete(slaId) { return client.delete(`/sla/${slaId}`) },
  addMetric(slaId, data) { return client.post(`/sla/${slaId}/metrics`, data) },
  compliance(slaId) { return client.get(`/sla/${slaId}/compliance`) },
  dashboard(projectId) { return client.get(`/projects/${projectId}/sla/dashboard`) },
}
