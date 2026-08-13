import client from './client'

export default {
  global() { return client.get('/dashboard') },
  project(projectId) { return client.get(`/dashboard/projects/${projectId}`) },
}
