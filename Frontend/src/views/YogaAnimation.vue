<template>
  <div class="yoga-animation-container" :class="{ 'dark': isDarkMode }">
    <!-- Loading state -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading yoga asanas...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchAsanas" class="retry-btn">Try Again</button>
    </div>

    <!-- Main content -->
    <div v-else>
      <!-- Header Section -->
      <div class="yoga-header-section">
        <div class="yoga-header-content">
          <h1>Yoga Asana Animations</h1>
          <p class="subtitle">Interactive step-by-step animations to guide you through each yoga pose sequence</p>
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
      <!-- <img src="https://drive.google.com/thumbnail?id=1NVHUkG-24-bUbJ3TMFSrJ8GulbBSuzRF&sz=w600" alt="Improved Asanas" /> -->
      <!-- Improved Asanas Section -->
      <div class="asanas-section">
        <!-- No asanas found -->
        <div v-if="asanas.length === 0" class="no-asanas">
          <p>No yoga asanas found for the selected difficulty level.</p>
        </div>

        <!-- Asana grid -->
        <div v-else class="asana-grid">
          <div 
            v-for="asana in asanas" 
            :key="asana.asana_id"
            class="asana-card"
            @click="openAnimation(asana)"
          >
            <div class="asana-thumbnail">
              <div class="image-container">
                <img 
                  :src="getThumbnailUrl(asana.images[0]?.image_url)" 
                  :alt="asana.name"
                  class="thumbnail-image"
                  @load="handleImageLoad"
                  @error="handleThumbnailError"
                  loading="lazy"
                />
                <!-- <div class="image-loading" v-if="imageLoading[asana.asana_id]">
                  <div class="mini-spinner"></div>
                </div> -->
              </div>
              <div class="badges-container">
                <span class="duration-badge">{{ asana.duration_minutes }} min</span>
                <span class="difficulty-badge" :class="getDifficultyClass(asana.difficulty)">
                  {{ getDifficultyEmoji(asana.difficulty) }} {{ asana.difficulty }}
                </span>
              </div>
              <div class="play-overlay">
                <div class="play-icon">▶</div>
                <span class="play-text">View Animation</span>
              </div>
            </div>
            <div class="asana-details">
              <h3 class="asana-title">{{ asana.name }}</h3>
              <p class="sanskrit-name">{{ asana.sanskrit_name }}</p>
              <p class="asana-description">{{ truncateText(asana.description, 100) }}</p>
              <div class="asana-meta">
                <div class="meta-item">
                  <span class="meta-icon">📸</span>
                  <span class="pose-count">{{ asana.images.length }} poses</span>
                </div>
                <div class="meta-item">
                  <span class="meta-icon">✨</span>
                  <span class="benefits">{{ truncateText(asana.benefits, 50) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Animation Modal as separate overlay -->
  <div v-if="showModal" class="animation-modal" @click="closeModal" @keydown="handleKeydown">
    <div class="modal-backdrop"></div>
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ selectedAsana?.name }}</h3>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="animation-container">
          <div class="image-wrapper">
            <img 
              :src="getCurrentImage()" 
              :alt="`${selectedAsana?.name} pose ${currentIndex + 1}`"
              class="yoga-image"
              @load="handleModalImageLoad"
              @error="handleImageError"
            />
            <!-- <div class="modal-image-loading" v-if="modalImageLoading">
              <div class="spinner"></div>
            </div> -->
          </div>
          <div class="animation-controls">
            <button @click="toggleAnimation" class="control-btn">
              {{ isPlaying ? '⏸️ Pause' : '▶️ Play' }}
            </button>
            <button @click="resetAnimation" class="control-btn">
              🔄 Reset
            </button>
            <div class="speed-control">
              <label>Speed:</label>
              <input 
                type="range" 
                min="500" 
                max="5000" 
                step="200" 
                v-model="animationSpeed"
                @change="updateSpeed"
              />
              <span class="speed-value">{{ animationSpeed }}ms</span>
            </div>
          </div>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: getProgressPercentage() + '%' }"
            ></div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <div class="pose-info">
          <span class="current-pose">Pose {{ currentIndex + 1 }} of {{ images.length }}</span>
          <span class="difficulty-label" :class="getDifficultyClass(selectedAsana?.difficulty)">
            {{ getDifficultyEmoji(selectedAsana?.difficulty) }} {{ selectedAsana?.difficulty }}
          </span>
        </div>
        <p class="asana-instructions">{{ selectedAsana?.instructions }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { auth } from '@/stores/auth';
import axios from 'axios';

const router = useRouter();
const auth_store = auth();

// API data
const asanas = ref([]);
const loading = ref(true);
const error = ref(null);
const difficultyFilter = ref('all');
const isDarkMode = ref(false);
const difficultyLevels = ref([]);

// Modal and animation state
const showModal = ref(false);
const selectedAsana = ref(null);
const currentIndex = ref(0);
const isPlaying = ref(false);
const animationInterval = ref(null);
const animationSpeed = ref(5000);
const images = ref([]);

// New reactive variables for image loading states
const imageLoading = reactive({});
const modalImageLoading = ref(false);

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
  
  // Fetch yoga asanas from the backend
  await fetchAsanas();
});

onBeforeUnmount(() => {
  stopAnimation();
  window.removeEventListener('storage', handleStorageChange);
  window.removeEventListener('darkModeChanged', initializeDarkMode);
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

async function fetchAsanas() {
  loading.value = true;
  error.value = null;
  
  try {
    // Build the URL with query parameters if a filter is selected
    let url = `${auth_store.backend_url}/api/asanas`;
    if (difficultyFilter.value !== 'all') {
      url += `?difficulty=${difficultyFilter.value}`;
    }
    
    const response = await axios.get(url);
    
    if (response.data.status === 'success') {
      asanas.value = response.data.asanas;
      
      // Initialize loading states for each asana
      asanas.value.forEach(asana => {
        imageLoading[asana.asana_id] = true;
      });
      
      // Extract unique difficulty levels from the asanas
      const uniqueDifficulties = new Set();
      asanas.value.forEach(asana => {
        if (asana.difficulty) {
          uniqueDifficulties.add(asana.difficulty);
        }
      });
      difficultyLevels.value = Array.from(uniqueDifficulties);
    } else {
      error.value = 'Failed to load asanas';
    }
  } catch (err) {
    console.error('Error fetching asanas:', err);
    error.value = 'Could not load yoga asanas. Please try again later.';
  } finally {
    loading.value = false;
  }
}

// Improved image URL handling
function getThumbnailUrl(googleDriveUrl) {
  if (!googleDriveUrl) return '/images/placeholder.jpg';
  
  try {
    // Handle different Google Drive URL formats
    let fileId = null;
    
    // Format 1: /d/{fileId}/
    const shareMatch = googleDriveUrl.match(/\/d\/([a-zA-Z0-9-_]+)/);
    if (shareMatch) {
      fileId = shareMatch[1];
    }
    
    // Format 2: id={fileId}
    const idMatch = googleDriveUrl.match(/[?&]id=([a-zA-Z0-9-_]+)/);
    if (idMatch) {
      fileId = idMatch[1];
    }
    
    if (fileId) {
      // Use thumbnail API with higher resolution
      return `https://drive.google.com/thumbnail?id=${fileId}&sz=w600`;
    }
    
    return googleDriveUrl;
  } catch (error) {
    console.warn('Error processing image URL:', error);
    return '/images/placeholder.jpg';
  }
}

function getDirectImageUrl(googleDriveUrl) {
  return getThumbnailUrl(googleDriveUrl);
}

// New helper functions
function truncateText(text, maxLength) {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function handleImageLoad(event) {
  // Find the asana ID and mark loading as complete
  const imgElement = event.target;
  const card = imgElement.closest('.asana-card');
  if (card) {
    const asanaKey = card.getAttribute('data-asana-id');
    if (asanaKey) {
      imageLoading[asanaKey] = false;
    }
  }
}

function handleModalImageLoad() {
  modalImageLoading.value = false;
}

function handleThumbnailError(event) {
  console.warn(`Thumbnail failed to load: ${event.target.src}`);
  event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDQwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjRjVGNUY1Ii8+CjxwYXRoIGQ9Ik0xOTUgMTMwSDIwNVYxNzBIMTk1VjEzMFpNMTc1IDEzMEgxODVWMTcwSDE3NVYxMzBaTTE3NSAxNTBIMjA1VjE2MEgxNzVWMTUwWiIgZmlsbD0iI0NDQ0NDQyIvPgo8dGV4dCB4PSIyMDAiIHk9IjIwMCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5OTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5Zb2dhIEltYWdlPC90ZXh0Pgo8L3N2Zz4K';
  
  // Mark loading as complete
  const card = event.target.closest('.asana-card');
  if (card) {
    const asanaId = Object.keys(imageLoading).find(id => 
      card.querySelector(`[data-asana-id="${id}"]`) !== null
    );
    if (asanaId) {
      imageLoading[asanaId] = false;
    }
  }
}

// Filter asanas by difficulty
function filterByDifficulty(difficulty) {
  difficultyFilter.value = difficulty;
  fetchAsanas();
}

function getDifficultyClass(difficulty) {
  if (!difficulty) return 'difficulty-all';
  
  // Convert difficulty to lowercase and handle compound difficulties
  const normalizedDifficulty = difficulty.toLowerCase()
    .replace(/\s+to\s+/g, '-to-')  // Handle "Beginner to Intermediate"
    .replace(/\s+/g, '-');         // Replace remaining spaces with hyphens
  return `difficulty-${normalizedDifficulty}`;
}

function getDifficultyEmoji(difficulty) {
  if (!difficulty) return '⚪';
  
  // Define color-coded emojis for the difficulty levels in the new dataset
  const difficultyMap = {
    'beginner': '🟢',
    'beginner to intermediate': '🟡',
    'intermediate': '🟠',
    'advanced': '🔴',
    'easy': '🟢',
    'medium': '🟠',
    'hard': '🔴',
    'senior': '🔵',
    'all levels': '⚪'
  };
  
  // Default to a blue circle for other difficulties
  return difficultyMap[difficulty.toLowerCase()] || '🔵';
}

function getCurrentImage() {
  if (images.value.length === 0) {
    return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAwIiBoZWlnaHQ9IjQwMCIgdmlld0JveD0iMCAwIDYwMCA0MDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI2MDAiIGhlaWdodD0iNDAwIiBmaWxsPSIjRjVGNUY1Ii8+CjxjaXJjbGUgY3g9IjMwMCIgY3k9IjIwMCIgcj0iNTAiIGZpbGw9IiNEREREREQiLz4KPHRleHQgeD0iMzAwIiB5PSIyODAiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzk5OTk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSI+SW1hZ2UgTm90IEZvdW5kPC90ZXh0Pgo8L3N2Zz4K';
  }
  
  modalImageLoading.value = true;
  return getThumbnailUrl(images.value[currentIndex.value]?.image_url);
}

function getProgressPercentage() {
  if (images.value.length === 0) return 0;
  return ((currentIndex.value + 1) / images.value.length) * 100;
}

function openAnimation(asana) {
  selectedAsana.value = asana;
  images.value = asana.images.sort((a, b) => a.display_order - b.display_order);
  currentIndex.value = 0;
  showModal.value = true;
  modalImageLoading.value = true;
  document.body.style.overflow = 'hidden';
  preloadImages();
}

function closeModal() {
  stopAnimation();
  showModal.value = false;
  selectedAsana.value = null;
  images.value = [];
  modalImageLoading.value = false;
  document.body.style.overflow = 'auto';
}

function preloadImages() {
  images.value.forEach(imageObj => {
    const img = new Image();
    img.src = getThumbnailUrl(imageObj.image_url);
  });
}

function startAnimation() {
  if (animationInterval.value) {
    clearInterval(animationInterval.value);
  }
  
  animationInterval.value = setInterval(() => {
    nextFrame();
  }, animationSpeed.value);
  
  isPlaying.value = true;
}

function stopAnimation() {
  if (animationInterval.value) {
    clearInterval(animationInterval.value);
    animationInterval.value = null;
  }
  isPlaying.value = false;
}

function toggleAnimation() {
  if (isPlaying.value) {
    stopAnimation();
  } else {
    startAnimation();
  }
}

function nextFrame() {
  currentIndex.value = (currentIndex.value + 1) % images.value.length;
  modalImageLoading.value = true;
}

function resetAnimation() {
  stopAnimation();
  currentIndex.value = 0;
  modalImageLoading.value = true;
}

function updateSpeed() {
  if (isPlaying.value) {
    stopAnimation();
    startAnimation();
  }
}

function handleImageError(event) {
  console.warn(`Failed to load image: ${event.target.src}`);
  modalImageLoading.value = false;
  event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAwIiBoZWlnaHQ9IjQwMCIgdmlld0JveD0iMCAwIDYwMCA0MDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI2MDAiIGhlaWdodD0iNDAwIiBmaWxsPSIjRjVGNUY1Ii8+CjxjaXJjbGUgY3g9IjMwMCIgY3k9IjIwMCIgcj0iNTAiIGZpbGw9IiNEREREREQiLz4KPHRleHQgeD0iMzAwIiB5PSIyODAiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzk5OTk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSI+SW1hZ2UgTm90IEZvdW5kPC90ZXh0Pgo8L3N2Zz4K';
}

function handleKeydown(event) {
  if (event.key === 'Escape' && showModal.value) {
    closeModal();
  }
}
</script>

<style scoped>

/* Utility styles */
.yoga-img {
  max-width: 100%;   /* Shrinks to fit container */
  height: auto;      /* Maintains aspect ratio */
  display: block;    /* Removes inline gap */
  margin: 0 auto;    /* Centers image */
}

.container {
  width: 80%;        /* Adjust container width */
  max-width: 600px;  /* Prevents it from being too big */
  margin: 20px auto; /* Centers container */
}

.yoga-animation-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #e0f7fa, #ffe6f0, #f0f9ff);
  font-family: 'Poppins', sans-serif;
  padding: 20px;
}

.dark-mode .yoga-animation-container {
  background: linear-gradient(135deg, #1e293b, #334155, #475569);
  color: #f8fafc;
}

.loading-container, .error-message {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
  color: #2563eb;
  font-weight: 500;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(30, 58, 138, 0.2);
  border-top: 4px solid #1e3a8a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background: linear-gradient(135deg, #3b82f6, #10b981);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  cursor: pointer;
  margin-top: 20px;
  font-weight: 600;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
}

.yoga-header-section {
  text-align: center;
  color: #2563eb;
  margin-bottom: 40px;
}

.yoga-header-section h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 600;
  color: #1e40af;
}

.subtitle {
  color: #64748b;
  font-weight: 400;
  font-size: 1rem;
}

.filter-label {
  color: #64748b;
  font-weight: 500;
  font-size: 0.95rem;
}

.filter-btn {
  background: rgba(255, 255, 255, 0.8);
  color: #64748b;
  border: 2px solid rgba(37, 99, 235, 0.2);
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(37, 99, 235, 0.4);
  color: #2563eb;
}

.filter-btn.active {
  background: linear-gradient(135deg, #3b82f6, #10b981);
  color: white;
  border-color: transparent;
}

.asanas-section {
  max-width: 1200px;
  margin: 0 auto;
}

.no-asanas {
  text-align: center;
  color: #64748b;
  font-size: 1.1rem;
  margin-top: 50px;
  font-weight: 400;
}

.asana-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
  padding: 0 10px;
}

.asana-card {
  background: linear-gradient(135deg, #ffffff, #ffffff);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(59, 130, 246, 0.15);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  border: 2px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.asana-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.3);
}

.asana-thumbnail {
  position: relative;
  height: 220px;
  overflow: hidden;
  background: #ffffff;
}

.image-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
}

.thumbnail-image {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  object-position: center;
  transition: transform 0.3s ease;
  border-radius: 0;
  display: block;
}

.asana-card:hover .thumbnail-image {
  transform: scale(1.08);
}

.image-loading, .modal-image-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  padding: 10px;
}

.mini-spinner, .spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner {
  width: 30px;
  height: 30px;
}

.badges-container {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.duration-badge, .difficulty-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.duration-badge {
  background: linear-gradient(135deg, #1e3a8a, #374151);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.difficulty-badge {
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  color: #374151;
  border: 1px solid rgba(59, 130, 246, 0.3);
  backdrop-filter: blur(10px);
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #10b981, #3b82f6, #06b6d4);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  backdrop-filter: blur(5px);
}

.asana-card:hover .play-overlay {
  opacity: 0.75;
}

.play-icon {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #ffffff, #aec9db);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 28px;
  color: #1e3a8a;
  margin-bottom: 8px;
  transition: transform 0.2s ease;
  border: 2px solid rgba(255, 255, 255, 0.5);
}

.play-overlay:hover .play-icon {
  transform: scale(1.1);
}

.play-text {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.asana-details {
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
}

.asana-title {
  margin: 0 0 6px 0;
  color: #1e40af;
  font-size: 1.2rem;
  font-weight: 600;
  line-height: 1.3;
}

.sanskrit-name {
  color: #ec4899;
  font-style: italic;
  margin-bottom: 12px;
  font-size: 0.9rem;
  font-weight: 400;
}

.asana-description {
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 16px;
  font-weight: 400;
}

.asana-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-icon {
  font-size: 1rem;
}

.pose-count, .benefits {
  background: rgba(255, 255, 255, 0.6);
  color: #2563eb;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid rgba(37, 99, 235, 0.2);
}

/* Fixed Modal Overlay Styles */
.animation-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
}

.modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  z-index: -1;
}

.modal-content {
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  border-radius: 20px;
  padding: 0;
  width: 800px;
  max-width: 90vw;
  height: 700px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
  transform: translateY(0);
  animation: modalSlideIn 0.3s ease-out;
  display: flex;
  flex-direction: column;
  border: 3px solid rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px);
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  padding: 20px 24px 16px;
  border-bottom: 2px solid rgba(59, 130, 246, 0.2);
  background: linear-gradient(135deg, #10b981, #3b82f6, #06b6d4);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 17px 17px 0 0;
  flex-shrink: 0;
}

.modal-header h3 {
  margin: 0;
  color: white;
  font-size: 1.3rem;
  font-weight: 600;
  max-width: calc(100% - 60px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.close-btn {
  background: rgba(255, 255, 255, 0.25);
  border: 2px solid rgba(255, 255, 255, 0.3);
  font-size: 24px;
  cursor: pointer;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.4);
  border-color: rgba(255, 255, 255, 0.6);
  transform: scale(1.1);
}

.modal-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.animation-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.image-wrapper {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(30, 58, 138, 0.15);
  flex: 1;
  min-height: 350px;
  max-height: 400px;
  background: linear-gradient(135deg, #ffffff, #ffffff);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(59, 130, 246, 0.2);
}

.yoga-image {
  max-width: 100%;
  max-height: 100%;
  width: 350px;
  height: 350px;
  object-fit: contain;
  transition: opacity 0.3s ease;
  border-radius: 8px;
}

.animation-controls {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
  flex-shrink: 0;
}

.control-btn {
  background: linear-gradient(135deg, #3b82f6, #10b981);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
  font-size: 0.9rem;
}

.control-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
  background: linear-gradient(135deg, #2563eb, #059669);
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #f8fafc, #ffffff);
  padding: 8px 16px;
  border-radius: 20px;
  border: 2px solid rgba(59, 130, 246, 0.2);
  backdrop-filter: blur(10px);
}

.speed-control label {
  font-weight: 500;
  color: #2563eb;
  font-size: 0.8rem;
}

.speed-control input[type="range"] {
  width: 100px;
  accent-color: #3b82f6;
}

.speed-value {
  font-size: 0.7rem;
  color: #10b981;
  font-weight: 500;
  min-width: 40px;
}

.progress-bar {
  margin-top: 16px;
  width: 100%;
  height: 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  transition: width 0.3s ease;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.modal-footer {
  padding: 16px 20px;
  border-top: 2px solid rgba(59, 130, 246, 0.2);
  background: linear-gradient(135deg, #f8fafc, #ffffff);
  border-radius: 0 0 17px 17px;
  flex-shrink: 0;
}

.pose-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 0;
}
.current-pose {
  font-weight: 500;
  color: #2563eb;
  font-size: 0.9rem;
}

.asana-instructions {
  margin: 0;
  color: #64748b;
  font-size: 0.85rem;
  line-height: 1.4;
  max-height: 60px;
  overflow-y: auto;
  font-weight: 400;
}

/* Dark mode with simplified text */
.dark-mode.loading-container, .dark-mode.error-message {
  color: #93c5fd;
}

.dark-mode.yoga-header-section {
  color: #93c5fd;
}

.dark-mode.yoga-header-section h1 {
  color: #dbeafe;
}

.dark-mode.subtitle,
.dark-mode.filter-label,
.dark-mode.no-asanas {
  color: #cbd5e0;
}

.dark-mode.filter-btn {
  background: rgba(45, 45, 58, 0.7);
  color: #cbd5e0;
  border-color: rgba(147, 197, 253, 0.3);
}

.dark-mode.filter-btn:hover {
  color: #93c5fd;
}

.dark-mode.asana-title {
  color: #dbeafe;
}

.dark-mode.sanskrit-name {
  color: #f9a8d4;
}

.dark-mode.asana-description {
  color: #cbd5e0;
}

.dark-mode.pose-count, .dark-mode.benefits {
  background: rgba(45, 45, 58, 0.6);
  color: #93c5fd;
  border-color: rgba(147, 197, 253, 0.3);
}

.dark-mode.current-pose {
  color: #93c5fd;
}

.dark-mode.asana-instructions {
  color: #cbd5e0;
}

.dark-mode.speed-control label {
  color: #93c5fd;
}

/* Enhanced thumbnail styles */
.asana-thumbnail {
  position: relative;
  height: 220px;
  overflow: hidden;
  background: #f8fafc;
}

.image-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
}

.thumbnail-image {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  object-position: center;
  transition: transform 0.3s ease;
  border-radius: 0;
  display: block;
}

.asana-card:hover .thumbnail-image {
  transform: scale(1.08);
}

/* Dark mode adjustments for thumbnails */
.dark-mode.asana-thumbnail {
  background: #2d3748;
}

.dark-mode.image-container {
  background: linear-gradient(135deg, #2d3748, #4b5568);
}

/* Enhanced responsive design for thumbnails */
@media (max-width: 768px) {
  .asana-thumbnail {
    height: 200px;
  }
  
  .thumbnail-image {
    object-fit: cover;
  }
}

@media (max-width: 480px) {
  .asana-thumbnail {
    height: 180px;
  }
}
</style>