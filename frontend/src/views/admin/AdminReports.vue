<script setup>
import { ref, onMounted } from 'vue'

const reports = ref([])
const loading = ref(true)
const error = ref('')

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

function barWidth(items, count) {
    return (count / Math.max(1, ...items.map(item => item.count)) * 100) + '%'
}

onMounted(loadReports)
</script>

<template>
    <section>
        <h2>Reports</h2>
        <p v-if="loading" role="status">Loading reports...</p>
        <p v-else-if="error" role="alert">{{ error }} <button @click="loadReports">Retry</button></p>
        <div v-else v-for="report in reports" :key="report.title" class="chart">
            <h3>{{ report.title }}</h3>
            <div v-for="item in report.items" :key="item.label" class="row">
                <span>{{ item.label }}</span>
                <div class="track" aria-hidden="true"><div class="bar" :style="{ width: barWidth(report.items, item.count) }"></div></div>
                <strong>{{ item.count }}</strong>
            </div>
        </div>
    </section>
</template>

<style scoped>
section { padding: 1rem; max-width: 45rem; }
.chart { margin-bottom: 2rem; }
.row { display: grid; grid-template-columns: 6rem 1fr 3rem; gap: 1rem; align-items: center; margin: 0.6rem 0; }
.track { background: #eee; height: 1rem; }
.bar { background: #175cf1; height: 100%; }
</style>
