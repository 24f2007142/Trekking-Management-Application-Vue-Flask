<script setup>
import { ref, onMounted } from 'vue'

const treks = ref([])
const selectedTrekId = ref('')
const participants = ref([])
const search = ref('')
const totalConfirmed = ref(0)
const loadingTreks = ref(false)
const loadingParticipants = ref(false)
const error = ref('')
const loaded = ref(false)
const removing = ref(false)
const message = ref('')

async function fetchTreks() {
    loadingTreks.value = true
    error.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/staff/treks', {
            credentials: 'include'
        })
        if (!response.ok) throw new Error('Failed to load assigned treks')

        const result = await response.json()
        treks.value = []
        for (const trek of result.data) {
            if (trek.assignment_status !== 'cancelled') {
                // A trek may have more than one assignment record.
                let alreadyAdded = false
                for (const existingTrek of treks.value) {
                    if (existingTrek.trek_id === trek.trek_id) alreadyAdded = true
                }
                if (!alreadyAdded) treks.value.push(trek)
            }
        }
    } catch (err) {
        error.value = err.message
    } finally {
        loadingTreks.value = false
    }
}

async function fetchParticipants() {
    participants.value = []
    totalConfirmed.value = 0
    loaded.value = false
    error.value = ''

    if (!selectedTrekId.value) return

    loadingParticipants.value = true
    try {
        const url = 'http://127.0.0.1:5000/api/staff/treks/' + selectedTrekId.value
            + '/participants?search=' + encodeURIComponent(search.value.trim())
        const response = await fetch(url, { credentials: 'include' })
        const result = await response.json()
        if (!response.ok) throw new Error(result.message || 'Failed to load participants')

        participants.value = result.data
        totalConfirmed.value = result.total_confirmed
        loaded.value = true
    } catch (err) {
        error.value = err.message
    } finally {
        loadingParticipants.value = false
    }
}

function changeTrek() {
    search.value = ''
    fetchParticipants()
}

function clearSearch() {
    search.value = ''
    fetchParticipants()
}

async function removeParticipant(participant) {
    if (removing.value || !confirm('Remove ' + participant.username + ' and initiate their refund?')) return
    removing.value = true
    error.value = ''
    message.value = ''
    try {
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrf_access_token='))
        const token = cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : ''
        const response = await fetch('http://127.0.0.1:5000/api/staff/treks/' + selectedTrekId.value
            + '/participants/' + participant.booking_id, {
            method: 'PATCH', credentials: 'include',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-TOKEN': token },
            body: JSON.stringify({ action: 'remove' })
        })
        const result = await response.json()
        if (!response.ok) throw new Error(result.message || 'Could not remove participant')
        message.value = result.message
        await fetchParticipants()
    } catch (err) { error.value = err.message }
    finally { removing.value = false }
}

onMounted(fetchTreks)
</script>

<template>
    <section class="participants-page">
        <h2>Participants</h2>
        <p v-if="message" role="status">{{ message }}</p>
        <p>Select an assigned trek to view its bookings and registered trekkers.</p>

        <p v-if="loadingTreks" role="status">Loading assigned treks...</p>
        <template v-else>
            <label for="participant-trek">Trek</label>
            <select id="participant-trek" v-model="selectedTrekId" :disabled="loadingParticipants || removing" @change="changeTrek">
                <option value="">Select a trek</option>
                <option v-for="trek in treks" :key="trek.trek_id" :value="trek.trek_id">
                    {{ trek.display_id }} — {{ trek.trek_name }}
                </option>
            </select>
            <p v-if="treks.length === 0 && !error">No assigned treks available.</p>

            <form v-if="selectedTrekId" class="search-form" @submit.prevent="fetchParticipants">
                <label for="participant-search">Search participants</label>
                <div class="search-controls">
                    <input id="participant-search" v-model="search" type="search" placeholder="Name or booking ID" :disabled="loadingParticipants || removing" />
                    <button type="submit" :disabled="loadingParticipants || removing">Search</button>
                    <button type="button" :disabled="loadingParticipants || removing" @click="clearSearch">Clear</button>
                </div>
            </form>
        </template>

        <div v-if="error" class="error-message" role="alert">
            <p>{{ error }}</p>
            <button v-if="selectedTrekId" type="button" @click="fetchParticipants">Try again</button>
            <button v-else type="button" @click="fetchTreks">Try again</button>
        </div>
        <p v-if="loadingParticipants" role="status">Loading participants...</p>
        <template v-else-if="loaded">
            <p><strong>Total confirmed participants: {{ totalConfirmed }}</strong> (whole trek)</p>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th scope="col">Booking ID</th>
                            <th scope="col">Name</th>
                            <th scope="col">Email</th>
                            <th scope="col">Slots Booked</th>
                            <th scope="col">Booking Status</th><th>Payment Status</th><th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="participant in participants" :key="participant.booking_id">
                            <td>{{ participant.booking_id }}</td>
                            <td>{{ participant.username }}</td>
                            <td>{{ participant.email }}</td>
                            <td>{{ participant.slots_booked }}</td>
                            <td class="booking-status">{{ participant.booking_status }}</td>
                            <td>{{ participant.payment_status }}</td>
                            <td><button v-if="participant.can_remove" :disabled="removing" @click="removeParticipant(participant)">Remove</button></td>
                        </tr>
                        <tr v-if="participants.length === 0">
                            <td colspan="7">{{ search.trim() ? 'No participants match your search.' : 'No bookings for this trek yet.' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </template>
    </section>
</template>

<style scoped>
.participants-page { padding: 1rem; }
label { display: block; font-weight: bold; margin-bottom: 0.5rem; }
input, select { padding: 0.65rem; border: 1px solid #d6d6d6; border-radius: 0.5rem; font: inherit; max-width: 100%; box-sizing: border-box; }
select { width: 25rem; }
.search-form { margin-top: 1.5rem; }
.search-controls { display: flex; flex-wrap: wrap; gap: 0.75rem; }
input { flex: 1; min-width: 10rem; }
button { padding: 0.5rem 1rem; border: 1px solid #175cf1; border-radius: 0.5rem; background: white; color: #175cf1; font: inherit; cursor: pointer; }
button:hover:not(:disabled) { background: #175cf1; color: white; }
button:disabled { cursor: not-allowed; opacity: 0.6; }
button:focus-visible, input:focus-visible, select:focus-visible { outline: 2px solid #175cf1; outline-offset: 2px; }
.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
thead { background: #f2f2f2; }
th, td { padding: 1rem; text-align: center; }
td { border-bottom: 1px solid #f2f2f2; }
.booking-status { text-transform: capitalize; }
.error-message { color: #b42318; }
</style>
