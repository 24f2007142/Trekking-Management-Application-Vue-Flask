<script setup>
import { ref, onMounted } from 'vue'

const history = ref([])
const loading = ref(false)
const error = ref('')

const exporting = ref(false)
const exportMessage = ref('')
const exportError = ref('')

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



async function loadHistory() {
    loading.value = true
    error.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/user/history', {
            credentials: 'include'
        })

        if (!response.ok) {
            throw new Error('Failed to load trekking history')
        }

        const result = await response.json()
        history.value = result.data

    } catch (err) {
        history.value = []
        error.value = err.message

    } finally {
        loading.value = false
    }
}

async function exportHistory() {
    if (exporting.value) return

    exporting.value = true
    exportMessage.value = ''
    exportError.value = ''

    try {
        const response = await fetch(
            'http://127.0.0.1:5000/api/user/history/export',
            {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'X-CSRF-TOKEN': getCsrfToken(),
                },
            }
        )

        const result = await response.json()

        if (!response.ok) {
            throw new Error(
                result.message || result.msg || 'Could not request export'
            )
        }

        exportMessage.value = result.message
    } catch (err) {
        exportError.value = err.message
    } finally {
        exporting.value = false
    }
}


onMounted(loadHistory)
</script>

<template>
    <section class="history-page">
        <h1>Trekking History</h1>
        <p>View your completed treks and cancelled bookings.</p>

        <button type="button" :disabled="exporting" @click="exportHistory">

            {{ exporting ? 'Requesting export...' : 'Export history as CSV' }}

        </button>

        <p v-if="exportMessage" role="status">
            {{ exportMessage }}
        </p>

        <p v-if="exportError" role="alert" class="error">
            {{ exportError }}
        </p>

        <p v-if="loading" role="status">Loading trekking history...</p>

        <div v-if="error" role="alert" class="error">
            {{ error }}
            <button type="button" :disabled="loading" @click="loadHistory">Retry</button>
        </div>

        <div v-if="!loading" class="table-container">
            <table aria-label="Trekking history">
                <thead>
                    <tr>
                        <th scope="col">Booking ID</th>
                        <th scope="col">Booked On</th>
                        <th scope="col">Trek</th>
                        <th scope="col">Location</th>
                        <th scope="col">Difficulty</th>
                        <th scope="col">Duration</th>
                        <th scope="col">Start Date</th>
                        <th scope="col">End Date</th>
                        <th scope="col">Slots</th>
                        <th scope="col">Booking Status</th><th scope="col">Payment Status</th><th scope="col">Trek Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="trek in history" :key="trek.booking_id">
                        <td>{{ trek.booking_id }}</td>
                        <td>{{ trek.booking_date }}</td>
                        <td>{{ trek.trek_name }}</td>
                        <td>{{ trek.location }}</td>
                        <td>{{ trek.difficulty }}</td>
                        <td>{{ trek.duration }} days</td>
                        <td>{{ trek.start_date }}</td>
                        <td>{{ trek.end_date }}</td>
                        <td>{{ trek.slots_booked }}</td>
                        <td>{{ trek.booking_status === 'confirmed' ? 'Booked' : trek.booking_status }}</td><td>{{ trek.payment_status }}</td><td>{{ trek.trek_status === 'upcoming' ? (trek.bookings_open ? 'Open' : 'Closed') : trek.trek_status }}</td>
                    </tr>
                    <tr v-if="history.length === 0 && !error">
                        <td colspan="12">You have no completed treks or cancelled bookings yet.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>
</template>

<style scoped>
.history-page { padding: 1rem; }
.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
thead { background: #f2f2f2; }
th, td { padding: 1rem; text-align: left; border-bottom: 1px solid #f2f2f2; }
button { padding: 0.5rem 1rem; background: #175cf1; color: white; border: 1px solid #175cf1; border-radius: 0.5rem; cursor: pointer; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
button:focus-visible { outline: 2px solid #175cf1; outline-offset: 3px; }
.error { color: #b42318; }
</style>
