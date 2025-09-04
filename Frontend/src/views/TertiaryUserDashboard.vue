<script setup>
import { useRouter } from 'vue-router';
import { ref, onMounted } from 'vue';
import { auth } from '@/stores/auth';

const router = useRouter();
const auth_store = auth();
const username = ref('Health Worker');

onMounted(() => {
  if (auth_store.userDetails) {
    try {
      const userDetails = JSON.parse(auth_store.userDetails);
      username.value = userDetails.username || 'Health Worker';
    } catch (e) {
      console.error('Error parsing user details:', e);
    }
  }
});

function goToFeature(path) {
  router.push(path);
}
</script>

<template>
  <div class="dashboard-container">
    <section class="welcome-section">
      <div class="welcome-content">
        <h1>Welcome, {{ username }} 👋</h1>
        <p class="subtitle">NGO / Health Center Dashboard</p>
        <p class="helper-text">Community well-being starts with data. Access tools to monitor and support health initiatives.</p>
      </div>
      <div class="welcome-image">
        <img src="https://placehold.co/400x300/e0ffe0/1f2937?text=Health+Center" alt="Health Center" class="care-image">
      </div>
    </section>

    <section class="features-section">
      <h2>Available Services</h2>
      <div class="card-container">
        <div class="feature-card" @click="goToFeature('/sharehealthtips')">
          <div class="card-icon">📢</div>
          <h3>Share Yoga Videos</h3>
          <p>Send yoga videos and information to community members</p>
        </div>
        
        <div class="feature-card" @click="goToFeature('/symptom-trends')">
          <div class="card-icon">📈</div>
          <h3>View Health Trends</h3>
          <p>Analyze community health patterns and statistics</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body, html {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden;
}

.dashboard-container {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #e0ffe0, #e6fff9, #e0f5ff);
  font-family: 'Poppins', sans-serif;
  display: flex;
  flex-direction: column;
  color: #333;
  padding: 0;
  margin: 0;
}

.dark-mode .dashboard-container {
  background: linear-gradient(135deg, #1a2435, #2d2d3a, #1a1f2c);
  color: #f1f1f1;
}

.welcome-section {
  display: flex;
  margin: 30px 30px;
  background-color: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.welcome-content {
  flex: 1;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.welcome-image {
  flex: 1;
  background-color: #ecfdf5;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.care-image {
  max-width: 100%;
  max-height: 250px;
  object-fit: cover;
  border-radius: 12px;
}

h1 {
  color: #1f2937;
  font-size: 2.2rem;
  margin-bottom: 10px;
  font-weight: 600;
}

.subtitle {
  color: #059669;
  font-size: 1.1rem;
  margin-bottom: 15px;
}

.helper-text {
  color: #6b7280;
  font-size: 0.95rem;
  line-height: 1.5;
}

.features-section {
  padding: 0 30px 30px;
}

.features-section h2 {
  color: #1f2937;
  font-size: 1.5rem;
  margin-bottom: 20px;
  font-weight: 500;
  padding-left: 10px;
  border-left: 4px solid #059669;
}

.card-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.feature-card {
  background-color: white;
  border-radius: 16px;
  padding: 25px;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  border-color: #a7f3d0;
  background-color: #d0f5ec;
}

.card-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.feature-card h3 {
  color: #1f2937;
  font-size: 1.2rem;
  margin-bottom: 10px;
  font-weight: 500;
}

.feature-card p {
  color: #6b7280;
  font-size: 0.95rem;
}

.dark-mode {
  background-color: #1a2435;
  color: #f1f1f1;
}
/* ...existing code... */

.dark-mode .dashboard-container {
  background: linear-gradient(135deg, #1a2435, #2d2d3a, #1a1f2c);
  color: #f1f1f1;
}

.dark-mode .welcome-section {
  background-color: #232a36;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.dark-mode .welcome-content {
  color: #f1f1f1;
}

.dark-mode .welcome-image {
  background-color: #232a36;
}

.dark-mode .care-image {
  border: 2px solid #374151;
}

.dark-mode h1 {
  color: #f3f4f6;
}

.dark-mode .subtitle {
  color: #38bdf8;
}

.dark-mode .helper-text {
  color: #a1a1aa;
}

.dark-mode .features-section h2 {
  color: #f3f4f6;
  border-left: 4px solid #38bdf8;
}

.dark-mode .feature-card {
  background-color: #232a36;
  border: 1px solid #374151;
  color: #f1f1f1;
  box-shadow: 0 4px 12px rgba(0,0,0,0.18);
}

.dark-mode .feature-card:hover {
  background-color: #1a2435;
  border-color: #38bdf8;
  box-shadow: 0 10px 20px rgba(0,0,0,0.25);
}

.dark-mode .card-icon {
  color: #38bdf8;
}

.dark-mode .feature-card h3 {
  color: #f3f4f6;
}

.dark-mode .feature-card p {
  color: #a1a1aa;
}


@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    margin: 20px 15px;
  }
  
  .welcome-content, .welcome-image {
    padding: 25px;
  }
  
  h1 {
    font-size: 1.8rem;
  }
  
  .features-section {
    padding: 0 15px 15px;
  }
  
  .card-container {
    grid-template-columns: 1fr;
  }

}
</style>