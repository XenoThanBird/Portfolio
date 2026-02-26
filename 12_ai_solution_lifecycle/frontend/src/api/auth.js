import client from './client'

export default {
  login(email, password) {
    return client.post('/auth/login', { email, password })
  },
}
