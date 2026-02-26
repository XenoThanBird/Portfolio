import client from './client'

export default {
  listRules(projectId) { return client.get(`/projects/${projectId}/alerts/rules`) },
  createRule(projectId, data) { return client.post(`/projects/${projectId}/alerts/rules`, data) },
  updateRule(ruleId, data) { return client.put(`/alerts/rules/${ruleId}`, data) },
  deleteRule(ruleId) { return client.delete(`/alerts/rules/${ruleId}`) },
  listEvents(projectId, limit = 50) { return client.get(`/projects/${projectId}/alerts/events`, { params: { limit } }) },
  acknowledge(eventId) { return client.put(`/alerts/events/${eventId}/acknowledge`) },
  unacknowledged() { return client.get('/alerts/events/unacknowledged') },
  evaluate(projectId) { return client.post(`/projects/${projectId}/alerts/evaluate`) },
}
