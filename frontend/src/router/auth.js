import { createRouter, createWebHashHistory } from 'vue-router'
import LoginView from '../components/LoginView.vue'
import RegisterView from '../components/RegisterView.vue'
import AuthDashboard from '../components/AuthDashboard.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginView },
    { path: '/register', component: RegisterView },
    ...['admin', 'staff', 'user'].map(role => ({
      path: `/${role}/dashboard`, component: AuthDashboard,
      props: { role }, meta: { role },
    })),
  ],
})

router.beforeEach(async to => {
  if (!to.meta.role) return
  try {
    const response = await fetch('http://127.0.0.1:5000/api/who', {
      credentials: 'include',
    })
    if (!response.ok) return '/login'
    const { user } = await response.json()
    if (!['admin', 'staff', 'user'].includes(user.role)) return '/login'
    if (user.role !== to.meta.role) return `/${user.role}/dashboard`
  } catch {
    return '/login'
  }
})

export default router
