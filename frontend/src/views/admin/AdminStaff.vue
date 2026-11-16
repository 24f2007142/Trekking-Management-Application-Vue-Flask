<script setup>
import { ref, onMounted, reactive } from 'vue'

const staffList = ref([])
const loading = ref(false)
const error = ref('')
const message = ref('')
const showAddForm = ref(false)
const saving = ref(false)
const updatingStaffId = ref(null)
const searchText = ref('')
const editingStaff = ref(null)
const historyForStaff = ref(null)
const assignmentHistory = ref([])
const loadingHistory = ref(false)

const form = reactive({
    username: '',
    email: '',
    password: '',
    contact_number: '',
    next_available_date: '',
})

function getCsrfToken() {
    const cookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrf_access_token='))

    return cookie
        ? decodeURIComponent(cookie.split('=').slice(1).join('='))
        : ''
}

async function addStaff() {
    error.value = ''
    message.value = ''
    saving.value = true
    historyForStaff.value = ''

    try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/staffs',
            {
                method: 'POST',
                credentials: 'include',
                headers:
                {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': getCsrfToken()
                },
                body: JSON.stringify(form)
            }
        )

        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Staff profile not created')
        }

        message.value = result.message || 'Staff created successfully'
        form.username = ''
        form.email = ''
        form.password = ''
        form.contact_number = ''
        form.next_available_date = ''
        showAddForm.value = false
        await fetchStaff()
    } catch (err) {
        error.value = err.message
    } finally {
        saving.value = false
    }
}

async function fetchStaff(search = searchText.value) {
    loading.value = true
    error.value = ''

    try {
        const url = new URL('http://127.0.0.1:5000/api/admin/staffs')
        url.searchParams.set('search', search)

        const response = await fetch(url, {
            credentials: 'include'
        })

        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Could not load staff')
        }

        staffList.value = result.data
    } catch (err) {
        error.value = err.message
    } finally {
        loading.value = false
    }
}

async function startEdit(staff) {
    error.value = ''
    message.value = ''

    try {
        const response = await fetch(
            `http://127.0.0.1:5000/api/admin/staffs/${staff.user_id}`,
            { credentials: 'include' }
        )
        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Could not load staff details')
        }

        const details = result.data || result
        form.username = details.username
        form.email = details.email
        form.password = ''
        form.contact_number = details.contact_number || ''
        form.next_available_date = details.next_available_date || ''
        editingStaff.value = details.user_id || details.id || staff.user_id
    } catch (err) {
        error.value = err.message
    }
}

function cancelEdit() {
    editingStaff.value = null
    form.username = ''
    form.email = ''
    form.password = ''
    form.contact_number = ''
    form.next_available_date = ''
}

async function saveStaffEdit() {
    error.value = ''
    message.value = ''
    saving.value = true

    try {
        const response = await fetch(
            `http://127.0.0.1:5000/api/admin/staffs/${editingStaff.value}`,
            {
                method: 'PUT',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': getCsrfToken()
                },
                body: JSON.stringify({
                    username: form.username,
                    email: form.email,
                    contact_number: form.contact_number,
                    next_available_date: form.next_available_date
                })
            }
        )
        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Could not update staff')
        }

        message.value = result.message || 'Staff updated successfully'
        cancelEdit()
        await fetchStaff(searchText.value)
    } catch (err) {
        error.value = err.message
    } finally {
        saving.value = false
    }
}

async function showAssignmentHistory(staff) {
    error.value = ''
    message.value = ''
    loadingHistory.value = true

    try {
        const response = await fetch(
            `http://127.0.0.1:5000/api/admin/staffs/${staff.user_id}/assignments`,
            { credentials: 'include' }
        )
        const result = await response.json()

        if (!response.ok) {
            throw new Error(result.message || 'Could not load assignment history')
        }

        assignmentHistory.value = result.data
        historyForStaff.value = staff
    } catch (err) {
        error.value = err.message
    } finally {
        loadingHistory.value = false
    }
}

function closeAssignmentHistory() {
    historyForStaff.value = null
    assignmentHistory.value = []
}

async function updateStaffStatus(staff) {

    error.value = ''
    message.value = ''

    let newStatus = 'blacklist'

    if (staff.approval_status === 'blacklist') {
        newStatus = 'approved'
    } else if (!confirm('Are you sure you want to blacklist this staff?')) {
        return
    }

    updatingStaffId.value = staff.user_id

    try {
        const response = await fetch(
            `http://127.0.0.1:5000/api/admin/staffs/${staff.user_id}/status`,
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
            throw new Error(result.message || 'Could not update staff status')
        }

        message.value = result.message || 'Staff status updated successfully'
        await fetchStaff()
    } catch (err) {
        error.value = err.message
    } finally {
        updatingStaffId.value = null
    }
}

onMounted(fetchStaff)
</script>

<template>
    <section>
        <div class="section-heading">
            <h2>Manage Staff</h2>
            <button type="button" class="add-button" @click="showAddForm = !showAddForm">
                {{ showAddForm ? 'Cancel' : 'Add Staff' }}
            </button>
        </div>

        <p v-if="message" role="status">{{ message }}</p>
        <p v-if="error" role="alert">{{ error }}</p>

        <form v-if="editingStaff" class="staff-form" @submit.prevent="saveStaffEdit">
            <label for="edit-staff-username">Name</label>
            <input id="edit-staff-username" v-model="form.username" type="text" required>

            <label for="edit-staff-email">Email</label>
            <input id="edit-staff-email" v-model="form.email" type="email" required>

            <label for="edit-staff-contact">Contact number</label>
            <input id="edit-staff-contact" v-model="form.contact_number" type="tel" required>

            <label for="edit-staff-date">Next available date</label>
            <input id="edit-staff-date" v-model="form.next_available_date" type="date">

            <div class="form-actions">
                <button type="button" class="trek-button" @click="cancelEdit">Cancel</button>
                <button type="submit" class="trek-button primary" :disabled="saving">
                    {{ saving ? 'Saving...' : 'Save Changes' }}
                </button>
            </div>
        </form>

        <form v-else-if="showAddForm  && !historyForStaff" class="staff-form" @submit.prevent="addStaff">
            <label for="staff-username">Name</label>
            <input id="staff-username" v-model="form.username" type="text" required>

            <label for="staff-email">Email</label>
            <input id="staff-email" v-model="form.email" type="email" required>

            <label for="staff-password">Password</label>
            <input id="staff-password" v-model="form.password" type="password" required>

            <label for="staff-contact">Contact number</label>
            <input id="staff-contact" v-model="form.contact_number" type="tel" required>

            <label for="staff-available-date">Next available date</label>
            <input id="staff-available-date" v-model="form.next_available_date" type="date">

            <button type="submit" class="trek-button primary" :disabled="saving">
                {{ saving ? 'Saving...' : 'Save Staff' }}
            </button>
        </form>

        <form v-if="!editingStaff && !historyForStaff && !showAddForm" class="search-form" @submit.prevent="fetchStaff(searchText)">
            <input id="staff-search" v-model="searchText" type="search" placeholder="Search staff..." aria-label="Search staff">
            <button type="submit" class="trek-button primary">Search</button>
        </form>

        <p v-if="loading">Loading staff...</p>

        <div v-if="historyForStaff && !editingStaff" class="staff-list">
            <div class="section-heading">
                <h3>Assignment History: {{ historyForStaff.username }}</h3>
                <button type="button" class="trek-button" @click="closeAssignmentHistory">
                    Back to Staff
                </button>
            </div>
            <p v-if="loadingHistory">Loading assignment history...</p>
            <table v-else-if="assignmentHistory.length">
                <thead>
                    <tr>
                        <th>Assignment ID</th>
                        <th>Trek</th>
                        <th>Location</th>
                        <th>Trek Dates</th>
                        <th>Assignment Status</th>
                        <th>Trek Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="assignment in assignmentHistory" :key="assignment.assignment_id">
                        <td>{{ assignment.assignment_id }}</td>
                        <td>{{ assignment.trek.display_id }} — {{ assignment.trek.trek_name }}</td>
                        <td>{{ assignment.trek.location }}</td>
                        <td>{{ assignment.trek.start_date }} to {{ assignment.trek.end_date }}</td>
                        <td>{{ assignment.status }}</td>
                        <td>{{ assignment.trek.trek_status }}</td>
                    </tr>
                </tbody>
            </table>
            <p v-else-if="!loadingHistory">No assignments found for this staff member.</p>
        </div>

        <div v-else-if="!editingStaff && staffList.length" class="staff-list">
        <table>
            <thead>
                <tr>
                    <th>Staff ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Contact</th>
                    <th>Next Available Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="staff in staffList" :key="staff.user_id">
                    <td>{{ staff.staff_id }}</td>
                    <td>{{ staff.username }}</td>
                    <td>{{ staff.email }}</td>
                    <td>{{ staff.contact_number || '—' }}</td>
                    <td>{{ staff.next_available_date || '—' }}</td>
                    <td>{{ staff.approval_status }}</td>
                    <td>
                        <div class="staff-actions">
                            <button type="button" class="trek-button" @click="showAssignmentHistory(staff)">
                                History
                            </button>
                            <button type="button" class="trek-button" @click="startEdit(staff)">
                                Edit
                            </button>
                            <button
                                type="button"
                                class="trek-button"
                                :disabled="updatingStaffId === staff.user_id"
                                @click="updateStaffStatus(staff)"
                            >
                                <span v-if="updatingStaffId === staff.user_id">Saving...</span>
                                <span v-else-if="staff.approval_status === 'blacklist'">Reactivate</span>
                                <span v-else>Blacklist</span>
                            </button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
        </div>

        <p v-else-if="!editingStaff && !loading">No staff found.</p>
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

.staff-form {
    display: grid;
    grid-template-columns: minmax(8rem, 12rem) minmax(12rem, 24rem);
    align-items: center;
    gap: 1rem;
    margin: 1.5rem 2rem;
}

.staff-form input {
    width: 100%;
    padding: 0.75rem;
    box-sizing: border-box;
    border: 0.1rem solid #d6d6d6;
    border-radius: 0.5rem;
    font-size: 1rem;
}

.staff-form input:focus {
    border-color: #175cf1;
    outline: none;
}

.staff-form button {
    grid-column: 2;
    justify-self: start;
}

.form-actions {
    grid-column: 2;
    display: flex;
    gap: 0.75rem;
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

.staff-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.add-button {
    cursor: pointer;
    padding: 0.65rem 1rem;
    background-color: #175cf1;
    color: white;
    border: 0;
    border-radius: 0.5rem;
}

.staff-list {
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

.trek-button:hover {
    background-color: #175cf1;
    border-color: #175cf1;
    color: white;
}

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
    .staff-form {
        grid-template-columns: 1fr;
        margin: 1rem 0;
    }

    .staff-form button,
    .form-actions {
        grid-column: 1;
    }

    .search-form {
        flex-wrap: wrap;
        margin: 1rem 0;
    }

    .staff-list {
        margin: 1rem 0;
    }
}

</style>
