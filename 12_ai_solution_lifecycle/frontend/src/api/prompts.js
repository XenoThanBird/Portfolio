import client from './client'

export default {
  list(projectId) { return client.get(`/projects/${projectId}/prompts`) },
  search(projectId, params) { return client.get(`/projects/${projectId}/prompts/search`, { params }) },
  get(promptId) { return client.get(`/prompts/${promptId}`) },
  create(projectId, data) { return client.post(`/projects/${projectId}/prompts`, data) },
  update(promptId, data) { return client.put(`/prompts/${promptId}`, data) },
  delete(promptId) { return client.delete(`/prompts/${promptId}`) },
  run(promptId, data) { return client.post(`/prompts/${promptId}/run`, data) },
  feedback(runId, data) { return client.put(`/prompts/runs/${runId}/feedback`, data) },
}
