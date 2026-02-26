import client from './client'

export default {
  list() { return client.get('/projects') },
  get(id) { return client.get(`/projects/${id}`) },
  create(data) { return client.post('/projects', data) },
  update(id, data) { return client.put(`/projects/${id}`, data) },
  delete(id) { return client.delete(`/projects/${id}`) },
  summary(id) { return client.get(`/projects/${id}/summary`) },
}
