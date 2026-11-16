<script setup>
import { ref, onMounted } from 'vue'

const treks = ref([])
const selectedTrek = ref(null)
const error = ref('')
const loading = ref(false)
const loadingDetails = ref(false)
const detailsError = ref('')
const totalSlots = ref(1)
const savingSlots = ref(false)
const slotsError = ref('')
const slotsMessage = ref('')
const bookingsOpen = ref(false)
const savingBookings = ref(false)
const bookingsError = ref('')
const bookingsMessage = ref('')
const savingStatus = ref(false)
const statusError = ref('')
const statusMessage = ref('')
const trekStatus = ref('upcoming')

async function fetchTreks() {
    loading.value = true
    error.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/staff/treks', {
            credentials: 'include'
        })

        if (!response.ok) throw new Error('Failed to load assigned treks')

        const result = await response.json()
        treks.value = result.data
    } catch (err) {
        error.value = err.message
    } finally {
        loading.value = false
    }
}

function canManage(trek) {
    return ['assigned', 'completed'].includes(trek.assignment_status)
}

async function manageTrek(trek) {
    if (!canManage(trek) || loadingDetails.value || savingSlots.value || savingBookings.value || savingStatus.value) return

    loadingDetails.value = true
    detailsError.value = ''
    statusError.value = ''
    statusMessage.value = ''
    selectedTrek.value = null
    bookingsError.value = ''
    bookingsMessage.value = ''
    slotsError.value = ''
    slotsMessage.value = ''

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/staff/treks/${trek.trek_id}`, {
            credentials: 'include'
        })
        const result = await response.json()

        if (!response.ok) throw new Error(result.message || 'Failed to load trek details')

        trekStatus.value = result.data.trek_status
        selectedTrek.value = result.data
        totalSlots.value = result.data.total_slots
        bookingsOpen.value = result.data.bookings_open
    } catch (err) {
        detailsError.value = err.message
    } finally {
        loadingDetails.value = false
    }
}

function getCsrfToken() {
    const cookie = document.cookie.split('; ')
        .find(row => row.startsWith('csrf_access_token='))
    return cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : ''
}

async function updateSlots() {
    if (!selectedTrek.value || savingSlots.value || savingBookings.value || savingStatus.value || !canManage(selectedTrek.value) || !['approved', 'upcoming'].includes(selectedTrek.value.trek_status)) return

    slotsError.value = ''
    slotsMessage.value = ''

    if (!Number.isInteger(totalSlots.value) || totalSlots.value < 1) {
        slotsError.value = 'Total slots must be a positive whole number.'
        return
    }

    if (totalSlots.value < selectedTrek.value.booked_slots) {
        slotsError.value = 'Total slots cannot be less than registered participants.'
        return
    }

    savingSlots.value = true

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/staff/treks/${selectedTrek.value.trek_id}/slots`, {
            method: 'PATCH',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCsrfToken()
            },
            body: JSON.stringify({ total_slots: totalSlots.value })
        })
        const result = await response.json()

        if (!response.ok) throw new Error(result.message || 'Failed to update trek slots')

        Object.assign(selectedTrek.value, result.data)
        for (const trek of treks.value) {
            if (trek.trek_id === result.data.trek_id) Object.assign(trek, result.data)
        }
        totalSlots.value = result.data.total_slots
        slotsMessage.value = result.message
    } catch (err) {
        slotsError.value = err.message
    } finally {
        savingSlots.value = false
    }
}

async function updateBookingsStatus() {
    if (!selectedTrek.value || savingBookings.value || savingSlots.value || savingStatus.value || !canManage(selectedTrek.value) || !['approved', 'upcoming'].includes(selectedTrek.value.trek_status)) return

    bookingsError.value = ''
    bookingsMessage.value = ''
    savingBookings.value = true

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/staff/treks/${selectedTrek.value.trek_id}/bookings-status`, {
            method: 'PATCH',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCsrfToken()
            },
            body: JSON.stringify({ bookings_open: bookingsOpen.value })
        })
        const result = await response.json()

        if (!response.ok) throw new Error(result.message || 'Failed to update booking status')

        Object.assign(selectedTrek.value, result.data)
        for (const trek of treks.value) {
            if (trek.trek_id === result.data.trek_id) Object.assign(trek, result.data)
        }
        bookingsOpen.value = result.data.bookings_open
        trekStatus.value = result.data.trek_status
        bookingsMessage.value = result.message
    } catch (err) {
        bookingsError.value = err.message
    } finally {
        savingBookings.value = false
    }
}

async function updateTrekStatus(trek) {
    if (savingStatus.value || savingSlots.value || savingBookings.value || loadingDetails.value) return
    if (!canManage(trek)) return

    statusError.value = ''
    statusMessage.value = ''
    savingStatus.value = true

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/staff/treks/${trek.trek_id}/status`, {
            method: 'PATCH',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCsrfToken()
            },
            body: JSON.stringify({ trek_status: trekStatus.value })
        })
        const result = await response.json()

        if (!response.ok) throw new Error(result.message || 'Failed to update trek status')

        for (const row of treks.value) {
            if (row.trek_id === trek.trek_id) {
                row.trek_status = result.data.trek_status
                row.bookings_open = result.data.bookings_open
                if (row.assignment_status !== 'cancelled') {
                    row.assignment_status = result.data.assignment_status
                }
            }
        }
        Object.assign(trek, result.data)
        bookingsOpen.value = result.data.bookings_open
        statusMessage.value = result.message
    } catch (err) {
        statusError.value = err.message
    } finally {
        savingStatus.value = false
    }
}

onMounted(fetchTreks)
</script>

<template>
    <section class="treks-page">
        <div class="section-heading">
            <h2>My Treks</h2>
            <div class="line"></div>
        </div>
        <p class="page-description">View your assigned treks, registered participants, and available slots.</p>

        <p v-if="loading" role="status">Loading assigned treks...</p>
        <div v-else-if="error" class="error-message" role="alert">
            <p>{{ error }}</p>
            <button type="button" class="trek-button" @click="fetchTreks">Try again</button>
        </div>
        <template v-else>
            <template v-if="!selectedTrek">
            <div class="table-container">
                <table aria-label="Assigned treks">
                    <thead>
                        <tr>
                            <th scope="col">Trek ID</th>
                            <th scope="col">Trek Name</th>
                            <th scope="col">Location</th>
                            <th scope="col">Start Date</th>
                            <th scope="col">Registered</th>
                            <th scope="col">Available Slots</th>
                            <th scope="col">Bookings</th>
                            <th scope="col">Trek Status</th>
                            <th scope="col">Assignment</th>
                            <th scope="col">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(trek, index) in treks" :key="index">
                            <td>{{ trek.display_id }}</td>
                            <td class="trek-name">{{ trek.trek_name }}</td>
                            <td>{{ trek.location }}</td>
                            <td class="date-cell">{{ trek.start_date }}</td>
                            <td>{{ trek.assignment_status != 'cancelled' ? trek.booked_slots : '--' }}</td>
                            <td>{{trek.assignment_status != 'cancelled' ? trek.available_slots : '--' }}</td>
                            <td>{{ trek.assignment_status != 'cancelled' ? trek.bookings_open ? 'Open' : 'Closed'  : '--'}}</td>
                            <td><span class="status" :class="trek.trek_status">{{ trek.assignment_status != 'cancelled' ? trek.trek_status : 'Unavailable'}}</span></td>
                            <td><span class="status" :class="trek.assignment_status">{{ trek.assignment_status }}</span></td>
                            <td>
                                <button
                                    type="button"
                                    class="trek-button"
                                    :disabled="!canManage(trek) || loadingDetails || savingSlots || savingBookings || savingStatus"
                                    :title="canManage(trek) ? 'View trek summary' : 'Cancelled staff assignments cannot manage treks'"
                                    @click="manageTrek(trek)"
                                >Manage</button>

                            </td>
                        </tr>
                        <tr v-if="treks.length === 0">
                            <td colspan="10" class="empty-state">No treks assigned yet.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <p v-if="treks.length" class="table-note">All assignments remain visible for your records. Cancelled staff assignments cannot manage treks.</p>
            <p v-if="loadingDetails" role="status">Loading trek details...</p>
            <p v-if="detailsError" class="error-message" role="alert">{{ detailsError }}</p>

            </template>

            <section v-else class="trek-summary" aria-labelledby="summary-heading">
                <div class="section-heading">
                    <h3 id="summary-heading">{{ selectedTrek.trek_name }} — Manage Trek</h3>
                    <button type="button" class="trek-button" :disabled="savingSlots || savingBookings || savingStatus" @click="selectedTrek = null">Back to My Treks</button>
                </div>
                <dl class="summary-details">
                    <div><dt>Trek ID</dt><dd>{{ selectedTrek.display_id }}</dd></div>
                    <div><dt>Location</dt><dd>{{ selectedTrek.location }}</dd></div>
                    <div><dt>Difficulty</dt><dd class="capitalize">{{ selectedTrek.difficulty }}</dd></div>
                    <div><dt>Duration</dt><dd>{{ selectedTrek.duration }} days</dd></div>
                    <div><dt>Start Date</dt><dd>{{ selectedTrek.start_date }}</dd></div>
                    <div><dt>End Date</dt><dd>{{ selectedTrek.end_date }}</dd></div>
                    <div><dt>Total Slots</dt><dd>{{ selectedTrek.total_slots }}</dd></div>
                    <div><dt>Registered Participants</dt><dd>{{ selectedTrek.booked_slots }}</dd></div>
                </dl>
                <form v-if="['approved', 'upcoming'].includes(selectedTrek.trek_status)" class="slots-form" @submit.prevent="updateSlots">
                    <label for="total-slots">Total Slots</label>
                    <div class="slots-controls">
                        <input
                            id="total-slots"
                            v-model.number="totalSlots"
                            type="number"
                            :min="Math.max(1, selectedTrek.booked_slots)"
                            step="1"
                            required
                            :disabled="savingSlots || savingBookings || savingStatus"
                            aria-describedby="slots-help"
                        />
                        <button type="submit" class="trek-button" :disabled="savingSlots || savingBookings || savingStatus">
                            {{ savingSlots ? 'Saving...' : 'Update total Slots' }}
                        </button>
                    </div>
                    <p id="slots-help" class="table-note">Total capacity includes registered participants. Currently available: {{ selectedTrek.available_slots }} slots.</p>
                    <p v-if="slotsError" class="error-message" role="alert">{{ slotsError }}</p>
                    <p v-if="slotsMessage" class="success-message" role="status">{{ slotsMessage }}</p>
                </form>
                <form v-if="['approved', 'upcoming'].includes(selectedTrek.trek_status)" class="slots-form" @submit.prevent="updateBookingsStatus">
                    <label for="bookings-status">Bookings</label>
                    <div class="slots-controls">
                        <select id="bookings-status" v-model="bookingsOpen" :disabled="savingBookings || savingSlots || savingStatus" aria-describedby="bookings-help">
                            <option :value="true">Open</option>
                            <option :value="false">Closed</option>
                        </select>
                        <button type="submit" class="trek-button" :disabled="savingBookings || savingSlots || savingStatus">
                            {{ savingBookings ? 'Saving...' : 'Update Booking Status' }}
                        </button>
                    </div>
                    <p id="bookings-help" class="table-note">Current booking status: {{ selectedTrek.bookings_open ? 'Open' : 'Closed' }}. Closing bookings does not cancel existing registrations.</p>
                    <p v-if="bookingsError" class="error-message" role="alert">{{ bookingsError }}</p>
                    <p v-if="bookingsMessage" class="success-message" role="status">{{ bookingsMessage }}</p>
                </form>
                <div class="slots-form">
                    <h3>Trek Status</h3>
                    <p>Current status: <span class="status" :class="selectedTrek.trek_status">{{ selectedTrek.trek_status }}</span></p>
                    <label for="trek-status">Trek Status</label>
                    <div class="slots-controls">
                        <select id="trek-status" v-model="trekStatus" :disabled="savingStatus || savingSlots || savingBookings">
                            <option :value="selectedTrek.trek_status">{{ selectedTrek.trek_status }}</option>
                            <option v-if="selectedTrek.trek_status === 'upcoming'" value="ongoing">Ongoing</option>
                            <option v-if="['upcoming', 'ongoing'].includes(selectedTrek.trek_status)" value="completed">Completed</option>
                            <option v-if="!['completed', 'cancelled'].includes(selectedTrek.trek_status)" value="cancelled">Cancelled</option>
                        </select>
                        <button type="button" class="trek-button"
                            :disabled="savingStatus || savingSlots || savingBookings"
                            @click="updateTrekStatus(selectedTrek)"
                        >{{ savingStatus ? 'Updating...' : 'Update Trek Status' }}</button>
                    </div>
                    <p class="table-note">Open bookings after admin approval. Start or complete an upcoming trek. Completed and cancelled treks cannot be reopened.</p>
                    <p v-if="statusError" class="error-message" role="alert">{{ statusError }}</p>
                    <p v-if="statusMessage" class="success-message" role="status">{{ statusMessage }}</p>
                </div>
            </section>
        </template>
    </section>
</template>

<style scoped>
.treks-page {
    padding: 1rem;
    min-width: 0;
}

.section-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.line {
    flex: 1;
    border-top: 0.05rem solid #f2f2f2;
}

.page-description,
.table-note {
    color: #595959;
    line-height: 1.5;
}

.page-description {
    margin: 0 0 1.5rem;
}

.table-container {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

thead {
    background-color: #f2f2f2;
}

th,
td {
    padding: 1rem;
    text-align: center;
}

td {
    border-bottom: 1px solid #f2f2f2;
}

tbody tr:hover {
    background-color: #fafafa;
}

.trek-name {
    min-width: 9rem;
}

.date-cell {
    white-space: nowrap;
}

.trek-button {
    padding: 0.5rem 1rem;
    border: 1px solid #175cf1;
    border-radius: 0.5rem;
    background: white;
    color: #175cf1;
    font: inherit;
    cursor: pointer;
}

.trek-button:hover:not(:disabled) {
    background: #175cf1;
    color: white;
}

.trek-button:focus-visible {
    outline: 2px solid #175cf1;
    outline-offset: 3px;
}

.trek-button:disabled {
    background: #f2f2f2;
    border-color: #d6d6d6;
    color: #666;
    cursor: not-allowed;
}

.status {
    display: inline-block;
    padding: 0.3rem 0.6rem;
    border-radius: 0.5rem;
    background: #f2f2f2;
    text-transform: capitalize;
}

.status.assigned,
.status.upcoming {
    background: #edf3ff;
    color: #175cf1;
}

.status.ongoing {
    background: #edf7ee;
    color: #216e39;
}

.status.cancelled {
    background: #fff0ef;
    color: #b42318;
}

.empty-state,
.error-message {
    color: #b42318;
}

.trek-summary {
    margin-top: 1.5rem;
    padding: 1rem;
    border: 0.2rem solid #f2f2f2;
    border-radius: 1rem;
}

.summary-details {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1.5rem;
}

dt {
    font-weight: bold;
}

dd {
    margin: 0.5rem 0 0;
    overflow-wrap: anywhere;
}

.capitalize {
    text-transform: capitalize;
}

.slots-form {
    border-top: 1px solid #f2f2f2;
    padding-top: 1rem;
}

.slots-form label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
}

.slots-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.slots-controls input,
.slots-controls select {
    width: 8rem;
    padding: 0.65rem;
    border: 1px solid #d6d6d6;
    border-radius: 0.5rem;
    font: inherit;
}

.slots-controls input:focus-visible,
.slots-controls select:focus-visible {
    outline: 2px solid #175cf1;
    outline-offset: 2px;
}

.success-message {
    color: #216e39;
}

@media (max-width: 800px) {
    .summary-details {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 480px) {
    .summary-details {
        grid-template-columns: 1fr;
    }

    .section-heading {
        flex-wrap: wrap;
    }
}
</style>
