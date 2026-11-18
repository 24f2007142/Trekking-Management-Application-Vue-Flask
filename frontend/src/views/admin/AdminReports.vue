<script setup>
import { ref, onMounted } from 'vue'

const reports = ref([])
const loading = ref(true)
const error = ref('')

const chartColors = {
    Treks: '#2563eb',
    'Users (trekkers)': '#15803d',
    Bookings: '#9333ea'
}

async function loadReports() {
    loading.value = true
    error.value = ''
    try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/reports', { credentials: 'include' })
        if (!response.ok) throw new Error('Could not load reports')
        reports.value = (await response.json()).data
    } catch (err) { error.value = err.message }
    finally { loading.value = false }
}

function totalCount(items) {
    return items.reduce((total, item) => total + item.count, 0)
}

function barWidth(items, count) {
    return (count / Math.max(1, totalCount(items)) * 100) + '%'
}

onMounted(loadReports)
</script>

<template>
    <section>
        <h2>Reports</h2>
        <p v-if="loading" role="status">Loading reports...</p>
        <p v-else-if="error" role="alert">{{ error }} <button @click="loadReports">Retry</button></p>
        <div v-else v-for="report in reports" :key="report.title" class="chart"
            :style="{ '--chart-color': chartColors[report.title] }">
            <div class="chart-heading">
                <h3>{{ report.title }}</h3>
                <strong class="total">Total: {{ totalCount(report.items) }}</strong>
            </div>
            <div v-for="item in report.items" :key="item.label" class="row">
                <span>{{ item.label }}</span>
                <div class="track" aria-hidden="true"><div class="bar" :style="{ width: barWidth(report.items, item.count), backgroundColor: chartColors[report.title] }"></div></div>
                <strong class="count">{{ item.count }}</strong>
            </div>
            <p v-if="totalCount(report.items) === 0" class="chart-hint">No records yet.</p>
        </div>
    </section>
</template>

<style scoped>
section { padding: 1rem; max-width: 45rem; }
.chart { margin-bottom: 1.5rem; padding: 1.25rem; border: 1px solid #dfe3e8; border-left: 4px solid var(--chart-color); border-radius: .65rem; background: white; }
.chart-heading { display: flex; justify-content: space-between; align-items: center; gap: .75rem; flex-wrap: wrap; }
h3 { margin: 0; }
.total { color: #374151; font-size: .95rem; }
.chart-hint { margin: .6rem 0 1rem; color: #596273; font-size: .9rem; }
.row { display: grid; grid-template-columns: 6rem minmax(0, 1fr) 3rem; gap: .75rem; align-items: center; margin: .85rem 0; }
.track { background: #eef0f3; height: 1rem; border-radius: .25rem; overflow: hidden; }
.bar { background: var(--chart-color); height: 100%; border-radius: .25rem; }
.count { text-align: right; font-variant-numeric: tabular-nums; }
@media (max-width: 480px) {
    .chart { padding: .85rem; }
    .row { grid-template-columns: 5rem minmax(0, 1fr) 2rem; gap: .5rem; font-size: .85rem; }
}
</style>
