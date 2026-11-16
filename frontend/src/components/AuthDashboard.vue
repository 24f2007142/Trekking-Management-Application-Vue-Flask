<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ role: String })
const router = useRouter()
const message = ref('')
const error = ref('')
const notice = ref('')
const staff = ref({ username: '', email: '', password: '', contact_number: '' })
const saving = ref(false)
const titles = { admin: 'Admin', staff: 'Trek Staff', user: 'Trekker' }

function csrfToken() {
  const cookie = document.cookie.split('; ').find(item => item.startsWith('csrf_access_token='))
  return cookie ? decodeURIComponent(cookie.split('=')[1]) : ''
}

watch(() => props.role, async role => {
  message.value = ''
  error.value = ''
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/${role}/dashboard`, {
      credentials: 'include',
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.message || data.msg || 'Access denied')
    message.value = data.message
  } catch (err) {
    error.value = err.message
  }
}, { immediate: true })

async function createStaff() {
  saving.value = true
  notice.value = ''
  try {
    const response = await fetch('http://127.0.0.1:5000/api/admin/staffs', {
      method: 'POST', credentials: 'include',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-TOKEN': csrfToken() },
      body: JSON.stringify(staff.value),
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.message || data.msg || 'Could not create staff')
    notice.value = data.message
    staff.value = { username: '', email: '', password: '', contact_number: '' }
  } catch (err) {
    notice.value = err.message
  } finally {
    saving.value = false
  }
}

async function logout() {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/logout', {
      method: 'POST', credentials: 'include',
      headers: { 'X-CSRF-TOKEN': csrfToken() },
    })
    if (!response.ok) throw new Error('Logout failed')
    await router.push('/login')
  } catch (err) {
    error.value = err.message
  }
}
</script>

<template>
  <main>
    <h1>{{ titles[role] }} Dashboard</h1>
    <p>{{ message }}</p>
    <p role="alert">{{ error }}</p>
    <button @click="logout">Log out</button>
    <form v-if="role === 'admin'" @submit.prevent="createStaff">
      <h2>Create Trek Staff account</h2>
      <label>Name <input v-model="staff.username" required maxlength="100"></label>
      <label>Email <input v-model="staff.email" type="email" required maxlength="100"></label>
      <label>Password <input v-model="staff.password" type="password" required></label>
      <label>Contact number <input v-model="staff.contact_number" required maxlength="15"></label>
      <button :disabled="saving">{{ saving ? 'Creating…' : 'Create staff' }}</button>
      <p role="status">{{ notice }}</p>
    </form>
  </main>
</template>

<style scoped>
main { max-width: 640px; margin: 3rem auto; padding: 1rem; font-family: sans-serif; }
form { margin-top: 2rem; }
label { display: block; margin: 1rem 0; }
input { display: block; padding: .5rem; width: 90%; }
button { padding: .6rem 1rem; cursor: pointer; }
</style>
