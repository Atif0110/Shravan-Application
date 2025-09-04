<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const showAddModal = ref(false);
const showEditModal = ref(false);
const showVideoModal = ref(false);
const selectedVideo = ref(null);
const isLoading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
const editingVideoId = ref(null);
const backend_url = 'http://127.0.0.1:5000';

// Separate form data for add and edit
const newVideo = ref({
  title: '',
  description: '',
  video_url: '',
  difficulty: 'easy',
  duration: ''
});

const editVideo = ref({
  title: '',
  description: '',
  video_url: '',
  difficulty: 'easy',
  duration: ''
});

// Yoga videos list
const yogaVideos = ref([]);

// Difficulty levels for the dropdown
const difficulties = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' }
];

onMounted(() => {
  fetchYogaVideos();
});

async function fetchYogaVideos() {
  try {
    const response = await fetch(`${backend_url}/api/yoga-videos`);
    if (!response.ok) {
      throw new Error('Failed to fetch yoga videos');
    }
    const data = await response.json();
    yogaVideos.value = data.videos || [];
    console.log(yogaVideos.value)
    
  } catch (error) {
    console.error('Error fetching yoga videos:', error);
    errorMessage.value = 'Failed to load yoga videos';
  }
}

function openAddModal() {
  // Reset form for new video
  newVideo.value = {
    title: '',
    description: '',
    video_url: '',
    difficulty: 'easy',
    duration: ''
  };
  errorMessage.value = '';
  successMessage.value = '';
  showAddModal.value = true;
}

function openEditModal(video) {
  // Populate form with existing video data
  editingVideoId.value = video.id;
  editVideo.value = {
    title: video.title,
    description: video.description,
    video_url: video.video_url,
    difficulty: video.difficulty,
    duration: video.duration
  };
  errorMessage.value = '';
  successMessage.value = '';
  showEditModal.value = true;
}

function openVideoModal(video) {
  selectedVideo.value = video;
  showVideoModal.value = true;
}

function closeVideoModal() {
  showVideoModal.value = false;
  selectedVideo.value = null;
}

function closeAddModal() {
  showAddModal.value = false;
}

function closeEditModal() {
  showEditModal.value = false;
  editingVideoId.value = null;
}

async function addVideo() {
  // Basic validation
  if (!newVideo.value.title || !newVideo.value.video_url || !newVideo.value.duration) {
    errorMessage.value = 'Please fill in all required fields';
    return;
  }

  isLoading.value = true;
  try {
    const response = await fetch(`${backend_url}/api/yoga-videos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newVideo.value)
    });
    
    if (!response.ok) {
      throw new Error('Failed to add yoga video');
    }

    successMessage.value = 'Yoga video added successfully!';
    
    // Refresh the videos list
    await fetchYogaVideos();
    
    // Close modal after success
    setTimeout(() => {
      closeAddModal();
      successMessage.value = '';
    }, 2000);
    
  } catch (error) {
    console.error('Error adding yoga video:', error);
    errorMessage.value = 'Failed to add yoga video. Please try again.';
  } finally {
    isLoading.value = false;
  }
}

async function updateVideo() {
  // Basic validation
  if (!editVideo.value.title || !editVideo.value.video_url || !editVideo.value.duration) {
    errorMessage.value = 'Please fill in all required fields';
    return;
  }

  isLoading.value = true;
  try {
    const response = await fetch(`${backend_url}/api/yoga-videos/${editingVideoId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(editVideo.value)
    });
    
    if (!response.ok) {
      throw new Error('Failed to update yoga video');
    }

    successMessage.value = 'Yoga video updated successfully!';
    
    // Refresh the videos list
    await fetchYogaVideos();
    
    // Close modal after success
    setTimeout(() => {
      closeEditModal();
      successMessage.value = '';
    }, 2000);
    
  } catch (error) {
    console.error('Error updating yoga video:', error);
    errorMessage.value = 'Failed to update yoga video. Please try again.';
  } finally {
    isLoading.value = false;
  }
}

async function deleteVideo(videoId) {
  if (!confirm('Are you sure you want to delete this yoga video?')) {
    return;
  }

  try {
    const response = await fetch(`${backend_url}/api/yoga-videos/${videoId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error('Failed to delete yoga video');
    }

    // Refresh the videos list
    await fetchYogaVideos();
    successMessage.value = 'Yoga video deleted successfully!';
    
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
    
  } catch (error) {
    console.error('Error deleting yoga video:', error);
    errorMessage.value = 'Failed to delete yoga video. Please try again.';
  }
}

function getDifficultyLabel(difficultyValue) {
  const difficulty = difficulties.find(diff => diff.value === difficultyValue);
  return difficulty ? difficulty.label : difficultyValue;
}

function getVideoId(url) {
  const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
}
</script>

<template>
  <div class="health-tips-container">
    <!-- <nav class="navbar">
      <div class="logo">
        <img src="../assets/Sharvan_logo.jpeg" alt="Sharvan Logo" class="logo-image" />
        <span style="margin-left: 10px">SHRAVAN</span>
      </div>
      <div class="nav-right">
        <button class="back-button" @click="goBack">
          🏠 Home
        </button>
      </div>
    </nav> -->

    <section class="header-section">
      <h1>Yoga Videos & Wellness</h1>
      <p class="subtitle">Share yoga content and wellness resources with the community</p>
    </section>

    <div class="content-container">
      <div v-if="successMessage" class="success-message-global">
        {{ successMessage }}
      </div>
      
      <div v-if="errorMessage" class="error-message-global">
        {{ errorMessage }}
      </div>

      <div class="action-bar">
        <button class="new-post-button" @click="openAddModal()">
          ✏️ Add New Yoga Video
        </button>
      </div>

      <div class="blog-grid">
        <div v-for="video in yogaVideos" :key="video.id" class="blog-card">
          <div class="blog-image">
            <img 
              :src="getVideoId(video.video_url) ? `https://img.youtube.com/vi/${getVideoId(video.video_url)}/maxresdefault.jpg` : 'https://placehold.co/300x200/e0f7fa/1f2937?text=Yoga'"
              :alt="video.title"
            >
            <div class="category-badge">{{ getDifficultyLabel(video.difficulty) }}</div>
            <div class="duration-badge">{{ video.duration }} min</div>
          </div>
          <div class="blog-content">
            <h2>{{ video.title }}</h2>
            <p class="blog-summary">{{ video.description }}</p>
            <div class="video-actions">
              <button class="watch-button" @click="openVideoModal(video)">
                ▶️ Watch Video
              </button>
              <button class="edit-button" @click="openEditModal(video)">
                ✏️ Edit
              </button>
              <button class="delete-button" @click="deleteVideo(video.id)">
                🗑️ Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Video Player Modal -->
    <div class="modal-overlay" v-if="showVideoModal" @click.self="closeVideoModal">
      <div class="video-modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedVideo?.title }}</h2>
          <button class="close-button" @click="closeVideoModal">×</button>
        </div>
        
        <div class="video-modal-body">
          <div class="video-info">
            <p class="video-description">{{ selectedVideo?.description }}</p>
            <div class="video-meta">
              <span class="difficulty-tag">{{ getDifficultyLabel(selectedVideo?.difficulty) }}</span>
              <span class="duration-tag">{{ selectedVideo?.duration }} minutes</span>
            </div>
          </div>
          
          <div class="video-container">
            <iframe 
              v-if="getVideoId(selectedVideo?.video_url)"
              :src="`https://www.youtube.com/embed/${getVideoId(selectedVideo?.video_url)}`"
              frameborder="0"
              allowfullscreen
              class="video-iframe"
            ></iframe>
            <div v-else class="video-error">
              <p>Unable to load video. Please check the video URL.</p>
              <a :href="selectedVideo?.video_url" target="_blank" class="external-link">
                Open in new tab
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Video Modal -->
    <div class="modal-overlay" v-if="showAddModal" @click.self="closeAddModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Add New Yoga Video</h2>
          <button class="close-button" @click="closeAddModal">×</button>
        </div>
        
        <div class="modal-body">
          <div v-if="successMessage" class="success-message">
            {{ successMessage }}
          </div>
          
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          
          <form @submit.prevent="addVideo">
            <div class="form-group">
              <label for="add-title">Video Title *</label>
              <input 
                type="text" 
                id="add-title" 
                v-model="newVideo.title" 
                placeholder="Enter yoga video title"
                required
              >
            </div>
            
            <div class="form-group">
              <label for="add-description">Description</label>
              <textarea 
                id="add-description" 
                v-model="newVideo.description" 
                placeholder="Describe the yoga practice, benefits, or instructions"
                rows="4"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="add-video_url">Video URL *</label>
              <input 
                type="url" 
                id="add-video_url" 
                v-model="newVideo.video_url" 
                placeholder="https://www.youtube.com/watch?v=..."
                required
              >
              <small>YouTube, Vimeo, or other video platform URLs</small>
            </div>
            
            <div class="form-group">
              <label for="add-difficulty">Difficulty Level</label>
              <select id="add-difficulty" v-model="newVideo.difficulty">
                <option v-for="difficulty in difficulties" :key="difficulty.value" :value="difficulty.value">
                  {{ difficulty.label }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="add-duration">Duration (minutes) *</label>
              <input 
                type="number" 
                id="add-duration" 
                v-model="newVideo.duration" 
                placeholder="e.g., 30"
                min="1"
                required
              >
            </div>
            
            <div class="form-actions">
              <button type="button" class="cancel-button" @click="closeAddModal">Cancel</button>
              <button type="submit" class="submit-button" :disabled="isLoading">
                <span v-if="isLoading">Adding...</span>
                <span v-else">Add Video</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit Video Modal -->
    <div class="modal-overlay" v-if="showEditModal" @click.self="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Edit Yoga Video</h2>
          <button class="close-button" @click="closeEditModal">×</button>
        </div>
        
        <div class="modal-body">
          <div v-if="successMessage" class="success-message">
            {{ successMessage }}
          </div>
          
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          
          <form @submit.prevent="updateVideo">
            <div class="form-group">
              <label for="edit-title">Video Title *</label>
              <input 
                type="text" 
                id="edit-title" 
                v-model="editVideo.title" 
                placeholder="Enter yoga video title"
                required
              >
            </div>
            
            <div class="form-group">
              <label for="edit-description">Description</label>
              <textarea 
                id="edit-description" 
                v-model="editVideo.description" 
                placeholder="Describe the yoga practice, benefits, or instructions"
                rows="4"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="edit-video_url">Video URL *</label>
              <input 
                type="url" 
                id="edit-video_url" 
                v-model="editVideo.video_url" 
                placeholder="https://www.youtube.com/watch?v=..."
                required
              >
              <small>YouTube, Vimeo, or other video platform URLs</small>
            </div>
            
            <div class="form-group">
              <label for="edit-difficulty">Difficulty Level</label>
              <select id="edit-difficulty" v-model="editVideo.difficulty">
                <option v-for="difficulty in difficulties" :key="difficulty.value" :value="difficulty.value">
                  {{ difficulty.label }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="edit-duration">Duration (minutes) *</label>
              <input 
                type="number" 
                id="edit-duration" 
                v-model="editVideo.duration" 
                placeholder="e.g., 30"
                min="1"
                required
              >
            </div>
            
            <div class="form-actions">
              <button type="button" class="cancel-button" @click="closeEditModal">Cancel</button>
              <button type="submit" class="submit-button" :disabled="isLoading">
                <span v-if="isLoading">Updating...</span>
                <span v-else">Update Video</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.health-tips-container {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #e0ffe0, #e6fff9);
  font-family: 'Poppins', sans-serif;
  display: flex;
  flex-direction: column;
  color: #333;
}


.header-section {
  padding: 30px;
  text-align: center;
}

h1 {
  color: #1f2937;
  font-size: 2.2rem;
  margin-bottom: 10px;
  font-weight: 600;
}

.subtitle {
  color: #6b7280;
  font-size: 1.1rem;
}


.content-container {
  flex: 1;
  padding: 0 30px 30px;
}


.action-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.new-post-button {
  background-color: #059669;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.new-post-button:hover {
  background-color: #047857;
  transform: translateY(-2px);
}


.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
}

.blog-card {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.blog-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.blog-image {
  height: 180px;
  position: relative;
}

.blog-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.category-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(5, 150, 105, 0.8);
  color: white;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.duration-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.blog-content {
  padding: 20px;
}

.blog-content h2 {
  font-size: 1.2rem;
  margin-bottom: 10px;
  color: #1f2937;
}

.blog-meta {
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 10px;
}

.blog-summary {
  font-size: 0.95rem;
  color: #4b5563;
  margin-bottom: 15px;
  line-height: 1.5;
}

.video-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.watch-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.watch-button:hover {
  background-color: #2563eb;
}

.edit-button {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-button:hover {
  background-color: #059669;
}

.delete-button {
  background-color: #6b7280;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-button:hover {
  background-color: #4b5563;
}

.success-message-global,
.error-message-global {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
  font-weight: 500;
}

.success-message-global {
  background-color: #d1fae5;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.error-message-global {
  background-color: #fee2e2;
  color: #ef4444;
  border: 1px solid #fecaca;
}


.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 1.5rem;
  color: #1f2937;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.success-message {
  background-color: #d1fae5;
  color: #059669;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.error-message {
  background-color: #fee2e2;
  color: #ef4444;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #4b5563;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.95rem;
}

.form-group textarea {
  resize: vertical;
}

.form-group small {
  font-size: 0.8rem;
  color: #6b7280;
  margin-top: 5px;
  display: block;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 20px;
}

.cancel-button {
  background-color: #f3f4f6;
  color: #4b5563;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}

.submit-button {
  background-color: #059669;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}

.submit-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.dark-mode {
  background: linear-gradient(135deg, #232526, #414345) !important;
  color: #e0e0e0 !important;
}

.dark-mode .health-tips-container {
  background: linear-gradient(135deg, #232526, #414345) !important;
  color: #e0e0e0 !important;
}

.dark-mode h1,
.dark-mode .subtitle,
.dark-mode .blog-content h2 {
  color: #e0e0e0 !important;
}

.dark-mode .blog-card {
  background-color: #2d2d2d !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}

.dark-mode .blog-summary,
.dark-mode .video-description {
  color: #bdbdbd !important;
}

.dark-mode .category-badge {
  background-color: #059669 !important;
  color: #fff !important;
}

.dark-mode .duration-badge {
  background-color: #333 !important;
  color: #fff !important;
}

.dark-mode .watch-button {
  background-color: #2563eb !important;
}

.dark-mode .edit-button {
  background-color: #059669 !important;
}

.dark-mode .delete-button {
  background-color: #444 !important;
}

.dark-mode .modal-content,
.dark-mode .video-modal-content {
  background-color: #232526 !important;
  color: #e0e0e0 !important;
}

.dark-mode .modal-header {
  border-bottom: 1px solid #444 !important;
}

.dark-mode .close-button {
  color: #bdbdbd !important;
}

.dark-mode .form-group input,
.dark-mode .form-group select,
.dark-mode .form-group textarea {
  background-color: #2d2d2d !important;
  color: #e0e0e0 !important;
  border: 1px solid #444 !important;
}

.dark-mode .form-group label {
  color: #bdbdbd !important;
}

.dark-mode .success-message-global {
  background-color: #064e3b !important;
  color: #a7f3d0 !important;
  border: 1px solid #059669 !important;
}

.dark-mode .error-message-global {
  background-color: #7f1d1d !important;
  color: #fecaca !important;
  border: 1px solid #ef4444 !important;
}

.dark-mode .success-message {
  background-color: #064e3b !important;
  color: #a7f3d0 !important;
}

.dark-mode .error-message {
  background-color: #7f1d1d !important;
  color: #fecaca !important;
}

.dark-mode .cancel-button {
  background-color: #333 !important;
  color: #bdbdbd !important;
}

.dark-mode .submit-button {
  background-color: #059669 !important;
  color: #fff !important;
}

.dark-mode .submit-button:disabled {
  background-color: #444 !important;
  color: #888 !important;
}

.dark-mode .video-container {
  background-color: #333 !important;
}

.dark-mode .difficulty-tag {
  background-color: #3730a3 !important;
  color: #ddd6fe !important;
}

.dark-mode .duration-tag {
  background-color: #333 !important;
  color: #e0e0e0 !important;
}

.dark-mode .external-link {
  color: #60a5fa !important;
}

.dark-mode .external-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .header-section {
    padding: 20px 15px;
  }
  
  .content-container {
    padding: 0 15px 20px;
  }
  
  .blog-grid {
    grid-template-columns: 1fr;
  }
  
  .action-bar {
    justify-content: center;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .cancel-button, .submit-button {
    width: 100%;
  }
}

.video-modal-content {
  background-color: white;
  border-radius: 12px;
  width: 95%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.video-modal-body {
  padding: 20px;
}

.video-info {
  margin-bottom: 20px;
}

.video-description {
  color: #4b5563;
  margin-bottom: 15px;
  line-height: 1.5;
}

.video-meta {
  display: flex;
  gap: 15px;
  align-items: center;
}

.difficulty-tag {
  background-color: #ddd6fe;
  color: #7c3aed;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.duration-tag {
  background-color: #f3f4f6;
  color: #374151;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.video-container {
  width: 100%;
  height: 0;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  position: relative;
  background-color: #f3f4f6;
  border-radius: 8px;
  overflow: hidden;
}

.video-iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #6b7280;
}

.external-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.external-link:hover {
  text-decoration: underline;
}

</style>