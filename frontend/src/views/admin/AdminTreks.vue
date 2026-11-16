<script setup>
import { ref, reactive, onMounted } from 'vue'


const API = 'http://127.0.0.1:5000/api/admin/treks'

const treks = ref([])
const selectedTrek = ref(null)
const isEditing = ref(false)
const status = ref('')
const showForm = ref(false)
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const message = ref('')
const searchText = ref('')
const assignmentTrek = ref(null)
const availableStaff = ref([])
const staffSearchText = ref('')
const assignedStaff = ref([])
const selectedStaffId = ref('')
const loadingAssignments = ref(false)
const searchingStaff = ref(false)
const searched = ref(false)
const savingAssignment = ref(false)
const cancellingAssignmentId = ref(null)
let staffSearchTimer = null

function getCsrfToken() {
    const cookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrf_access_token='))

    return cookie
        ? decodeURIComponent(cookie.split('=').slice(1).join('='))
        : ''
}

const form = reactive({
    trek_name: '',
    location: '',
    difficulty: '',
    duration: '',
    start_date: '',
    end_date: '',
    total_slots: '',
    price: '',
    description: '',
    bookings_open: true
})

function resetForm() {
    form.trek_name = ''
    form.location = ''
    form.difficulty = ''
    form.duration = ''
    form.start_date = ''
    form.end_date = ''
    form.total_slots = ''
    form.price = ''
    form.description = ''
    form.bookings_open = true
}

function cancelForm() {
    resetForm()
    showForm.value = false
    error.value = ''
}



async function approveTrek(trek) {
    error.value = ''
    saving.value = true
    try {
        const response = await fetch(`${API}/${trek.id}/approve`, {
            method: 'PATCH', credentials: 'include',
            headers: { 'X-CSRF-TOKEN': getCsrfToken() }
        })
        const result = await response.json()
        if (!response.ok) throw new Error(result.message || 'Approval failed')
        message.value = result.message
        selectedTrek.value = null
        await fetchTreks()
    } catch (err) { error.value = err.message }
    finally { saving.value = false }
}

async function fetchTreks(search = searchText.value) {
    loading.value = true
    error.value = ''
    try {
        const url = new URL(API)
        url.searchParams.set('search', search)

        const response = await fetch(url, {
            credentials: 'include'
        })

        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Failed to load treks')}

        treks.value = result.data
    } catch (err) {
        error.value = err.message
    } finally {
        loading.value = false
    }
}

async function createTrek() {
    error.value = ''
    message.value = ''
    if (form.end_date < form.start_date) {
        error.value = 'End date cannot be before start date'
        return
    }
    saving.value = true
    try {
        const response = await fetch(API, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCsrfToken()
            },
            body: JSON.stringify(form)
        })
        const result = await response.json()
        if (!response.ok) throw new Error(result.message || 'Failed to create trek')
        message.value = result.message || 'Trek added successfully'
        cancelForm()
        await fetchTreks()
    } catch (err) {
        error.value = err.message
    } finally {
        saving.value = false
    }
}

async function fullInfo(trekID) {
    error.value = ''
    selectedTrek.value = null
    isEditing.value = false

    try {
        const response = await fetch(`${API}/${trekID}`, {
            credentials: 'include'
        })

        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Failed to load trek')
        }

        selectedTrek.value = result.data

    } catch (err) {
        error.value = err.message
    }
}

async function editTrek(trekId) {

    selectedTrek.value = null
    isEditing.value = false

    await fullInfo(trekId)

    if (selectedTrek.value) {
        startEditing()
    }
}

function backToTreks() {
    selectedTrek.value = null
    isEditing.value = false
}

function startEditing() {

    Object.assign(form, {
        trek_name: selectedTrek.value.trek_name,
        location: selectedTrek.value.location,
        difficulty: selectedTrek.value.difficulty,
        duration: selectedTrek.value.duration,
        start_date: selectedTrek.value.start_date,
        end_date: selectedTrek.value.end_date,
        total_slots: selectedTrek.value.total_slots,
        price: selectedTrek.value.price,
        description: selectedTrek.value.description || '',
        bookings_open: selectedTrek.value.bookings_open
    })

    isEditing.value = true
}

async function saveTrek() {

    error.value = ''
    message.value = ''

    if (form.end_date < form.start_date) {
        error.value = 'End date cannot be before start date'
        return
    }

    saving.value = true

    try {
        const response = await fetch(`${API}/${selectedTrek.value.id}`, {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCsrfToken()
            },
            body: JSON.stringify(form)
        })

        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || result.msg || 'Failed to update trek')
        }

        message.value = result.message || 'Trek updated successfully'


        await fullInfo(selectedTrek.value.id)


        if (selectedTrek.value) {
            isEditing.value = false
            selectedTrek.value = null
        }


        await fetchTreks()

    } catch (err) {
        error.value = err.message
    } finally {
        saving.value = false
    }
}

async function deleteTrek(trek_id){

    error.value=''

    if (!confirm('Are you sure you want to delete this trek?')) {
        return
    }

    try{ const response = await fetch(`${API}/${trek_id}`,{
        method: 'DELETE',
        credentials: 'include',
        headers: {
                'X-CSRF-TOKEN': getCsrfToken()
            }
    })

    const result = await response.json()



    if (!response.ok) {
            throw new Error(result.message || 'Failed to delete trek')
        }

        message.value = result.message || 'Trek deleted successfully'

        await fetchTreks()

    } catch (err) {
        error.value = err.message
    }
}

async function openStaffAssignment(trek) {
    error.value = ''
    message.value = ''
    assignmentTrek.value = trek
    selectedStaffId.value = ''
    staffSearchText.value = ''
    availableStaff.value = []
    searched.value = false
    loadingAssignments.value = true

    try {
        await fetchAssignedStaff(trek.id)
    } catch (err) {
        error.value = err.message
    } finally {
        loadingAssignments.value = false
    }
}

async function searchAvailableStaff() {
    const search = staffSearchText.value.trim()

    if (!search) {
        searched.value = false
        error.value = ''
        availableStaff.value = []
        return
    }

    error.value = ''
    searched.value = false
    availableStaff.value = []
    selectedStaffId.value = ''
    searchingStaff.value = true

    try {
        const url = new URL('http://127.0.0.1:5000/api/admin/staffs')
        url.searchParams.set('search', search)

        const response = await fetch(url, { credentials: 'include' })
        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Could not search staff')
        }



        if (search !== staffSearchText.value.trim()) {
            return
        }

        availableStaff.value = result.data.filter(staff => {
            const isApproved = staff.approval_status === 'approved'
            const hasProfile = staff.staff_id
            const alreadyAssigned = assignedStaff.value.some(
                assigned => assigned.staff_id === staff.staff_id
            )

            return isApproved && hasProfile && !alreadyAssigned
        })
        searched.value = true
    } catch (err) {
        error.value = err.message
    } finally {
        searchingStaff.value = false
    }
}

function clearStaffSearchResults() {
    clearTimeout(staffSearchTimer)
    searched.value = false
    selectedStaffId.value = ''
    availableStaff.value = []
    error.value = ''

    if (staffSearchText.value.trim()) {
        staffSearchTimer = setTimeout(searchAvailableStaff, 300)
    }
}

async function fetchAssignedStaff(trekId) {
    const response = await fetch(`${API}/${trekId}/staff`, {
        credentials: 'include'
    })
    const result = await response.json()

    if (!response.ok) {
        throw new Error(result.message || 'Could not load assigned staff')
    }

    assignedStaff.value = result.data
    searched.value = false
}

async function assignStaff() {
    if (!assignmentTrek.value || !selectedStaffId.value) {
        error.value = 'Select a staff member first'
        return
    }

    error.value = ''
    message.value = ''
    savingAssignment.value = true

    try {
        const assignedStaffId = Number(selectedStaffId.value)
        const response = await fetch(`${API}/${assignmentTrek.value.id}/staff`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCsrfToken()
            },
            body: JSON.stringify({ staff_id: Number(selectedStaffId.value) })
        })
        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Could not assign staff')
        }

        message.value = result.message || 'Staff assigned successfully'
        selectedStaffId.value = ''
        await fetchAssignedStaff(assignmentTrek.value.id)
        availableStaff.value = availableStaff.value.filter(
            staff => staff.staff_id !== assignedStaffId
        )
    } catch (err) {
        error.value = err.message
    } finally {
        savingAssignment.value = false
    }
}

async function cancelStaffAssignment(assignment) {
    error.value = ''
    message.value = ''

    if (!confirm(`Remove ${assignment.username} from this trek?`)) {
        return
    }

    cancellingAssignmentId.value = assignment.assignment_id

    try {
        const response = await fetch(
            `http://127.0.0.1:5000/api/admin/cancel-assignments/${assignment.assignment_id}`,
            {
                method: 'PATCH',
                credentials: 'include',
                headers: { 'X-CSRF-TOKEN': getCsrfToken() }
            }
        )
        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Could not remove staff assignment')
        }

        message.value = result.message || 'Staff assignment cancelled'
        await fetchAssignedStaff(assignmentTrek.value.id)
    } catch (err) {
        error.value = err.message
    } finally {
        cancellingAssignmentId.value = null
    }
}


onMounted(fetchTreks)
</script>

<template>
    <section class="grid-22">
        <div class="section-heading">
            <h2>{{  showForm ? 'Add New Trek' : 'Manage Treks'  }}</h2>
            <button v-if="!showForm && !selectedTrek && !assignmentTrek"
                    type="button"
                    @click="showForm = true">
                    + Add Trek
            </button>
            <button v-if="selectedTrek"
                    type="button"
                    class="trek-button"
                    @click="backToTreks">
                    ← Back to Treks
            </button>
        </div>

        <p v-if="error" class="feedback error" role="alert">{{ error }}</p>
        <p v-if="message" class="feedback success" role="status">{{ message }}</p>

        <section v-if="assignmentTrek" class="assignment-panel">
            <div class="section-heading">
                <h3>Assign staff for {{ assignmentTrek.trek_name }}</h3>
                <button type="button" class="trek-button" @click="assignmentTrek = null">
                    Cancel
                </button>
            </div>

            <p v-if="loadingAssignments">Loading staff...</p>
            <template v-else>
                <form class="assignment-form" @submit.prevent="searchAvailableStaff">
                    <input
                        v-model="staffSearchText"
                        type="search"
                        placeholder="Search staff by name or ID"
                        aria-label="Search staff by name or ID"
                        @input="clearStaffSearchResults"
                    >
                </form>

                <form v-if="availableStaff.length" class="staff-results" @submit.prevent="assignStaff">
                    <label v-for="staff in availableStaff" :key="staff.staff_id" class="staff-result">
                        <input v-model="selectedStaffId" type="radio" :value="staff.staff_id" required>
                        <span>
                            <strong>{{ staff.username }}</strong>
                            <span>Staff ID: {{ staff.staff_id }}</span>
                            <span>{{ staff.contact_number || 'No contact number' }}</span>
                            <span>Next available: {{ staff.next_available_date || 'Not specified' }}</span>
                        </span>
                    </label>
                    <button type="submit" class="trek-button primary" :disabled="savingAssignment || !selectedStaffId">
                        {{ savingAssignment ? 'Assigning...' : 'Assign Selected Staff' }}
                    </button>
                </form>
                <p v-else-if="searchingStaff">Searching staff...</p>
                <p v-else-if="searched && availableStaff.length === 0">
                    No available staff matched that search.
                </p>

                <h4>Currently assigned</h4>
                <p v-if="!assignedStaff.length">No staff assigned to this trek.</p>
                <ul v-else class="assigned-staff-list">
                    <li v-for="staff in assignedStaff" :key="staff.assignment_id">
                        <span>{{ staff.username }} — {{ staff.contact_number }}</span>
                        <button
                            type="button"
                            class="trek-button"
                            :disabled="cancellingAssignmentId === staff.assignment_id"
                            @click="cancelStaffAssignment(staff)"
                        >
                            {{ cancellingAssignmentId === staff.assignment_id ? 'Removing...' : 'Remove' }}
                        </button>
                    </li>
                </ul>
            </template>
        </section>

        <form v-if="showForm" @submit.prevent="createTrek">
            <div class="grid-221">
                <div class="col-1">
                    <div class="col-11"><label for="trek_name">Trek Name</label><input id="trek_name" v-model="form.trek_name" type="text" maxlength="100" required></div>
                    <div class="col-11"><label for="location">Location</label><input id="location" v-model="form.location" type="text" maxlength="100" required></div>
                    <div class="col-11"><label for="difficulty">Difficulty</label><select id="difficulty" v-model="form.difficulty" required><option value="" disabled>Select difficulty</option><option value="easy">Easy</option><option value="moderate">Moderate</option><option value="hard">Hard</option></select></div>
                    <div class="col-11"><label for="duration">Duration (days)</label><input id="duration" v-model.number="form.duration" type="number" min="1" step="1" required></div>
                    <div class="col-11"><label for="start_date">Start Date</label><input id="start_date" v-model="form.start_date" type="date" required></div>
                    <div class="col-11"><label for="end_date">End Date</label><input id="end_date" v-model="form.end_date" type="date" :min="form.start_date" required></div>
                </div>
                <div class="col-2">
                    <div class="col-22"><label for="total_slots">Total Slots</label><input id="total_slots" v-model.number="form.total_slots" type="number" min="1" step="1" required></div>
                    <div class="col-22"><label for="price">Price</label><input id="price" v-model.number="form.price" type="number" min="0" step="0.01" required></div>
                    <div class="col-22"><label for="description">Description</label><textarea id="description" v-model="form.description" rows="4" maxlength="100"></textarea></div>
                    <p>New treks start Pending. Approve the trek, then open bookings.</p>
                </div>
            </div>
            <div class="action-row">
                <button type="button" class="button" @click="cancelForm">Cancel</button>
                <button type="submit" class="button primary" :disabled="saving">{{ saving ? 'Saving...' : 'Create Trek' }}</button>
            </div>
        </form>


        <div v-else-if="selectedTrek">

            <form v-if="isEditing" @submit.prevent="saveTrek">
                <div class="grid-221">
                    <div class="col-1">
                        <div class="col-11">
                            <label for="trek_name">Trek Name</label>
                            <input id="trek_name" v-model="form.trek_name" type="text" maxlength="100" required>
                        </div>
                        <div class="col-11"><label for="location">Location</label><input id="location" v-model="form.location" type="text" maxlength="100" required></div>
                        <div class="col-11"><label for="difficulty">Difficulty</label><select id="difficulty" v-model="form.difficulty" required><option value="" disabled>Select difficulty</option><option value="easy">Easy</option><option value="moderate">Moderate</option><option value="hard">Hard</option></select></div>
                        <div class="col-11"><label for="duration">Duration (days)</label><input id="duration" v-model.number="form.duration" type="number" min="1" step="1" required></div>
                        <div class="col-11"><label for="start_date">Start Date</label><input id="start_date" v-model="form.start_date" type="date" required></div>
                        <div class="col-11"><label for="end_date">End Date</label><input id="end_date" v-model="form.end_date" type="date" :min="form.start_date" required></div>
                    </div>
                    <div class="col-2">
                        <div class="col-22"><label for="total_slots">Total Slots</label><input id="total_slots" v-model.number="form.total_slots" type="number" min="1" step="1" required></div>
                        <div class="col-22"><label for="price">Price</label><input id="price" v-model.number="form.price" type="number" min="0" step="0.01" required></div>
                        <div class="col-22"><label for="description">Description</label><textarea id="description" v-model="form.description" rows="4" maxlength="100"></textarea></div>
                        <div class="checkline"><input id="bookings_open" v-model="form.bookings_open" type="checkbox"><label for="bookings_open">Bookings Open</label></div>
                    </div>
                </div>
                <div class="action-row">
                    <button type="button" class="button" @click="backToTreks">Cancel</button>
                    <button type="submit" class="button primary" :disabled="saving">{{ saving ? 'Saving...' : 'Save Trek' }}</button>
                </div>
            </form>

            <div v-else class="details-grid">
                <h2>{{ selectedTrek.trek_name }}</h2>
                <p>Status: {{ selectedTrek.trek_status }}</p>
                <button v-if="selectedTrek.trek_status === 'pending'" :disabled="saving" @click="approveTrek(selectedTrek)">Approve Trek</button>
                <p><strong>Trek ID:</strong> {{ selectedTrek.display_id }}</p>
                <p><strong>Location:</strong> {{ selectedTrek.location }}</p>
                <p><strong>Difficulty:</strong> {{ selectedTrek.difficulty }}</p>
                <p><strong>Duration:</strong> {{ selectedTrek.duration }} days</p>
                <p><strong>Start Date:</strong> {{ selectedTrek.start_date }}</p>
                <p><strong>End Date:</strong> {{ selectedTrek.end_date }}</p>
                <p><strong>Total Slots:</strong> {{ selectedTrek.total_slots }}</p>
                <p><strong>Available Slots:</strong> {{ selectedTrek.available_slots }}</p>
                <p><strong>Price:</strong> ₹{{ selectedTrek.price }}</p>
                <p><strong>Status:</strong> {{ selectedTrek.trek_status }}</p>
                <p><strong>Bookings Open:</strong> {{ selectedTrek.bookings_open ? 'Yes' : 'No' }}</p>
                <p><strong>Description:</strong> {{ selectedTrek.description || 'No description' }}</p>
            </div>

        </div>


        <div v-else-if="!assignmentTrek" class="treks-list">
            <form class="search-form" @submit.prevent="fetchTreks(searchText)">
                <input
                    id="trek-search"
                    v-model="searchText"
                    type="search"
                    placeholder="Search treks..."
                    aria-label="Search treks"
                >
                <button type="submit" class="trek-button search-button">Search</button>
            </form>

            <p v-if="loading">Loading treks...</p>
            <table v-else-if="treks.length">
                <thead>
                    <tr>
                        <th>Trek ID</th>
                        <th>Trek Name</th>
                        <th>Location</th>
                        <th>Start Date</th>
                        <th>Available Slots</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="trek in treks" :key="trek.id">
                        <td> {{ trek.display_id }} </td>
                        <td> {{ trek.trek_name }} </td>
                        <td> {{ trek.location }} </td>
                        <td> {{ trek.start_date }} </td>
                        <td> {{ trek.available_slots }} </td>
                        <td> {{ trek.trek_status }} </td>
                        <td>
                            <div class="trek-actions">
                                <button type="button" class="trek-button" @click="fullInfo(trek.id)">
                                    More Details
                                </button>

                                <button type="button" class="trek-button" @click="editTrek(trek.id)">
                                    Edit
                                </button>

                                <button type="button" class="trek-button" @click="deleteTrek(trek.id)">
                                    Delete
                                </button>
                                <button
                                    v-if="trek.trek_status === 'upcoming'"
                                    type="button"
                                    class="trek-button"
                                    @click="openStaffAssignment(trek)"
                                >
                                    Assign Staff
                                </button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
            <p v-else-if="!error">No treks found.</p>
        </div>
    </section>
</template>

<style scoped>
        .grid-22{

            display:grid;
            grid-template-rows: auto 1fr;
            padding:0.5rem;
            align-items: center;

        }

        .grid-22 h2{
            margin-bottom: 0rem;
            padding: 0rem;
            border-bottom: 0.2rem solid #f2f2f2;
        }


        .grid-221{
            display: grid;
            grid-template-columns: 1fr 1fr;
            align-items: start;

            padding:1rem;

        }

        .col-1, .col-2{

            display:flex;
            flex-direction: column;
            gap:1rem;
            padding:2rem;
            box-sizing: border-box;

        }

        .col-1{
            border-right: 0.15rem solid #f2f2f2;
        }

        .col-11, .col-22{
            display: flex;
            flex-direction: row;
            gap:1rem;
            justify-content: left;
        }

        .col-11, .col-22 {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }

        .col-11 label, .col-22 label{
            flex:0 0 30%;
            max-width:30%;
            font-size: large;
        }

        .col-11 input, .col-11 select, .col-22 input, .col-22 select, .col-22 textarea{
            flex:0 0 70%;
            max-width:70%;
            padding:1rem;
            font-size: large;
            font-weight: bold;
            box-sizing: border-box;
            border-radius: 0.5rem;
            border: 0.1rem solid #f2f2f2;
            outline: none;
        }

        .col-11 input:focus, .col-22 input:focus, .col-11 select:focus, .col-22 textarea:focus{
            border:0.1rem solid #175cf1;
        }

        .submit{
            justify-content:center;
            padding:1rem;
            width: 70%;
            cursor: pointer;
        }

        .button{
            text-decoration: none;
            padding: 1rem;
            width:30%;
            background-color: #e9e9ed;
            color: black;
            font-size: large;
            font-weight: bold;
            border-radius: 0.5rem;
            cursor: pointer;
        }

        .submit:focus, .button:focus{
            border:0.1rem solid #175cf1;
            background-color: #7d7d7e;
        }

        .trek-actions {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-wrap: nowrap;
    }

        .details-grid {
            display: flex;
            flex-direction: column;
            align-items: center;
            border: 0.1rem solid #7d7d7e;
            border-radius: 0.5rem;
            margin-left: 20%;
            margin-right: 20%;
            background-color: #f2f2f2;

    }

    .details-grid p{
        display: flex;
        flex-direction: row;

        justify-content: space-between;
    }

    .trek-button {
        background-color: #e9e9ed;
        color: #333;

        padding: 0.5rem 0.75rem;
        width: auto;

        font-size: 0.9rem;
        font-weight: 500;

        border: 0.1rem solid #d6d6d6;
        border-radius: 0.5rem;

        cursor: pointer;
        white-space: nowrap;

        transition: background-color 0.2s, color 0.2s;
    }

    .trek-button:hover {
        background-color: #175cf1;
        border-color: #175cf1;
        color: white;
    }

    .trek-button.delete:hover {
        background-color: #c62828;
        border-color: #c62828;
        color: white;
    }

    .trek-button:focus-visible {
        outline: 0.15rem solid #175cf1;
        outline-offset: 0.15rem;
    }


        .action-row { display: flex; gap: 1rem; justify-content: flex-end; padding: 0.75rem 2rem 1rem; }
        .action-row button { width: auto; cursor: pointer; border: 1px solid #d6d6d6; }
        .action-row .primary { background: #175cf1; color: white; border-color: #175cf1; }
        .action-row button:disabled { opacity: .6; cursor: wait; }
        .feedback { padding: .75rem 2rem; }
        .feedback.error { color: #b42318; }
        .feedback.success { color: #16703d; }
        .treks-list { margin: 1.5rem 2rem; overflow-x: auto; }
        .treks-list table { width: 100%; border-collapse: collapse; }
        .treks-list th, .treks-list td { padding: .8rem; border-bottom: 1px solid #f2f2f2; text-align: left; }
        .treks-list th { background: #f2f2f2; }
        .section-heading { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
        .section-heading button { cursor: pointer; padding: .65rem 1rem; background: #175cf1; color: white; border: 0; border-radius: .5rem; }
        .search-form { display: flex; gap: .75rem; margin-bottom: 1rem; }
        .search-form input { flex: 1; min-width: 10rem; padding: .65rem; border: 1px solid #d6d6d6; border-radius: .5rem; }
        .search-button { width: auto; }
        .assignment-panel { margin: 1rem 2rem; padding: 1rem; border: 1px solid #f2f2f2; border-radius: .5rem; }
        .assignment-form { display: flex; align-items: center; gap: .75rem; margin: 1rem 0; }
        .assignment-form input[type="search"] { flex: 1; min-width: 10rem; padding: .65rem; border: 1px solid #d6d6d6; border-radius: .5rem; }
        .staff-results { display: flex; flex-direction: column; gap: .5rem; margin-bottom: 1rem; }
        .staff-result { display: flex; align-items: flex-start; gap: .75rem; padding: .75rem; border: 1px solid #d6d6d6; border-radius: .5rem; cursor: pointer; }
        .staff-result > span { display: flex; flex-direction: column; gap: .2rem; }
        .staff-results > button { align-self: flex-start; }
        .assigned-staff-list { list-style: none; margin: 0; padding: 0; }
        .assigned-staff-list li { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: .5rem 0; border-bottom: 1px solid #f2f2f2; }
        .checkline { display:flex; align-items:center; gap:.75rem; margin-bottom:1rem; }
        .checkline input { width: 1.25rem; height: 1.25rem; accent-color:#175cf1; }
        .checkline label { font-size: large; }
        @media (max-width: 850px) {
          .grid-221 { grid-template-columns: 1fr; padding: 0; }
          .col-1 { border-right: 0; border-bottom: 1px solid #f2f2f2; }
          .col-1, .col-2 { padding: 1rem; }
          .treks-list { margin: 1rem 0; }
          .assignment-panel { margin: 1rem 0; }
          .assignment-form { align-items: stretch; flex-direction: column; }
          .col-11 label, .col-22 label { flex-basis: 35%; max-width: 35%; }
          .col-11 input, .col-11 select, .col-22 input, .col-22 select, .col-22 textarea { flex-basis: 65%; max-width: 65%; min-width: 0; }
        }

</style>
