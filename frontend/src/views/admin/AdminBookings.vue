<script setup>
import { ref, onMounted } from 'vue'

const bookings = ref([])
const displayedBookings = ref([])
const searchText = ref('')
const loading = ref(false)
const error = ref('')

async function fetchBookings() {
    loading.value = true
    error.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/all-bookings', {
            credentials: 'include'
        })
        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Could not load bookings')
        }

        bookings.value = result.data
        displayedBookings.value = result.data
    } catch (err) {
        error.value = err.message
    } finally {
        loading.value = false
    }
}

function searchBookings() {
    const search = searchText.value.trim().toLowerCase()

    if (!search) {
        displayedBookings.value = bookings.value
        return
    }

    displayedBookings.value = []

    for (const booking of bookings.value) {
        const bookingIdMatches = String(booking.id).includes(search)
        const userIdMatches = String(booking.user_id).includes(search)
        const trekIdMatches = String(booking.trek_id).includes(search)
        const statusMatches = booking.status.toLowerCase().includes(search)

        if (bookingIdMatches || userIdMatches || trekIdMatches || statusMatches) {
            displayedBookings.value.push(booking)
        }
    }
}

onMounted(fetchBookings)
</script>

<template>
    <section>
        <div class="section-heading">
            <h2>Manage Bookings</h2>
        </div>

        <form class="search-form" @submit.prevent="searchBookings">
            <input
                v-model="searchText"
                type="search"
                placeholder="Search by booking, user, or trek ID or status"
                aria-label="Search bookings"
            >
            <button type="submit" class="trek-button primary">Search</button>
        </form>

        <p v-if="loading">Loading bookings...</p>
        <p v-else-if="error" role="alert">{{ error }}</p>

        <div v-else-if="displayedBookings.length" class="bookings-list">
            <table>
                <thead>
                    <tr>
                        <th>Booking ID</th>
                        <th>User ID</th>
                        <th>Trek ID</th>
                        <th>Booking Date</th>
                        <th>Slots Booked</th>
                        <th>Status</th><th>Payment Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="booking in displayedBookings" :key="booking.id">
                        <td>{{ booking.id }}</td>
                        <td>{{ booking.user_id }}</td>
                        <td>{{ booking.trek_id }}</td>
                        <td>{{ booking.booking_date }}</td>
                        <td>{{ booking.slots_booked }}</td>
                        <td>{{ booking.status }}</td>
                        <td>{{ booking.payment_status }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <p v-else-if="!loading">No bookings found.</p>
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

.bookings-list {
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

.trek-button {
    width: auto;
    padding: 0.65rem 1rem;
    background-color: #e9e9ed;
    color: #333;
    border: 1px solid #d6d6d6;
    border-radius: 0.5rem;
    cursor: pointer;
}

.trek-button.primary {
    background-color: #175cf1;
    border-color: #175cf1;
    color: white;
}

p[role='alert'] {
    color: #b42318;
}

@media (max-width: 850px) {
    .search-form,
    .bookings-list {
        margin: 1rem 0;
    }

    .search-form {
        flex-wrap: wrap;
    }
}
</style>
