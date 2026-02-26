import client from './client'

export default {
  get(projectId) { return client.get(`/projects/${projectId}/value`) },
  createOrUpdate(projectId, data) { return client.post(`/projects/${projectId}/value`, data) },
  calculateRoi(projectId, data) { return client.post(`/projects/${projectId}/value/roi`, data) },
  getRoadmap(projectId) { return client.get(`/projects/${projectId}/value/roadmap`) },
  prioritizeUseCases(projectId, data) { return client.post(`/projects/${projectId}/value/use-cases`, data) },
}
