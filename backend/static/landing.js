// Vue displays the statistics supplied by Jinja when the page loads.
Vue.createApp({
    data() {
        return {
            stats: JSON.parse(document.getElementById('initial-statistics').textContent)
        }
    }
}).mount('#trek-statistics')
