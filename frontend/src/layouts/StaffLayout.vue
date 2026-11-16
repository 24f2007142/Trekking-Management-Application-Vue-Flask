<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('Staff')
const errorMessage = ref('')

onMounted(async () => {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/staff/dashboard', {
            credentials: 'include'
        })

        if (response.status === 401 || response.status === 422) {
            await router.replace('/login')
            return
        }

        if (!response.ok) throw new Error('Unable to load profile')

        const data = await response.json()
        username.value = data.data.staff_name
    } catch {
        errorMessage.value = 'Unable to load your profile. Please refresh to try again.'
    }
})

async function handleLogout() {
    errorMessage.value = ''
    try {
        const response = await fetch('http://127.0.0.1:5000/api/logout', {
            method: 'POST',
            credentials: 'include'
        })

        if (!response.ok) throw new Error('Logout failed')

        await router.replace('/login')
    } catch {
        errorMessage.value = 'Unable to log out. Please try again.'
    }
}
</script>

<template>
    <div class="staff-layout">
        <header class="staff-header">
            <p>Welcome, <span class="staff-name">{{ username }}</span></p>
            <button type="button" class="logout-button" @click="handleLogout">Logout</button>
        </header>

        <div class="staff-body">
            <nav class="staff-sidebar" aria-label="Staff navigation">
                <div class="sidebar-link">
                    <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                        <rect x="3" y="3" width="7" height="7" rx="1" />
                        <rect x="14" y="3" width="7" height="7" rx="1" />
                        <rect x="3" y="14" width="7" height="7" rx="1" />
                        <rect x="14" y="14" width="7" height="7" rx="1" />
                    </svg>
                    <RouterLink to="/staff/dashboard">Dashboard</RouterLink>
                </div>

                <div class="sidebar-link">
                    <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <circle cx="14" cy="4" r="2" />
                        <path d="m7 21 4-6 1-7 3 4h4M8 12l2-4h2m-1 7 4 2 2 4M20 12v9" />
                    </svg>
                    <RouterLink to="/staff/treks">My Treks</RouterLink>
                </div>

                <div class="sidebar-link">
                    <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <circle cx="9" cy="7" r="3" />
                        <path d="M3 21v-2a6 6 0 0 1 12 0v2M16 4a3 3 0 0 1 0 6m2 4a5 5 0 0 1 3 5v2" />
                    </svg>
                    <RouterLink to="/staff/participants">Participants</RouterLink>
                </div>

                <div class="sidebar-link">
                    <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <circle cx="12" cy="12" r="10" />
                        <circle cx="12" cy="9" r="3" />
                        <path d="M5 19a8 8 0 0 1 14 0" />
                    </svg>
                    <RouterLink to="/staff/profile">My Profile</RouterLink>
                </div>
            </nav>

            <main class="staff-content">
                <p v-if="errorMessage" role="alert">{{ errorMessage }}</p>
                <RouterView @profile-updated="username = $event" />
            </main>
        </div>
    </div>
</template>

<style scoped>
.staff-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    min-height: calc(100vh - 1rem);
}

.staff-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    padding: 0 1rem;
    background-color: #f2f2f2;
    border-bottom: 0.2rem solid #f2f2f2;
    border-radius: 0.5rem;
    font-size: 1.5rem;
}

.staff-name {
    color: #175cf1;
    overflow-wrap: anywhere;
}

.logout-button {
    padding: 0.5rem 1rem;
    border: 1px solid #175cf1;
    border-radius: 0.5rem;
    background-color: white;
    color: #175cf1;
    font: inherit;
    font-size: 0.9rem;
    cursor: pointer;
    transition: background-color 0.2s, color 0.2s;
}

.logout-button:hover {
    background-color: #175cf1;
    color: white;
}

.staff-body {
    display: grid;
    grid-template-columns: minmax(12rem, 1fr) minmax(0, 5fr);
}

.staff-sidebar {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    border-right: 0.2rem solid #f2f2f2;
}

.sidebar-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 0.5rem;
    border: 0.1rem solid transparent;
    border-radius: 0.75rem;
    color: inherit;
    text-decoration: none;
    transition: background-color 0.2s, color 0.2s;
}

.sidebar-link a {
    color: inherit;
    text-decoration: none;
    flex: 1;
}

.sidebar-link svg {
    flex-shrink: 0;
}

.sidebar-link:hover,
.sidebar-link:has(.router-link-active) {
    background-color: #f2f2f2;
    color: #175cf1;
}

.sidebar-link:has(.router-link-active) {
    border-color: #175cf1;
}

.sidebar-link a:focus-visible,
.logout-button:focus-visible {
    outline: 2px solid #175cf1;
    outline-offset: 3px;
}

.staff-content {
    min-width: 0;
}

@media (max-width: 640px) {
    .staff-body {
        grid-template-columns: 1fr;
        grid-template-rows: auto 1fr;
    }

    .staff-sidebar {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.5rem;
        padding: 0.75rem;
        border-right: 0;
        border-bottom: 0.2rem solid #f2f2f2;
    }

    .staff-header {
        font-size: 1.2rem;
    }
}
</style>
