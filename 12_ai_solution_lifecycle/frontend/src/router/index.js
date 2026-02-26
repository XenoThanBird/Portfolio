import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
  { path: '/', name: 'Dashboard', component: () => import('../views/DashboardView.vue') },
  { path: '/projects', name: 'Projects', component: () => import('../views/ProjectsView.vue') },
  { path: '/projects/:id', name: 'ProjectDetail', component: () => import('../views/ProjectDetailView.vue'), props: true },
  { path: '/projects/:id/documents', name: 'Documents', component: () => import('../views/DocumentsView.vue'), props: true },
  { path: '/projects/:id/prompts', name: 'Prompts', component: () => import('../views/PromptLibraryView.vue'), props: true },
  { path: '/projects/:id/playground', name: 'Playground', component: () => import('../views/PlaygroundView.vue'), props: true },
  { path: '/projects/:id/milestones', name: 'Milestones', component: () => import('../views/MilestonesView.vue'), props: true },
  { path: '/projects/:id/raci', name: 'RACI', component: () => import('../views/RACIView.vue'), props: true },
  { path: '/projects/:id/sla', name: 'SLA', component: () => import('../views/SLAView.vue'), props: true },
  { path: '/projects/:id/alerts', name: 'Alerts', component: () => import('../views/AlertsView.vue'), props: true },
  { path: '/projects/:id/risks', name: 'Risks', component: () => import('../views/RiskView.vue'), props: true },
  { path: '/models', name: 'ModelCatalog', component: () => import('../views/ModelCatalogView.vue') },
  { path: '/projects/:id/value', name: 'Value', component: () => import('../views/ValueView.vue'), props: true },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    return { name: 'Login' }
  }
})

export default router
