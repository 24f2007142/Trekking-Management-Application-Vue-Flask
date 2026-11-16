<script setup>
import { ref, onMounted } from 'vue'

const bookings = ref([])
const loading = ref(false)
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


async function loadBookings() {
    loading.value = true
    error.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/user/bookings', {
            credentials: 'include'
        })

        if (!response.ok) {
            throw new Error('Failed to load bookings')
        }

        const result = await response.json()
        bookings.value = result.data

    } catch (err) {
        bookings.value = []
        error.value = err.message

    } finally {
        loading.value = false
    }
}


async function cancelBooking(booking) {
    if (saving.value) {
        return
    }

    if (!confirm('Cancel your booking for ' + booking.trek_name + '?')) {
        return
    }

    saving.value = true
    error.value = ''
    message.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/user/bookings/' + booking.booking_id + '/cancel', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'X-CSRF-TOKEN': getCsrfToken()
            }
        })

        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Failed to cancel booking')
        }

        message.value = result.message
        await loadBookings()

    } catch (err) {
        error.value = err.message

    } finally {
        saving.value = false
    }
}


onMounted(loadBookings)
</script>

<template>
    <section class="bookings-page">
        <h1>My Bookings</h1>
        <p>View your bookings and track booking and trek status.</p>

        <p v-if="loading" role="status">Loading bookings...</p>
        <p v-if="saving" role="status">Cancelling booking...</p>
        <p v-if="message" role="status" class="success">{{ message }}</p>

        <div v-if="error" role="alert" class="error">
            {{ error }}
            <button type="button" :disabled="saving || loading" @click="loadBookings">Retry</button>
        </div>

        <div v-if="!loading" class="table-container">
            <table aria-label="My bookings">
                <thead>
                    <tr>
                        <th scope="col">Booking ID</th>
                        <th scope="col">Trek</th>
                        <th scope="col">Location</th>
                        <th scope="col">Booked On</th>
                        <th scope="col">Start Date</th>
                        <th scope="col">End Date</th>
                        <th scope="col">Slots</th>
                        <th scope="col">Booking Status</th><th>Payment Status</th>
                        <th scope="col">Trek Status</th>
                        <th scope="col">Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="booking in bookings" :key="booking.booking_id">
                        <td>{{ booking.booking_id }}</td>
                        <td>{{ booking.trek_name }}</td>
                        <td>{{ booking.location }}</td>
                        <td>{{ booking.booking_date }}</td>
                        <td>{{ booking.start_date }}</td>
                        <td>{{ booking.end_date }}</td>
                        <td>{{ booking.slots_booked }}</td>
                        <td>{{ booking.booking_status === 'confirmed' ? 'Booked' : booking.booking_status }}</td>
                        <td>{{ booking.payment_status }}</td>
                        <td>{{ booking.trek_status === 'upcoming' ? (booking.bookings_open ? 'Open' : 'Closed') : booking.trek_status }}</td>
                        <td>
                            <button v-if="booking.trek_status === 'upcoming' && booking.booking_status !== 'cancelled'"
                                type="button" class="cancel-button" :disabled="saving"
                                @click="cancelBooking(booking)">
                                Cancel
                            </button>
                            <span v-else>—</span>
                        </td>
                    </tr>
                    <tr v-if="bookings.length === 0 && !error">
                        <td colspan="11">You have no bookings yet.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>
</template>

<style scoped>
.bookings-page { padding: 1rem; }
.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
thead { background: #f2f2f2; }
th, td { padding: 1rem; text-align: left; border-bottom: 1px solid #f2f2f2; }
button { padding: 0.5rem 1rem; background: #175cf1; color: white; border: 1px solid #175cf1; border-radius: 0.5rem; cursor: pointer; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
button:focus-visible { outline: 2px solid #175cf1; outline-offset: 3px; }
.cancel-button { background: white; color: #b42318; border-color: #b42318; }
.error { color: #b42318; }
.success { color: #16703c; }
</style>
