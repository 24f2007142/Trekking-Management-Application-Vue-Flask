import { createRouter, createWebHashHistory } from 'vue-router'
import LoginView from '../components/LoginView.vue'
import RegisterView from '../components/RegisterView.vue'
import AuthDashboard from '../components/AuthDashboard.vue'

import AdminLayout from '../layouts/AdminLayout.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminTreks from '../views/admin/AdminTreks.vue'
import AdminStaff from '../views/admin/AdminStaff.vue'
import AdminUsers from '../views/admin/AdminUsers.vue'
import AdminBookings from '../views/admin/AdminBookings.vue'
import AdminReports from '../views/admin/AdminReports.vue'
import AdminSettings from '../views/admin/AdminSettings.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginView },
    { path: '/register', component: RegisterView },
    {
      path: '/admin', component: AdminLayout, meta: { role: 'admin' },
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', component: AdminDashboard },
        { path: 'treks', component: AdminTreks },
        { path: 'staff', component: AdminStaff },
        { path: 'users', component: AdminUsers },
        { path: 'bookings', component: AdminBookings },
        { path: 'reports', component: AdminReports },
        { path: 'settings', component: AdminSettings },
      ],
    },
    ...['staff', 'user'].map(role => ({
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
