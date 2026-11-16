<script setup>
import { ref, onMounted } from 'vue'

const users = ref([])
const searchText = ref('')
const loading = ref(false)
const loadingHistory = ref(false)
const updatingUserId = ref(null)
const error = ref('')
const message = ref('')
const historyForUser = ref(null)
const bookingHistory = ref([])

function getCsrfToken() {
    const cookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrf_access_token='))

    return cookie
        ? decodeURIComponent(cookie.split('=').slice(1).join('='))
        : ''
}

async function fetchUsers(search = searchText.value) {
    loading.value = true
    error.value = ''

    try {
        const url = new URL('http://127.0.0.1:5000/api/admin/users')
        url.searchParams.set('search', search)

        const response = await fetch(url, { credentials: 'include' })
        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Could not load users')
        }



        users.value = result.data
    } catch (err) {
        error.value = err.message
    } finally {
        loading.value = false
    }
}

async function showBookingHistory(user) {
    error.value = ''
    message.value = ''
    loadingHistory.value = true

    try {
        const response = await fetch(
            `http://127.0.0.1:5000/api/admin/users/${user.id}/bookings`,
            { credentials: 'include' }
        )
        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Could not load booking history')
        }

        bookingHistory.value = result.data
        historyForUser.value = user
    } catch (err) {
        error.value = err.message
    } finally {
        loadingHistory.value = false
    }
}

function closeBookingHistory() {
    historyForUser.value = null
    bookingHistory.value = []
}

async function updateUserStatus(user) {
    error.value = ''
    message.value = ''

    let newStatus = 'blacklist'

    if (user.approval_status === 'blacklist') {
        newStatus = 'approved'
    } else if (!confirm('Are you sure you want to blacklist this user?')) {
        return
    }

    updatingUserId.value = user.id

    try {
        const response = await fetch(
            `http://127.0.0.1:5000/api/admin/users/${user.id}/status`,
            {
                method: 'PATCH',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': getCsrfToken()
                },
                body: JSON.stringify({ approval_status: newStatus })
            }
        )
        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Could not update user status')
        }

        message.value = `User ID ${user.id}: ${result.message || 'Status updated successfully'}`
        await fetchUsers(searchText.value)
    } catch (err) {
        error.value = err.message
    } finally {
        updatingUserId.value = null
    }
}

onMounted(fetchUsers)
</script>

<template>
    <section>
        <div class="section-heading">
            <h2>Manage Users</h2>
        </div>

        <p v-if="message" role="status">{{ message }}</p>
        <p v-if="error" role="alert">{{ error }}</p>

        <form v-if="!historyForUser"class="search-form" @submit.prevent="fetchUsers(searchText)">
            <input
                id="user-search"
                v-model="searchText"
                type="search"
                placeholder="Search users..."
                aria-label="Search users"
            >
            <button type="submit" class="trek-button primary">Search</button>
        </form>

        <p v-if="loading">Loading users...</p>

        <div v-else-if="historyForUser" class="users-list">
            <div class="section-heading">
                <h3>Booking History: {{ historyForUser.username }}</h3>
                <button type="button" class="trek-button" @click="closeBookingHistory">
                    Back to Users
                </button>
            </div>

            <p v-if="loadingHistory">Loading booking history...</p>
            <table v-else-if="bookingHistory.length">
                <thead>
                    <tr>
                        <th>Booking ID</th>
                        <th>Trek</th>
                        <th>Location</th>
                        <th>Booking Date</th>
                        <th>Trek Dates</th>
                        <th>Slots</th>
                        <th>Booking Status</th>
                        <th>Trek Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="booking in bookingHistory" :key="booking.id">
                        <td>{{ booking.id }}</td>
                        <td>{{ booking.trek.display_id }} — {{ booking.trek.trek_name }}</td>
                        <td>{{ booking.trek.location }}</td>
                        <td>{{ booking.booking_date }}</td>
                        <td>{{ booking.trek.start_date }} to {{ booking.trek.end_date }}</td>
                        <td>{{ booking.slots_booked }}</td>
                        <td>{{ booking.status }}</td>
                        <td>{{ booking.trek.trek_status }}</td>
                    </tr>
                </tbody>
            </table>
            <p v-else-if="!loadingHistory">No booking history found.</p>
        </div>

        <div v-else-if="users.length" class="users-list">
            <table>
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="user in users" :key="user.id">
                        <td>{{ user.id }}</td>
                        <td>{{ user.username }}</td>
                        <td>{{ user.email }}</td>
                        <td>{{ user.approval_status }}</td>
                        <td>
                            <div class="user-actions">
                                <button type="button" class="trek-button" @click="showBookingHistory(user)">
                                    History
                                </button>
                                <button
                                    type="button"
                                    class="trek-button"
                                    :disabled="updatingUserId === user.id"
                                    @click="updateUserStatus(user)"
                                >
                                    <span v-if="updatingUserId === user.id">Saving...</span>
                                    <span v-else-if="user.approval_status === 'blacklist'">Reactivate</span>
                                    <span v-else>Blacklist</span>
                                </button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <p v-else-if="!loading">No users found.</p>
    </section>
</template>

<style scoped>
section {
    padding: 1rem;
}

.section-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.search-form {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1rem 2rem;
}

.search-form input {
    flex: 1;
    min-width: 10rem;
    padding: 0.65rem;
    border: 1px solid #d6d6d6;
    border-radius: 0.5rem;
}

.users-list {
    margin: 1.5rem 2rem;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 0.8rem;
    border-bottom: 1px solid #f2f2f2;
    text-align: left;
}

th {
    background-color: #f2f2f2;
}

.user-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.trek-button {
    width: auto;
    padding: 0.65rem 1rem;
    background-color: #e9e9ed;
    color: #333;
    border: 1px solid #d6d6d6;
    border-radius: 0.5rem;
    cursor: pointer;
}

.trek-button:hover,
.trek-button.primary {
    background-color: #175cf1;
    border-color: #175cf1;
    color: white;
}

.trek-button:disabled {
    opacity: 0.6;
    cursor: wait;
}

p[role='alert'] {
    color: #b42318;
}

p[role='status'] {
    color: #16703d;
}

@media (max-width: 850px) {
    .search-form,
    .users-list {
        margin: 1rem 0;
    }

    .search-form {
        flex-wrap: wrap;
    }
}
</style>
