//import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
import router from './router'

// The backend uses session-cookie auth. Without this, axios never sends the
// session cookie on cross-port requests (e.g. localhost:5173 -> localhost:5000),
// so every login-gated endpoint silently 401s even right after logging in.
axios.defaults.withCredentials = true

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
