import client from './client'

export default {
  list() { return client.get('/models') },
  create(data) { return client.post('/models', data) },
  update(modelId, data) { return client.put(`/models/${modelId}`, data) },
  recommend(data) { return client.post('/models/recommend', data) },
}
