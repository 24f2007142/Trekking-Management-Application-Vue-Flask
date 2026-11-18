import { createRouter, createWebHashHistory } from 'vue-router'
import LoginView from '../components/LoginView.vue'
import RegisterView from '../components/RegisterView.vue'

import AdminLayout from '../layouts/AdminLayout.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminTreks from '../views/admin/AdminTreks.vue'
import AdminStaff from '../views/admin/AdminStaff.vue'
import AdminUsers from '../views/admin/AdminUsers.vue'
import AdminBookings from '../views/admin/AdminBookings.vue'
import AdminReports from '../views/admin/AdminReports.vue'
import AdminSettings from '../views/admin/AdminSettings.vue'

import StaffLayout from '../layouts/StaffLayout.vue'
import StaffDashboard from '../views/staff/StaffDashboard.vue'
import ManageTreks from '../views/staff/ManageTreks.vue'
import ManageParticipants from '../views/staff/ManageParticipants.vue'
import StaffSettings from '../views/staff/StaffSettings.vue'

import UserLayout from '../layouts/UserLayout.vue'
import UserDashboard from '../views/user/UserDashboard.vue'
import UserTreks from '../views/user/UserTreks.vue'
import UserBookings from '../views/user/UserBookings.vue'
import UserHistory from '../views/user/UserHistory.vue'
import UserSettings from '../views/user/UserSettings.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      beforeEnter() {
        window.location.replace('http://127.0.0.1:5000/')
        return false
      },
    },
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
    {
      path: '/staff', component: StaffLayout, meta: { role: 'staff' },
      children: [
        { path: '', redirect: '/staff/dashboard' },
        { path: 'dashboard', component: StaffDashboard },
        { path: 'treks', component: ManageTreks },
        { path: 'participants', component: ManageParticipants },
        { path: 'profile', component: StaffSettings },
      ],
    },
    {
      path: '/user', component: UserLayout, meta: { role: 'user' },
      children: [
        { path: '', redirect: '/user/dashboard' },
        { path: 'dashboard', component: UserDashboard },
        { path: 'treks', component: UserTreks },
        { path: 'bookings', component: UserBookings },
        { path: 'history', component: UserHistory },
        { path: 'profile', component: UserSettings },
      ],
    },
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
