<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['profile-updated'])
const username = ref('')
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const message = ref('')
const loaded = ref(false)
const url = 'http://127.0.0.1:5000/api/admin/profile'

async function loadProfile() {
    loading.value = true
    error.value = ''
    try {
        const response = await fetch(url, { credentials: 'include' })
        if (!response.ok) throw new Error('Could not load your name')
        username.value = (await response.json()).data.username
        loaded.value = true
    } catch (err) { error.value = err.message }
    finally { loading.value = false }
}

async function saveName() {
    if (saving.value) return
    error.value = ''
    message.value = ''
    const name = username.value.trim()
    if (!name || name.length > 100) {
        error.value = 'Name must contain 1 to 100 characters'
        return
    }
    saving.value = true
    try {
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrf_access_token='))
        const token = cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : ''
        const response = await fetch(url, {
            method: 'PUT', credentials: 'include',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-TOKEN': token },
            body: JSON.stringify({ username: name })
        })
        const result = await response.json()
        if (!response.ok) throw new Error(result.message || 'Could not save your name')
        username.value = result.data.username
        emit('profile-updated', username.value)
        message.value = 'Name saved.'
    } catch (err) { error.value = err.message }
    finally { saving.value = false }
}

onMounted(loadProfile)
</script>

<template>
    <section>
        <h2>Settings</h2>
        <p v-if="loading" role="status">Loading...</p>
        <p v-if="error" role="alert">{{ error }}</p>
        <button v-if="!loading && !loaded" @click="loadProfile">Retry</button>
        <form v-if="loaded" @submit.prevent="saveName">
            <label for="admin-name">Display name</label>
            <input id="admin-name" v-model="username" required maxlength="100" :disabled="saving">
            <button type="submit" :disabled="saving">{{ saving ? 'Saving...' : 'Save' }}</button>
        </form>
        <p v-if="message" role="status">{{ message }}</p>
    </section>
</template>

<style scoped>
section { padding: 1rem; max-width: 30rem; }
label { display: block; margin-bottom: 0.5rem; }
input { padding: 0.6rem; max-width: 100%; box-sizing: border-box; }
button { margin-left: 0.5rem; padding: 0.6rem 1rem; cursor: pointer; }
[role='alert'] { color: #b42318; }
</style>
