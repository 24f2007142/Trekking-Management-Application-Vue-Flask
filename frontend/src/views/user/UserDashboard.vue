<script setup>
import { ref, onMounted } from 'vue'

const dashboard = ref(null)
const loading = ref(false)
const error = ref('')
const message = ref('')

const selectedTrek = ref(null)
const slotsBooked = ref(1)
const saving = ref(false)


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


async function loadDashboard() {
    loading.value = true
    error.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/user/dashboard', {
            credentials: 'include'
        })

        if (!response.ok) {
            throw new Error('Failed to load dashboard')
        }

        const result = await response.json()
        dashboard.value = result.data

    } catch (err) {
        dashboard.value = null
        error.value = err.message

    } finally {
        loading.value = false
    }
}


function openBookingForm(trek) {
    selectedTrek.value = trek
    slotsBooked.value = 1
    error.value = ''
    message.value = ''
    window.scrollTo(0, 0)
}


function closeBookingForm() {
    selectedTrek.value = null
    error.value = ''
}


async function bookTrek() {
    if (saving.value || !selectedTrek.value) {
        return
    }

    const trek = selectedTrek.value

    if (!Number.isInteger(slotsBooked.value) || slotsBooked.value < 1 || slotsBooked.value > trek.available_slots) {
        error.value = 'Choose a valid number of available slots.'
        return
    }

    if (!confirm('Book ' + slotsBooked.value + ' slot(s) for ' + trek.trek_name + '?')) {
        return
    }

    saving.value = true
    error.value = ''
    message.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/user/treks/' + trek.trek_id + '/book', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCsrfToken()
            },
            body: JSON.stringify({ slots_booked: slotsBooked.value })
        })

        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Failed to book trek')
        }

        selectedTrek.value = null
        message.value = result.message
        await loadDashboard()

    } catch (err) {
        error.value = err.message

    } finally {
        saving.value = false
    }
}


async function cancelBooking(trek) {
    if (saving.value) {
        return
    }

    if (!confirm('Cancel your booking for ' + trek.trek_name + '?')) {
        return
    }

    saving.value = true
    error.value = ''
    message.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/user/bookings/' + trek.booking_id + '/cancel', {
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
        await loadDashboard()

    } catch (err) {
        error.value = err.message

    } finally {
        saving.value = false
    }
}


onMounted(loadDashboard)
</script>

<template>
    <section class="dashboard">
        <h1 v-if="!selectedTrek">User Dashboard</h1>
        <p v-if="loading" role="status">Loading dashboard...</p>
        <div v-if="error" role="alert" class="error">
            {{ error }}
            <button type="button" :disabled="saving || loading" @click="closeBookingForm(); loadDashboard()">Retry</button>
        </div>
        <p v-if="message" role="status" class="success">{{ message }}</p>

        <template v-if="dashboard && !selectedTrek">
            <div v-for="notice in dashboard.notifications" :key="notice.booking_id" role="status">
                <p>You were removed from {{ notice.trek_name }} by staff member
                    {{ notice.staff_name }}. Refund status: {{ notice.payment_status }}.</p>
            </div>
            <div class="stats">
                <div class="stat"><h3>Total Bookings</h3><p>{{ dashboard.total_bookings }}</p></div>
                <div class="stat"><h3>Upcoming Treks</h3><p>{{ dashboard.upcoming_treks_count }}</p></div>
                <div class="stat"><h3>Completed Treks</h3><p>{{ dashboard.completed_treks_count }}</p></div>
            </div>

            <h2>Recent Treks</h2>

            <div class="table-container">
                <table aria-label="Recent available treks">
                    <thead><tr>
                        <th scope="col">Trek</th><th scope="col">Location</th>
                        <th scope="col">Difficulty</th><th scope="col">Duration</th>
                        <th scope="col">Start Date</th><th scope="col">Price / Slot</th>
                        <th scope="col">Available Slots</th><th scope="col">Book</th>
                    </tr></thead>
                    <tbody>
                        <tr v-for="trek in dashboard.recent_treks_list" :key="trek.trek_id">
                            <td>{{ trek.trek_name }}</td><td>{{ trek.location }}</td>
                            <td>{{ trek.difficulty }}</td><td>{{ trek.duration }} days</td>
                            <td>{{ trek.start_date }}</td><td>₹{{ trek.price.toLocaleString('en-IN') }}</td>
                            <td>{{ trek.available_slots }}</td>
                            <td>
                                <span v-if="trek.already_booked">Already booked</span>
                                <button v-else type="button" :disabled="saving || loading" @click="openBookingForm(trek)">
                                    Book
                                </button>
                            </td>
                        </tr>
                        <tr v-if="dashboard.recent_treks_list.length === 0">
                            <td colspan="8">No treks available for booking right now.</td>
                        </tr>
                    </tbody>
                </table>
            </div>



            <h2>My Upcoming Treks</h2>
            <div class="table-container">
                <table aria-label="My upcoming treks">
                    <thead><tr><th scope="col">Trek</th><th scope="col">Location</th>
                        <th scope="col">Start Date</th><th scope="col">Slots</th>
                        <th scope="col">Booking Status</th><th scope="col">Trek Status</th>
                        <th scope="col">Action</th></tr></thead>
                    <tbody>
                        <tr v-for="trek in dashboard.upcoming_treks_list" :key="trek.booking_id">
                            <td>{{ trek.trek_name }}</td><td>{{ trek.location }}</td>
                            <td>{{ trek.start_date }}</td><td>{{ trek.slots_booked }}</td>
                            <td>{{ trek.booking_status }}</td><td>{{ trek.trek_status }}</td>
                            <td>
                                <button type="button" class="cancel-button"
                                    :disabled="saving || loading" @click="cancelBooking(trek)">
                                    Cancel
                                </button>
                            </td>
                        </tr>
                        <tr v-if="dashboard.upcoming_treks_list.length === 0">
                            <td colspan="7">You have no upcoming treks.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </template>

        <form v-if="selectedTrek" class="booking-form" @submit.prevent="bookTrek">
            <button type="button" :disabled="saving || loading" @click="closeBookingForm">
                ← Back to Dashboard
            </button>
            <h1 >Book {{ selectedTrek.trek_name }}</h1>
            <p>{{ selectedTrek.start_date }} · {{ selectedTrek.location }}</p>
            <p>₹{{ selectedTrek.price.toLocaleString('en-IN') }} per slot · {{ selectedTrek.available_slots }} slots available</p>

            <label for="booking-slots">Number of slots</label>
            <input id="booking-slots" v-model.number="slotsBooked" type="number" min="1"
                :max="selectedTrek.available_slots" step="1" required :disabled="saving || loading" />

            <p v-if="Number.isInteger(slotsBooked) && slotsBooked > 0">
                Total: ₹{{ (selectedTrek.price * slotsBooked).toLocaleString('en-IN') }}
            </p>

            <div class="booking-actions">
                <button type="submit" :disabled="saving || loading">
                    {{ saving ? 'Booking...' : 'Confirm Booking' }}
                </button>
            </div>
        </form>
    </section>
</template>

<style scoped>
.dashboard { padding: 1rem; }
.stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
.stat { border: 0.2rem solid #f2f2f2; border-radius: 2rem; padding: 1rem; }
.stat p { font-size: 2rem; font-weight: bold; margin: 0; color: #175cf1; }
h2 { margin-top: 2rem; }
.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
thead { background: #f2f2f2; }
th, td { padding: 1rem; text-align: left; border-bottom: 1px solid #f2f2f2; }
.booking-form { max-width: 40rem; padding: 1.5rem; border: 1px solid #ddd; border-radius: 1rem; }
.booking-form h1 { margin-top: 1rem; }
.booking-form label { display: block; margin-bottom: 0.5rem; }
.booking-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
input { width: 4rem; padding: 0.5rem; border: 1px solid #aaa; border-radius: 0.5rem; }
button { padding: 0.5rem 1rem; background: #175cf1; color: white; border: 1px solid #175cf1; border-radius: 0.5rem; cursor: pointer; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.cancel-button { background: white; color: #b42318; border-color: #b42318; }
button:focus-visible, input:focus-visible { outline: 2px solid #175cf1; outline-offset: 3px; }
.error { color: #b42318; }
.success { color: #16703c; }
@media (max-width: 700px) { .stats { grid-template-columns: 1fr; } }
</style>
