<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['profile-updated'])

const username = ref('')
const email = ref('')
const loading = ref(false)
const loaded = ref(false)
const saving = ref(false)
const error = ref('')
const message = ref('')


function getCsrfToken() {
    const cookies = document.cookie.split('; ')

    for (const cookie of cookies) {
        const parts = cookie.split('=')

        if (parts[0] === 'csrf_access_token') {
            return decodeURIComponent(parts[1])
        }
    }

    return ''
}


async function loadProfile() {
    loading.value = true
    error.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/user/profile', {
            credentials: 'include'
        })

        if (!response.ok) {
            throw new Error('Failed to load profile')
        }

        const result = await response.json()
        username.value = result.data.username
        email.value = result.data.email
        loaded.value = true

    } catch (err) {
        error.value = err.message

    } finally {
        loading.value = false
    }
}


async function saveProfile() {
    if (saving.value || !loaded.value) {
        return
    }

    error.value = ''
    message.value = ''

    if (!username.value.trim()) {
        error.value = 'Please enter your name.'
        return
    }

    saving.value = true

    try {
        const response = await fetch('http://127.0.0.1:5000/api/user/profile', {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCsrfToken()
            },
            body: JSON.stringify({
                username: username.value.trim(),
                email: email.value.trim()
            })
        })

        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Failed to update profile')
        }

        username.value = result.data.username
        email.value = result.data.email
        message.value = result.message
        emit('profile-updated', username.value)

    } catch (err) {
        error.value = err.message

    } finally {
        saving.value = false
    }
}


onMounted(loadProfile)
</script>

<template>
    <section class="profile-page">
        <h1>My Profile</h1>
        <p>View and update your name and email address.</p>

        <p v-if="loading" role="status">Loading profile...</p>
        <p v-if="error" role="alert" class="error">{{ error }}</p>
        <p v-if="message" role="status" class="success">{{ message }}</p>

        <button v-if="!loaded && !loading" type="button" @click="loadProfile">Retry</button>

        <form v-if="loaded" @submit.prevent="saveProfile">
            <fieldset :disabled="saving || loading">
                <label for="user-name">Name</label>
                <input id="user-name" v-model="username" type="text" autocomplete="name" maxlength="100" required />

                <label for="user-email">Email</label>
                <input id="user-email" v-model="email" type="email" autocomplete="email" maxlength="100" required />

                <button type="submit">{{ saving ? 'Saving...' : 'Save Profile' }}</button>
            </fieldset>
        </form>
    </section>
</template>

<style scoped>
.profile-page { padding: 1rem; max-width: 32rem; }
fieldset { border: 0; padding: 0; margin: 0; min-width: 0; }
label { display: block; margin: 1rem 0 0.5rem; font-weight: bold; }
input { width: 100%; box-sizing: border-box; padding: 0.65rem; border: 1px solid #aaa; border-radius: 0.5rem; font: inherit; }
button { padding: 0.5rem 1rem; background: #175cf1; color: white; border: 1px solid #175cf1; border-radius: 0.5rem; cursor: pointer; }
form button { margin-top: 1.5rem; }
button:disabled, fieldset:disabled button { opacity: 0.6; cursor: not-allowed; }
button:focus-visible, input:focus-visible { outline: 2px solid #175cf1; outline-offset: 3px; }
.error { color: #b42318; }
.success { color: #16703c; }
</style>
