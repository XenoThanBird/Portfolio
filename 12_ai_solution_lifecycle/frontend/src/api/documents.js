import client from './client'

export default {
  list(projectId) { return client.get(`/projects/${projectId}/documents`) },
  get(docId) { return client.get(`/documents/${docId}`) },
  generate(projectId, data) { return client.post(`/projects/${projectId}/documents/generate`, data) },
  create(projectId, data) { return client.post(`/projects/${projectId}/documents`, data) },
  update(docId, data) { return client.put(`/documents/${docId}`, data) },
  versions(docId) { return client.get(`/documents/${docId}/versions`) },
}
