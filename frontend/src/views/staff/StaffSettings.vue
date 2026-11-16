<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['profile-updated'])
const username = ref('')
const email = ref('')
const contactNumber = ref('')
const availableDate = ref('')
const loading = ref(false)
const saving = ref(false)
const loaded = ref(false)
const error = ref('')
const message = ref('')

async function fetchProfile() {
    loading.value = true
    error.value = ''
    try {
        const response = await fetch('http://127.0.0.1:5000/api/staff/profile', {
            credentials: 'include'
        })
        const result = await response.json()
        if (!response.ok) throw new Error(result.message || 'Failed to load profile')

        username.value = result.data.username
        email.value = result.data.email
        contactNumber.value = result.data.contact_number
        availableDate.value = result.data.next_available_date || ''
        loaded.value = true
    } catch (err) {
        error.value = err.message
    } finally {
        loading.value = false
    }
}

function getCsrfToken() {
    const cookie = document.cookie.split('; ')
        .find(row => row.startsWith('csrf_access_token='))
    return cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : ''
}

async function saveProfile() {
    if (saving.value) return
    saving.value = true
    error.value = ''
    message.value = ''
    try {
        const response = await fetch('http://127.0.0.1:5000/api/staff/profile', {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCsrfToken()
            },
            body: JSON.stringify({
                username: username.value.trim(),
                contact_number: contactNumber.value.trim(),
                next_available_date: availableDate.value || null
            })
        })
        const result = await response.json()
        if (!response.ok) throw new Error(result.message || 'Failed to update profile')

        username.value = username.value.trim()
        contactNumber.value = contactNumber.value.trim()
        message.value = result.message
        emit('profile-updated', username.value)
    } catch (err) {
        error.value = err.message
    } finally {
        saving.value = false
    }
}

onMounted(fetchProfile)
</script>

<template>
    <section class="profile-page">
        <h2>My Profile</h2>
        <p v-if="loading" role="status">Loading profile...</p>
        <p v-if="error" class="error-message" role="alert">{{ error }}</p>
        <button v-if="!loaded && !loading" type="button" @click="fetchProfile">Try again</button>
        <form v-if="loaded" @submit.prevent="saveProfile">
            <fieldset :disabled="saving">
                <label for="staff-name">Name</label>
                <input id="staff-name" v-model="username" autocomplete="name" maxlength="100" required />

                <label for="staff-email">Email</label>
                <input id="staff-email" :value="email" type="email" readonly />

                <label for="staff-contact">Contact Number</label>
                <input id="staff-contact" v-model="contactNumber" type="tel" autocomplete="tel" maxlength="15" required />

                <label for="staff-available">Available From</label>
                <input id="staff-available" v-model="availableDate" type="date" aria-describedby="availability-help" />
                <p id="availability-help" class="help-text">Leave blank if you have no availability restriction. This does not change existing trek assignments.</p>

                <button type="submit">{{ saving ? 'Saving...' : 'Save Profile' }}</button>
            </fieldset>
            <p v-if="message" class="success-message" role="status">{{ message }}</p>
        </form>
    </section>
</template>

<style scoped>
.profile-page { padding: 1rem; max-width: 32rem; }
fieldset { border: 0; padding: 0; margin: 0; min-width: 0; }
label { display: block; margin: 1rem 0 0.5rem; font-weight: bold; }
input { width: 100%; box-sizing: border-box; padding: 0.65rem; border: 1px solid #d6d6d6; border-radius: 0.5rem; font: inherit; }
input[readonly] { background: #f2f2f2; color: #595959; }
button { padding: 0.6rem 1rem; border: 1px solid #175cf1; border-radius: 0.5rem; background: white; color: #175cf1; font: inherit; cursor: pointer; }
button:hover:not(:disabled) { background: #175cf1; color: white; }
button:disabled { cursor: not-allowed; opacity: 0.6; }
input:focus-visible, button:focus-visible { outline: 2px solid #175cf1; outline-offset: 2px; }
.help-text { color: #595959; line-height: 1.5; }
.error-message { color: #b42318; }
.success-message { color: #216e39; }
</style>
