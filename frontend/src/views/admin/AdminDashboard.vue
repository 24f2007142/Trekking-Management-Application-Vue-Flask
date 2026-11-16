<script setup>
import { ref, onMounted } from 'vue'

const dashboard = ref(null)
const loading = ref(false)
const error = ref('')

onMounted(async () => {
    loading.value = true
    try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/dashboard', {
            credentials: 'include'
        })

        if (!response.ok) throw new Error('Failed to load dashboard')

        const result = await response.json()
        dashboard.value = result.data

    } catch (err) {
        error.value = err.message
    } finally {
        loading.value = false
    }
})
</script>

<template>
    <p v-if="loading">Loading dashboard...</p>
    <p v-else-if="error" style="color: red">{{ error }}</p>
    <div v-else-if="dashboard">
                <div class="grid-22">

                    <div class="grid-221">

                        <div class="outer-flex-221">
                            <div class="flex-221">
                                <h3>Total Treks</h3>
                                <p>{{ dashboard.total_treks}}</p>
                            </div>

                            <svg width="5rem" height="5rem" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <g>
                                    <path fill="none" d="M0 0h24v24H0z"/>
                                    <path d="M7.617 8.712l3.205-2.328A1.995 1.995 0 0 1 12.065 6a2.616 2.616 0 0 1 2.427 1.82c.186.583.356.977.51 1.182A4.992 4.992 0 0 0 19 11v2a6.986 6.986 0 0 1-5.402-2.547l-.697 3.955 2.061 1.73 2.223 6.108-1.88.684-2.04-5.604-3.39-2.845a2 2 0 0 1-.713-1.904l.509-2.885-.677.492-2.127 2.928-1.618-1.176L7.6 8.7l.017.012zM13.5 5.5a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm-2.972 13.181l-3.214 3.83-1.532-1.285 2.976-3.546.746-2.18 1.791 1.5-.767 1.681z"/>
                                </g>
                            </svg>
                        </div>

                        <div class="outer-flex-221">

                            <div class="flex-221">
                                <h3>Total Staffs</h3>
                                <p>{{ dashboard.total_staffs }}</p>
                            </div>

                            <svg fill="#000000" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
                                width="6rem" height="6rem" viewBox="0 0 39.66 39.66" xml:space="preserve">
                                    <g>
                                        <g id="_x31__143_">
                                            <g>
                                                <path d="M4.619,15.479c0.888,3.39,3.752,6.513,7.382,6.513c3.684,0,6.594-3.109,7.504-6.49c0.346-0.039,0.632-0.303,0.663-0.663
                                                    l0.115-1.336c0.029-0.348-0.189-0.646-0.506-0.756c-0.006-0.08-0.008-0.161-0.017-0.24c-0.068-3.062-0.6-5.534-3.01-6.556
                                                    c-2.544-1.078-4.786-1.093-6.432-0.453C10.21,5.541,9.931,5.912,9.822,5.979C9.713,6.046,9.136,5.856,8.917,5.907
                                                    c-3.61,0.516-4.801,3.917-4.538,6.569C4.371,12.55,4.366,12.625,4.36,12.7c-0.349,0.087-0.599,0.404-0.567,0.774l0.114,1.336
                                                    C3.94,15.188,4.25,15.462,4.619,15.479z M5.388,12.833c1.581-0.579,4.622-1.79,4.952-2.426c1.383,1.437,6.267,2.244,8.411,2.513
                                                    c0.009,0.139,0.021,0.274,0.021,0.414c0,3.525-2.958,7.623-6.771,7.623c-3.799,0-6.638-4.024-6.638-7.623
                                                    C5.362,13.165,5.375,13,5.388,12.833z"/>
                                                <path d="M17.818,20.777c-0.19-0.029-0.376,0.014-0.498,0.063l-3.041,4.113l-2.307-1.84l-0.014,0.012v0.013l-0.003-0.003
                                                    l-2.307,1.84l-3.041-4.113c-0.121-0.05-0.308-0.093-0.498-0.064C0.364,21.608,0,34.584,0,34.584l11.969,0.008v-0.021
                                                    l11.958-0.008C23.928,34.563,23.562,21.587,17.818,20.777z"/>
                                                <path d="M23.997,15.302c0.72,2.75,3.044,5.281,5.987,5.281c2.988,0,5.349-2.521,6.087-5.264c0.28-0.032,0.513-0.245,0.538-0.537
                                                    l0.093-1.083c0.024-0.283-0.154-0.525-0.411-0.614c-0.004-0.063-0.007-0.13-0.014-0.193c-0.055-2.483-0.486-4.49-2.44-5.318
                                                    c-2.063-0.874-3.882-0.887-5.217-0.368c-0.087,0.035-0.313,0.336-0.401,0.392c-0.09,0.055-0.557-0.101-0.734-0.059
                                                    c-2.928,0.418-3.895,3.177-3.682,5.328c-0.007,0.061-0.01,0.121-0.015,0.182c-0.283,0.071-0.485,0.328-0.459,0.627l0.092,1.083
                                                    C23.446,15.065,23.698,15.288,23.997,15.302z M24.62,13.155c1.282-0.47,3.75-1.452,4.017-1.968
                                                    c1.123,1.164,5.084,1.818,6.822,2.039c0.008,0.11,0.018,0.222,0.018,0.335c0,2.858-2.398,6.183-5.492,6.183
                                                    c-3.082,0-5.385-3.264-5.385-6.183C24.6,13.425,24.609,13.29,24.62,13.155z"/>
                                                <path d="M34.703,19.6c-0.154-0.024-0.305,0.011-0.402,0.05l-2.468,3.337l-1.871-1.492l-0.011,0.009v0.011l-0.003-0.002
                                                    l-1.871,1.492l-2.468-3.337c-0.098-0.04-0.25-0.073-0.402-0.05c-1.521,0.214-2.574,1.482-3.307,3.089
                                                    c0.433,0.669,1.043,1.736,1.56,3.14c0.515,1.395,0.856,3.295,1.078,4.958l5.422,0.003v-0.018l9.7-0.006
                                                    C39.659,30.781,39.363,20.254,34.703,19.6z"/>
                                            </g>
                                        </g>
                                    </g>
                            </svg>



                        </div>

                        <div class="outer-flex-221">

                            <div class="flex-221">
                                <h3>Total Users</h3>
                                <p>{{ dashboard.total_users }}</p>
                            </div>

                            <svg width="6.5rem" height="6.5rem" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M5 21C5 17.134 8.13401 14 12 14C15.866 14 19 17.134 19 21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </div>

                        <div class="outer-flex-221">

                            <div class="flex-221">
                                <h3>Total Bookings</h3>
                                <p>{{ dashboard.total_bookings }}</p>
                            </div>

                            <svg fill="#000000" width="6rem" height="6rem" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg">
                                <title>report</title>
                                <path d="M6 11h4v17h-4v-17zM22 16v12h4v-12h-4zM14 28h4v-24h-4v24z"></path>
                            </svg>
                        </div>

                    </div>

                    <div class="grid-222">
                        <h2> Recently Added Treks </h2>
                        <div class="line"></div>
                    </div>

                    <div class="bookings-table">
                        <table>
                            <thead class="header">

                                <tr>
                                    <th>Trek ID</th>
                                    <th>Trek Name</th>
                                    <th>Location</th>
                                    <th>Start Date</th>
                                    <th>Available Slots</th>
                                    <th>Bookings Status</th>
                                    <th>Trek Status</th>
                                </tr>

                            </thead>

                            <tbody>

                                <tr v-for="trek in dashboard.recent_treks" :key="trek.id">

                                        <td>{{trek.display_id}}</td>
                                        <td>{{trek.trek_name}}</td>
                                        <td>{{trek.location}}</td>
                                        <td>{{trek.start_date}}</td>
                                        <td>{{trek.available_slots}}</td>
                                        <td>{{trek.bookings_open ? 'Open' : 'Closed'}}</td>
                                        <td>{{trek.trek_status}}</td>

                                    </tr>

                                    <tr v-if="dashboard.recent_treks.length === 0">
                                        <td colspan="7" style="color:red">No treks found.</td>
                                    </tr>

                            </tbody>
                        </table>
                        <div class="bookings-url">
                            <RouterLink to="/admin/treks">
                                <span>View all treks</span>
                            <svg fill="#175cf1" width="1.5rem" height="1.5rem" viewBox="0 0 24 24" id="right-arrow" xmlns="http://www.w3.org/2000/svg" class="icon line"><path id="primary" d="M3,12H21m-3,3,3-3L18,9" style="fill: none; stroke: #175cf1; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.5;"></path></svg>
                            </RouterLink>
                        </div>
                    </div>

                </div>
    </div>
</template>

<style scoped>
        .grid-22{

            display:grid;
            grid-template-rows: 1fr 0.5fr 3fr;
            padding:1rem;
        }

        .grid-221{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap:1rem;

            font-size: inherit;
        }

        .outer-flex-221{

            display: flex;
            flex-direction: row;
            border: 0.2rem solid #f2f2f2;
            padding:1rem;
            align-items: center;
            gap:1rem;
            border-radius: 2rem;

        }

        .outer-flex-221:hover{
            background-color: #f2f2f2;
            color:#175cf1;
            border: 0.2rem solid #175cf1;
        }

        .outer-flex-221.active{
            background-color: #f2f2f2;
            color:#175cf1;
            border: 0.2rem solid #175cf1;
        }



        .flex-221{
            display:flex;
            flex-direction: column;

        }

        .flex-221 p{
            font-size:2rem;
            font-weight: bold;
        }

        .grid-222{
            display: flex;
            align-items: center;
            gap:1rem;
            padding:0rem;
        }

        .grid-222 .line{
            flex:1;
            border-top: 0.05rem solid #f2f2f2;

        }

        table{
            width:100%;
            border-collapse: collapse;
        }

        .bookings-table{

            display: flex;
            flex-direction: column;


        }

        thead{

            background-color: #f2f2f2;

        }

        th{
            padding:1rem;
        }

        .bookings-table td{

            padding: 1rem;
            text-align: center;

        }

        .bookings-url{

            display: flex;
            flex-direction: row;
            gap:1rem;
            justify-content: right;
            align-items: center;
            padding: 0.5rem;

        }

        .bookings-url a{
            display: flex;
            align-items: center;
            gap:0.5rem;
            text-decoration: none;
            color: #175cf1;
            text-align: center;
        }



        .bookings-url:hover {
            text-decoration:0.1rem #175cf1 underline;
        }


</style>
