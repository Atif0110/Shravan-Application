<script setup>
import { ref, onMounted } from 'vue';

const isDarkMode = ref(false);

onMounted(() => {
  const savedTheme = localStorage.getItem('darkModePreference');
  if (savedTheme === 'dark') {
    isDarkMode.value = true;
    document.body.classList.add('dark-mode');
  }
});
</script>

<template>
  <div class="download-container" :class="{ 'dark': isDarkMode }">
    <div class="content-container">
      <div class="download-card">
        <div class="card-content">
          <h1>Download Shravan Mobile App</h1>
          <p class="subtitle">For the best experience with Medicine Reminders and other features, please use our mobile application</p>
          
          <div class="qr-container">
            <div class="qr-code">
              <!-- Sample QR code image - replace with your actual QR code -->
              <img src="../assets/mobile-app.png" alt="QR Code">
            </div>
            <div class="qr-instructions">
              <h3>How to get the app:</h3>
              <ol>
                <li>Scan this QR code with your phone's camera</li>
                <li>Follow the link to download the app</li>
                <li>Install and enjoy enhanced features!</li>
              </ol>
            </div>
          </div>
          
          <div class="app-benefits">
            <h3>Why use the mobile app?</h3>
            <ul>
              <li><span class="benefit-icon">⏰</span> Timely medication reminders with alarms</li>
              <li><span class="benefit-icon">📊</span> Track your medication adherence over time</li>
              <li><span class="benefit-icon">📱</span> Access even without internet connection</li>
              <li><span class="benefit-icon">🔔</span> Push notifications for important health updates</li>
            </ul>
          </div>
          
          <div class="download-buttons">
            <a href="https://github.com/Umang7198/soft-engg-project-may-2025-se-May-4/raw/refs/heads/main/final-mobile-apk/Shravan.apk" download class="download-btn android">
              <span class="material-icons">android</span> Download for Android
            </a>
          </div>
        </div>
        
        <div class="card-image">
          <img src="../assets/mobile_preview.jpg" alt="Mobile App Preview" class="app-preview">
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.download-container {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #e0f7fa, #ffe6f0, #f0f9ff);
  font-family: 'Poppins', sans-serif;
  color: #333;
  padding-top: 0;
}

.dark-mode .download-container{
  background: linear-gradient(135deg, #1a2435, #2d2d3a, #1a1f2c);
  color: #f1f1f1;
}

.content-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.download-card {
  background-color: white;
  border-radius: 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  display: flex;
  width: 90%;
  max-width: 1200px;
  overflow: hidden;
}

.dark-mode .download-card {
  background-color: #2a2a2a;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.card-content {
  flex: 3;
  padding: 40px;
}

.card-image {
  flex: 2;
  background-color: #f6f8fb;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.dark-mode .card-image {
  background-color: #333;
}

h1 {
  color: #1f2937;
  font-size: 2.2rem;
  margin-bottom: 10px;
  font-weight: 600;
}

.dark-mode h1 {
  color: #f3f4f6;
}

.subtitle {
  color: #6b7280;
  font-size: 1.1rem;
  margin-bottom: 30px;
}

.dark-mode .subtitle {
  color: #d1d5db;
}

.qr-container {
  display: flex;
  margin-bottom: 30px;
  background-color: #f9fafb;
  border-radius: 12px;
  padding: 20px;
}

.dark-mode .qr-container {
  background-color: #333;
}

.qr-code {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.qr-code img {
  max-width: 200px;
  border: 8px solid white;
  border-radius: 8px;
}

.dark-mode .qr-code img {
  border-color: #444;
}

.qr-instructions {
  flex: 2;
  padding-left: 30px;
}

.qr-instructions h3 {
  color: #1f2937;
  font-size: 1.3rem;
  margin-bottom: 15px;
}

.dark-mode .qr-instructions h3 {
  color: #f3f4f6;
}

.qr-instructions ol {
  padding-left: 20px;
}

.qr-instructions li {
  margin-bottom: 10px;
  color: #4b5563;
}

.dark-mode .qr-instructions li {
  color: #d1d5db;
}

.app-benefits {
  margin-bottom: 30px;
}

.app-benefits h3 {
  color: #1f2937;
  font-size: 1.3rem;
  margin-bottom: 15px;
}

.dark-mode .app-benefits h3 {
  color: #f3f4f6;
}

.app-benefits ul {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.app-benefits li {
  color: #4b5563;
  display: flex;
  align-items: center;
}

.dark-mode .app-benefits li {
  color: #d1d5db;
}

.benefit-icon {
  margin-right: 10px;
  font-size: 1.2rem;
}

.download-buttons {
  display: flex;
  gap: 15px;
}

.download-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 25px;
  border-radius: 10px;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.android {
  background-color: #4CAF50;
  color: white;
  border: none;
}

.android:hover {
  background-color: #3d8b40;
  transform: translateY(-2px);
}

.email {
  background-color: #3b82f6;
  color: white;
  border: none;
}

.email:hover {
  background-color: #2563eb;
  transform: translateY(-2px);
}

.app-preview {
  max-height: 600px;
  max-width: 100%;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.dark-mode .app-preview {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

@media (max-width: 992px) {
  .download-card {
    flex-direction: column;
  }
  
  .card-image {
    order: -1;
    padding: 30px;
  }
  
  .app-preview {
    max-height: 400px;
  }
}

@media (max-width: 768px) {
  .download-card {
    width: 95%;
  }
  
  .card-content {
    padding: 25px;
  }
  
  h1 {
    font-size: 1.8rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .qr-container {
    flex-direction: column;
  }
  
  .qr-code {
    margin-bottom: 20px;
  }
  
  .qr-instructions {
    padding-left: 0;
  }
  
  .app-benefits ul {
    grid-template-columns: 1fr;
  }
  
  .download-buttons {
    flex-direction: column;
  }
  
  .download-btn {
    width: 100%;
  }
}
</style>