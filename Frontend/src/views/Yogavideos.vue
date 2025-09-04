<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { auth } from '@/stores/auth';
import axios from 'axios';

const router = useRouter();
const auth_store = auth();
const yogaVideos = ref([]);
const loading = ref(true);
const error = ref(null);
const difficultyFilter = ref('all');
const isDarkMode = ref(false);
const showModal = ref(false);
const currentVideo = ref(null);
const difficultyLevels = ref([]);

onMounted(async () => {
  // Initialize dark mode from localStorage
  initializeDarkMode();
  
  // Listen for localStorage changes
  window.addEventListener('storage', handleStorageChange);
  
  // Listen for dark mode changes from the navbar
  window.addEventListener('darkModeChanged', initializeDarkMode);

  // Check for dark mode preference
  const savedTheme = localStorage.getItem('darkModePreference');
  if (savedTheme === 'dark') {
    isDarkMode.value = true;
    document.body.classList.add('dark-mode');
  }
  
  // Fetch yoga videos from the backend
  await fetchYogaVideos();
});


function initializeDarkMode() {
  const savedTheme = localStorage.getItem('darkModePreference');
  if (savedTheme === 'dark') {
    isDarkMode.value = true;
    document.body.classList.add('dark-mode');
  } else {
    isDarkMode.value = false;
    document.body.classList.remove('dark-mode');
  }
}

// Watch for localStorage changes (from other tabs/components)
function handleStorageChange(e) {
  if (e.key === 'darkModePreference') {
    initializeDarkMode();
  }
}

async function fetchYogaVideos() {
  loading.value = true;
  error.value = null;
  
  try {
    // Build the URL with query parameters if a filter is selected
    let url = `${auth_store.backend_url}/api/yoga-videos`;
    // if (difficultyFilter.value !== 'all') {
    //   url += `?difficulty=${difficultyFilter.value}`;
    // }
    
    const response = await axios.get(url);
    
    // Process videos to extract YouTube video IDs
    yogaVideos.value = response.data.videos.map(video => {
      // Extract YouTube video ID from the URL
      let videoId = '';
      if (video.video_url) {
        const urlObj = new URL(video.video_url);
        if (urlObj.hostname.includes('youtube.com')) {
          videoId = urlObj.searchParams.get('v') || '';
        } else if (urlObj.hostname.includes('youtu.be')) {
          videoId = urlObj.pathname.substring(1);
        }
      }
      
      return {
        ...video,
        videoId
      };
    });
    
    // Extract unique difficulty levels from the videos
    const uniqueDifficulties = new Set();
    yogaVideos.value.forEach(video => {
      if (video.difficulty) {
        uniqueDifficulties.add(video.difficulty);
      }
    });
    difficultyLevels.value = Array.from(uniqueDifficulties);
  } catch (err) {
    console.error('Error fetching yoga videos:', err);
    error.value = 'Could not load yoga videos. Please try again later.';
  } finally {
    loading.value = false;
  }
}

function filterByDifficulty(difficulty) {
  difficultyFilter.value = difficulty;
  fetchYogaVideos();
}

function getVideoThumbnail(videoId) {
  return videoId ? `https://img.youtube.com/vi/${videoId}/hqdefault.jpg` : '';
}

function getDifficultyClass(difficulty) {
  if (!difficulty) return 'difficulty-all';
  
  // Convert difficulty to lowercase and remove spaces for CSS class naming
  const normalizedDifficulty = difficulty.toLowerCase().replace(/\s+/g, '-');
  return `difficulty-${normalizedDifficulty}`;
}

function getDifficultyEmoji(difficulty) {
  if (!difficulty) return '⚪';
  
  // Define color-coded emojis for the most common difficulty levels
  const difficultyMap = {
    'beginner': '🟢',
    'intermediate': '🟠',
    'advanced': '🔴',
    'easy': '🟢',
    'medium': '🟠',
    'hard': '🔴',
    'senior': '�',
    'all levels': '⚪'
  };
  
  // Default to a blue circle for other difficulties
  return difficultyMap[difficulty.toLowerCase()] || '🔵';
}

function openVideoModal(video) {
  currentVideo.value = video;
  showModal.value = true;
  // Prevent scrolling when modal is open
  document.body.style.overflow = 'hidden';
}

function closeVideoModal() {
  showModal.value = false;
  currentVideo.value = null;
  // Re-enable scrolling
  document.body.style.overflow = 'auto';
}

// Close modal when Escape key is pressed
function handleKeydown(event) {
  if (event.key === 'Escape' && showModal.value) {
    closeVideoModal();
  }
}
</script>

<template>
  <div class="yoga-container" :class="{ 'dark': isDarkMode }">
    <div class="yoga-header-section">
      <div class="yoga-header-content">
        <h1>Age-Friendly Yoga Videos</h1>
        <p class="subtitle">Gentle exercises suitable for seniors to improve flexibility, balance, and overall well-being</p>
      </div>
      <div class="filter-controls">
        <div class="filter-label">Filter by difficulty:</div>
        <div class="filter-buttons">
          <button 
            class="filter-btn" 
            :class="{ active: difficultyFilter === 'all' }"
            @click="filterByDifficulty('all')"
          >
            All Levels
          </button>
          <button 
            v-for="level in difficultyLevels" 
            :key="level"
            class="filter-btn" 
            :class="[getDifficultyClass(level), { active: difficultyFilter === level }]"
            @click="filterByDifficulty(level)"
          >
            {{ getDifficultyEmoji(level) }} {{ level }}
          </button>
        </div>
      </div>
    </div>

    <div class="videos-section">
      <!-- Loading indicator -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading yoga videos...</p>
      </div>

      <!-- Error message -->
      <div v-else-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="fetchYogaVideos" class="retry-btn">Try Again</button>
      </div>

      <!-- No videos found -->
      <div v-else-if="yogaVideos.length === 0" class="no-videos">
        <p>No yoga videos found for the selected difficulty level.</p>
      </div>

      <!-- Video grid -->
      <div v-else class="video-grid">
        <div v-for="video in yogaVideos" :key="video.video_url" class="video-card">
          <div class="video-thumbnail">
            <img
              :src="getVideoThumbnail(video.videoId)"
              :alt="video.title"
              class="thumbnail"
            />
            <span class="duration-badge">{{ video.duration }} min</span>
            <span class="difficulty-badge" :class="getDifficultyClass(video.difficulty)">
              {{ getDifficultyEmoji(video.difficulty) }} {{ video.difficulty }}
            </span>
          </div>
          <div class="video-details">
            <h3 class="video-title">{{ video.title }}</h3>
            <p class="video-description">{{ video.description }}</p>
            <button class="play-btn" @click="openVideoModal(video)">
              <span class="play-icon">▶</span> Watch Video
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Video Modal -->
    <div v-if="showModal" class="video-modal" @click="closeVideoModal" @keydown="handleKeydown">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ currentVideo?.title }}</h3>
          <button class="close-btn" @click="closeVideoModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="video-wrapper">
            <iframe 
              v-if="currentVideo?.videoId" 
              :src="`https://www.youtube.com/embed/${currentVideo.videoId}?autoplay=1`" 
              frameborder="0" 
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
              allowfullscreen
            ></iframe>
            <div v-else class="video-error">
              <p>Sorry, the video cannot be played.</p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <p class="difficulty-label">
            <span :class="getDifficultyClass(currentVideo?.difficulty)">
              {{ getDifficultyEmoji(currentVideo?.difficulty) }} {{ currentVideo?.difficulty }}
            </span>
            <span class="duration-label">{{ currentVideo?.duration }} minutes</span>
          </p>
          <p class="video-description">{{ currentVideo?.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.yoga-container {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #e0f7fa, #ffe6f0, #f0f9ff);
  font-family: 'Poppins', sans-serif;
  color: #333;
  padding-top: 20px;
}

.dark-mode .yoga-container {
  background: linear-gradient(135deg, #1a2435, #2d2d3a, #1a1f2c);
  color: #f1f1f1;
}

.yoga-header-section {
  background-color: white;
  margin: 0px 20px;
  padding: 25px;
  border-radius: 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.dark-mode .yoga-header-section {
  background-color: #2a2a2a;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.yoga-header-content {
  text-align: center;
  margin-bottom: 20px;
}

h1 {
  color: #1f2937;
  font-size: 2rem;
  margin-bottom: 10px;
  font-weight: 600;
}

.dark-mode h1 {
  color: #f3f4f6;
}

.subtitle {
  color: #6b7280;
  font-size: 1.1rem;
  margin-bottom: 0;
}

.dark-mode .subtitle {
  color: #d1d5db;
}

.filter-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
}

.filter-label {
  font-weight: 500;
  margin-bottom: 10px;
  color: #4b5563;
}

.dark-mode .filter-label {
  color: #d1d5db;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background-color: white;
  color: #4b5563;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dark-mode .filter-btn {
  background-color: #374151;
  border-color: #4b5563;
  color: #e5e7eb;
}

.filter-btn.active {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.dark-mode .filter-btn.active {
  background-color: #60a5fa;
  border-color: #60a5fa;
}

.filter-btn:hover:not(.active) {
  background-color: #f3f4f6;
  border-color: #d1d5db;
}

.dark-mode .filter-btn:hover:not(.active) {
  background-color: #4b5563;
}

/* Generate dynamic styles for different difficulty levels */
.difficulty-beginner.active, .difficulty-easy.active { 
  background-color: #10b981; 
  border-color: #10b981; 
}

.difficulty-intermediate.active, .difficulty-medium.active { 
  background-color: #f59e0b; 
  border-color: #f59e0b; 
}

.difficulty-advanced.active, .difficulty-hard.active { 
  background-color: #ef4444; 
  border-color: #ef4444; 
}

.difficulty-senior.active { 
  background-color: #3b82f6; 
  border-color: #3b82f6; 
}

.videos-section {
  padding: 0 30px 30px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #3b82f6;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

.dark-mode .loading-spinner {
  border-color: rgba(255, 255, 255, 0.1);
  border-top-color: #60a5fa;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message, .no-videos {
  text-align: center;
  padding: 30px;
  background-color: white;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  margin-top: 20px;
}

.dark-mode .error-message, .dark-mode .no-videos {
  background-color: #2a2a2a;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.retry-btn {
  margin-top: 15px;
  padding: 8px 20px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retry-btn:hover {
  background-color: #2563eb;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.video-card {
  background-color: white;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.dark-mode .video-card {
  background-color: #2a2a2a;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.video-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.dark-mode .video-card:hover {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.video-thumbnail {
  position: relative;
  width: 100%;
  height: 200px;
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.duration-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 0.8rem;
}

.difficulty-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: white;
  color: #333;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 0.8rem;
  font-weight: 500;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.dark-mode .difficulty-badge {
  background-color: #374151;
  color: #e5e7eb;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
}

.difficulty-beginner, .difficulty-easy {
  background-color: #d1fae5;
  color: #065f46;
}

.dark-mode .difficulty-beginner, .dark-mode .difficulty-easy {
  background-color: #065f46;
  color: #d1fae5;
}

.difficulty-intermediate, .difficulty-medium {
  background-color: #fef3c7;
  color: #92400e;
}

.dark-mode .difficulty-intermediate, .dark-mode .difficulty-medium {
  background-color: #92400e;
  color: #fef3c7;
}

.difficulty-advanced, .difficulty-hard {
  background-color: #fee2e2;
  color: #b91c1c;
}

.dark-mode .difficulty-advanced, .dark-mode .difficulty-hard {
  background-color: #b91c1c;
  color: #fee2e2;
}

.difficulty-senior {
  background-color: #dbeafe;
  color: #1e40af;
}

.dark-mode .difficulty-senior {
  background-color: #1e40af;
  color: #dbeafe;
}

.video-details {
  padding: 20px;
}

.video-title {
  font-size: 1.2rem;
  margin-top: 0;
  margin-bottom: 10px;
  color: #1f2937;
}

.dark-mode .video-title {
  color: #f3f4f6;
}

.video-description {
  color: #6b7280;
  font-size: 0.95rem;
  margin-bottom: 15px;
  line-height: 1.5;
}

.dark-mode .video-description {
  color: #d1d5db;
}

.play-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  color: white;
  padding: 10px 20px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.play-btn:hover {
  background: linear-gradient(90deg, #2563eb, #3b82f6);
  transform: translateY(-2px);
}

.play-icon {
  margin-right: 8px;
}

@media (max-width: 768px) {
  .yoga-header-section {
    margin: 15px;
    padding: 15px;
  }
  
  h1 {
    font-size: 1.5rem;
  }
  
  .subtitle {
    font-size: 0.9rem;
  }
  
  .filter-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .filter-btn {
    width: 100%;
  }
  
  .videos-section {
    padding: 0 15px 15px;
  }
  
  .video-grid {
    grid-template-columns: 1fr;
  }
}

/* Video Modal Styles */
.video-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background-color: white;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  border-radius: 15px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.3);
}

.dark-mode .modal-content {
  background-color: #2a2a2a;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.dark-mode .modal-header {
  border-bottom-color: #4b5563;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.4rem;
  color: #1f2937;
  padding-right: 20px;
}

.dark-mode .modal-header h3 {
  color: #f3f4f6;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #ef4444;
}

.dark-mode .close-btn {
  color: #d1d5db;
}

.dark-mode .close-btn:hover {
  color: #f87171;
}

.modal-body {
  padding: 0;
  flex-grow: 1;
  overflow: hidden;
}

.video-wrapper {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
  height: 0;
  overflow: hidden;
}

.video-wrapper iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}

.video-error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  background-color: #f3f4f6;
  color: #6b7280;
  font-weight: 500;
}

.dark-mode .video-error {
  background-color: #374151;
  color: #d1d5db;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #e5e7eb;
}

.dark-mode .modal-footer {
  border-top-color: #4b5563;
}

.difficulty-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.difficulty-label span {
  padding: 5px 10px;
  border-radius: 5px;
  font-weight: 500;
}

.duration-label {
  background-color: #f3f4f6;
  color: #4b5563;
}

.dark-mode .duration-label {
  background-color: #374151;
  color: #d1d5db;
}
</style>