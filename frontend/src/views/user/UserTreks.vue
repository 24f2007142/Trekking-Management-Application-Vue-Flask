<script setup>
import { ref, onMounted, computed } from 'vue'

const treks = ref([])
const loading = ref(false)
const error = ref('')
const message = ref('')

const selectedTrek = ref(null)
const slotsBooked = ref(1)
const saving = ref(false)

const search = ref('')
const location = ref('')
const difficulty = ref('')
const duration = ref('')


const filteredTreks = computed(function () {
    const results = []
    const searchText = search.value.trim().toLowerCase()
    const locationText = location.value.trim().toLowerCase()

    for (const trek of treks.value) {
        if (!trek.trek_name.toLowerCase().includes(searchText)) {
            continue
        }

        if (!trek.location.toLowerCase().includes(locationText)) {
            continue
        }

        if (difficulty.value && trek.difficulty !== difficulty.value) {
            continue
        }

        if (duration.value && trek.duration !== Number(duration.value)) {
            continue
        }

        results.push(trek)
    }

    return results
})


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


async function loadTreks() {
    loading.value = true
    error.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/user/treks', {
            credentials: 'include'
        })

        if (!response.ok) {
            throw new Error('Failed to load treks')
        }

        const result = await response.json()
        treks.value = result.data.upcoming_treks

    } catch (err) {
        treks.value = []
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
        await loadTreks()

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
        await loadTreks()

    } catch (err) {
        error.value = err.message

    } finally {
        saving.value = false
    }
}


onMounted(loadTreks)
</script>

<template>
    <section class="treks-page">
        <template v-if="!selectedTrek">
            <h1>Available Treks</h1>
            <p>Explore upcoming treks and manage your bookings.</p>
        </template>
        <div v-if="!selectedTrek" class="filters">

            <label>Search<input v-model="search" type="search" placeholder="Trek name" /></label>
            <label>Location<input v-model="location" type="search" placeholder="Location" /></label>
            <label>Difficulty<select v-model="difficulty">
                <option value="">All</option>
                <option value="easy">Easy</option>
                <option value="moderate">Moderate</option>
                <option value="hard">Hard</option>
            </select>
        </label>
            <label>Duration (days)
                <input v-model="duration" type="number" min="1" step="1" placeholder="Any" />
            </label>
        </div>
        <p v-if="loading" role="status">Loading treks...</p>
        <p v-if="message" role="status" class="success">{{ message }}</p>
        <div v-if="error" role="alert" class="error">{{ error }}
            <button type="button" :disabled="saving || loading" @click="closeBookingForm(); loadTreks()">Retry</button>
        </div>
        <p v-if="saving" role="status">Updating booking...</p>
        <div v-if="!loading && !selectedTrek" class="table-container">
            <table aria-label="Available treks">
                <thead><tr><th scope="col">Trek</th><th scope="col">Location</th>
                    <th scope="col">Difficulty</th><th scope="col">Duration</th>
                    <th scope="col">Dates</th><th scope="col">Price / Slot</th>
                    <th scope="col">Available Slots</th><th scope="col">Booking</th></tr></thead>
                <tbody>
                    <tr v-for="trek in filteredTreks" :key="trek.trek_id">
                        <td><strong>{{ trek.trek_name }}</strong></td>
                        <td>{{ trek.location }}</td><td>{{ trek.difficulty }}</td>
                        <td>{{ trek.duration }} days</td><td>{{ trek.start_date }} – {{ trek.end_date }}</td>
                        <td>₹{{ trek.price.toLocaleString('en-IN') }}</td><td>{{ trek.available_slots }}</td>
                        <td>
                            <div v-if="trek.already_booked" class="actions">
                                <button type="button" disabled>Booked</button>
                                <span>{{ trek.slots_booked }} slot(s)</span>
                                <button type="button" class="cancel" :disabled="saving" @click="cancelBooking(trek)">Cancel</button>
                            </div>
                            <button v-else type="button"
                                :disabled="saving || !trek.bookings_open || trek.available_slots < 1"
                                @click="openBookingForm(trek)">
                                Book
                            </button>
                        </td>
                    </tr>
                    <tr v-if="filteredTreks.length === 0"><td colspan="8">No treks match your selection.</td></tr>
                </tbody>
            </table>
        </div>
        <form v-if="selectedTrek" class="booking-form" @submit.prevent="bookTrek">
            <button type="button" :disabled="saving" @click="closeBookingForm">← Back to Treks</button>
            <h1>Book {{ selectedTrek.trek_name }}</h1>
            <p>{{ selectedTrek.start_date }} · {{ selectedTrek.location }}</p>
            <p>₹{{ selectedTrek.price.toLocaleString('en-IN') }} per slot · {{ selectedTrek.available_slots }} slots available</p>

            <label for="booking-slots">Number of slots</label>
            <input id="booking-slots" v-model.number="slotsBooked" class="slots" type="number"
                min="1" :max="selectedTrek.available_slots" step="1" required :disabled="saving" />

            <p v-if="Number.isInteger(slotsBooked) && slotsBooked > 0">
                Total: ₹{{ (selectedTrek.price * slotsBooked).toLocaleString('en-IN') }}
            </p>

            <div class="actions">
                <button type="submit" :disabled="saving">
                    {{ saving ? 'Booking...' : 'Confirm Booking' }}
                </button>
            </div>
        </form>
    </section>
</template>

<style scoped>
.treks-page { padding: 1rem; }
.filters { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; margin: 1.5rem 0; }
label { display: flex; flex-direction: column; gap: 0.5rem; }
input, select { min-width: 0; padding: 0.6rem; border: 1px solid #aaa; border-radius: 0.5rem; font: inherit; }
.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
thead { background: #f2f2f2; }
th, td { padding: 1rem; text-align: left; border-bottom: 1px solid #f2f2f2; }
td p { font-size: 0.9rem; }
.actions { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; min-width: 10rem; }
.slots { width: 4rem; }
.booking-form { max-width: 40rem; padding: 1.5rem; border: 1px solid #ddd; border-radius: 1rem; }
.booking-form h1 { margin-top: 1rem; }
.booking-form label { margin-bottom: 0.5rem; }
button { padding: 0.5rem 1rem; border: 1px solid #175cf1; border-radius: 0.5rem; background: #175cf1; color: white; cursor: pointer; }
button:disabled { opacity: 0.55; cursor: not-allowed; }
.cancel { background: white; color: #b42318; border-color: #b42318; }
button:focus-visible, input:focus-visible, select:focus-visible { outline: 2px solid #175cf1; outline-offset: 3px; }
.error { color: #b42318; }
.success { color: #16703c; }
@media (max-width: 800px) { .filters { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 480px) { .filters { grid-template-columns: 1fr; } }
</style>
