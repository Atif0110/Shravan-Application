<script setup>
import { secureFetch } from '@/api'
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { auth } from '@/stores/auth';

const router = useRouter();
const auth_store = auth();

const isDarkMode = ref(localStorage.getItem('darkModePreference') === 'dark');
const pincode = ref('');
const trends = ref([]);
const loading = ref(false);
const error = ref('');
const hasSearched = ref(false);

// Pre-fill with the logged-in user's own pincode if they registered with
// one, so the health worker isn't starting from a blank field every time.
onMounted(() => {
  if (auth_store.user_details) {
    try {
      const details = JSON.parse(auth_store.user_details);
      if (details.pincode) {
        pincode.value = details.pincode;
      }
    } catch (e) {
    }
  }
});

async function fetchTrends() {
  if (!pincode.value.trim()) {
    error.value = 'Please enter a pincode to analyze';
    return;
  }

  loading.value = true;
  error.value = '';
  hasSearched.value = true;

  try {
    const response = await secureFetch(
      `${auth_store.backend_url}/api/analytics/symptom-trends?pincode=${encodeURIComponent(pincode.value.trim())}`,
      {
        method: 'GET',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP error! status: ${response.status}`);
    }

    trends.value = data.trends || [];
  } catch (err) {
    error.value = err.message || 'Failed to load health trends';
    trends.value = [];
  } finally {
    loading.value = false;
  }
}

function goBack() {
  router.push('/tertiaryuser');
}

// Simple bar width so a longer list of trends still reads well without
// pulling in a whole charting library for one screen.
function barWidth(count) {
  if (!trends.value.length) return '0%';
  const max = Math.max(...trends.value.map(t => t.count));
  if (max === 0) return '0%';
  return `${Math.round((count / max) * 100)}%`;
}
</script>

<template>
  <div class="trends-container" :class="{ 'dark-mode': isDarkMode }">
    <nav class="navbar">
      <div class="logo">
        <span>📈 Health Trends</span>
      </div>
      <button class="back-button" @click="goBack">🏠 Dashboard</button>
    </nav>

    <div class="content-section">
      <div class="page-header">
        <h1>Community Health Trends</h1>
        <p class="subtitle">See which symptoms are being reported most often in a pincode area</p>
      </div>

      <div class="search-card">
        <label for="pincode-input">Pincode</label>
        <div class="search-row">
          <input
            id="pincode-input"
            v-model="pincode"
            type="text"
            placeholder="e.g. 226001"
            @keyup.enter="fetchTrends"
          />
          <button class="search-button" :disabled="loading" @click="fetchTrends">
            {{ loading ? 'Loading...' : 'Analyze' }}
          </button>
        </div>
        <p v-if="error" class="error-text">{{ error }}</p>
      </div>

      <div v-if="loading" class="status-card">
        <p>Loading health trends...</p>
      </div>

      <div v-else-if="hasSearched && trends.length === 0 && !error" class="status-card">
        <p>No symptom reports found for this pincode yet.</p>
      </div>

      <div v-else-if="trends.length > 0" class="trends-card">
        <h2>Reported symptoms for {{ pincode }}</h2>
        <div class="trend-list">
          <div v-for="item in trends" :key="item.symptom" class="trend-row">
            <div class="trend-label">{{ item.symptom }}</div>
            <div class="trend-bar-track">
              <div class="trend-bar-fill" :style="{ width: barWidth(item.count) }"></div>
            </div>
            <div class="trend-count">{{ item.count }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.trends-container {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #e0f7fa, #f0fff4, #f0f9ff);
  font-family: 'Poppins', sans-serif;
  color: #333;
}

.dark-mode {
  background: linear-gradient(135deg, #1a2435, #2d2d3a, #1a1f2c);
  color: #f1f1f1;
}

.navbar {
  background-color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.dark-mode .navbar {
  background-color: #232a36;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.logo {
  font-weight: 600;
  font-size: 1.1rem;
}

.back-button {
  background-color: #38bdf8;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
}

.content-section {
  max-width: 800px;
  margin: 0 auto;
  padding: 30px 20px 60px;
}

.page-header h1 {
  margin-bottom: 5px;
}

.subtitle {
  color: #6b7280;
}

.dark-mode .subtitle {
  color: #a1a1aa;
}

.search-card,
.status-card,
.trends-card {
  background-color: white;
  border-radius: 16px;
  padding: 25px;
  margin-top: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dark-mode .search-card,
.dark-mode .status-card,
.dark-mode .trends-card {
  background-color: #232a36;
  border: 1px solid #374151;
}

.search-row {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}

.search-row input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  font-size: 1rem;
}

.dark-mode .search-row input {
  background-color: #1a2435;
  border-color: #374151;
  color: #f1f1f1;
}

.search-button {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
}

.search-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-text {
  color: #dc2626;
  margin-top: 10px;
}

.trend-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 15px;
}

.trend-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.trend-label {
  width: 140px;
  font-weight: 500;
  flex-shrink: 0;
}

.trend-bar-track {
  flex: 1;
  height: 12px;
  background-color: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.dark-mode .trend-bar-track {
  background-color: #374151;
}

.trend-bar-fill {
  height: 100%;
  background-color: #38bdf8;
  border-radius: 6px;
}

.trend-count {
  width: 30px;
  text-align: right;
  font-weight: 600;
}
</style>
