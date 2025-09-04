<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { auth } from '@/stores/auth';

// Avatar imports
import defaultAvatar from '@/assets/avatars/default.png';
import maleAvatar from '@/assets/avatars/male.png';
import femaleAvatar from '@/assets/avatars/female.png';

const router = useRouter();
const auth_store = auth();
const backend_url = 'http://127.0.0.1:5000';

const isDarkMode = ref(localStorage.getItem('darkModePreference') === 'dark');
const isEditing = ref(false);
const loading = ref(false);
const error = ref('');
const success = ref('');

// Avatar options
const avatarOptions = [
  { id: 'default', src: defaultAvatar, label: 'Default' },
  { id: 'male', src: maleAvatar, label: 'Male' },
  { id: 'female', src: femaleAvatar, label: 'Female' }
];

// User data
const user = ref({
  user_id: null,
  user_name: '',
  email: '',
  mobile_number: '',
  gender: '',
  dob: '',
  address: '',
  avatar: 'default' // Add avatar field
});

// Form data for editing
const editForm = ref({
  user_name: '',
  email: '',
  mobile_number: '',
  gender: '',
  dob: '',
  address: '',
  password: '',
  avatar: 'default' // Add avatar field
});

// Validation errors
const validationErrors = ref({});
const userDetails = localStorage.getItem('user_details') ? JSON.parse(localStorage.getItem('user_details')) : {};
async function fetchUserData() {
  console.log(userDetails);
  if (!userDetails.user_id) {
    error.value = 'User not authenticated';
    return;
  }

  loading.value = true;
  error.value = '';

  try {
    const response = await fetch(`${backend_url}/api/users/${userDetails.user_id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.status === 'success') {
      user.value = { ...data.user, avatar: data.user.avatar || 'default' };
      editForm.value = { 
        ...data.user,
        avatar: data.user.avatar || 'default',
        password: '' // Don't populate password field
      };
    } else {
      throw new Error(data.error || 'Failed to fetch user data');
    }
  } catch (err) {
    console.error('Error fetching user data:', err);
    error.value = `Failed to fetch user data: ${err.message}`;
  } finally {
    loading.value = false;
  }
}

function validateForm() {
  validationErrors.value = {};
  
  if (!editForm.value.user_name?.trim()) {
    validationErrors.value.user_name = 'Username is required';
  }
  
  if (!editForm.value.email?.trim()) {
    validationErrors.value.email = 'Email is required';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editForm.value.email)) {
    validationErrors.value.email = 'Invalid email format';
  }
  
  if (!editForm.value.mobile_number?.trim()) {
    validationErrors.value.mobile_number = 'Mobile number is required';
  } else if (!/^\d{10}$/.test(editForm.value.mobile_number)) {
    validationErrors.value.mobile_number = 'Mobile number must be 10 digits';
  }
  
  if (!editForm.value.gender) {
    validationErrors.value.gender = 'Gender is required';
  }
  
  if (!editForm.value.dob) {
    validationErrors.value.dob = 'Date of birth is required';
  }
  
  return Object.keys(validationErrors.value).length === 0;
}

async function updateProfile() {
  if (!validateForm()) {
    return;
  }

  loading.value = true;
  error.value = '';
  success.value = '';

  try {
    const updateData = { ...editForm.value };
    
    // Remove password if it's empty
    if (!updateData.password?.trim()) {
      delete updateData.password;
    }
    
    // Remove user_id from update data
    delete updateData.user_id;

    const response = await fetch(`${backend_url}/api/users/${user.value.user_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.status === 'success') {
      user.value = { ...data.user };
      editForm.value = { 
        ...data.user,
        password: ''
      };
      
      // Update auth store
      auth_store.updateUser(data.user);
      
      success.value = 'Profile updated successfully!';
      isEditing.value = false;
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        success.value = '';
      }, 3000);
    } else {
      throw new Error(data.error || 'Failed to update profile');
    }
  } catch (err) {
    console.error('Error updating profile:', err);
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

function cancelEdit() {
  editForm.value = { 
    ...user.value,
    password: ''
  };
  validationErrors.value = {};
  isEditing.value = false;
  error.value = '';
}

function goHome() {
  router.push('/userdashboard');
}

function formatDate(dateString) {
  if (!dateString) return 'Not provided';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

// Emergency contacts data
const emergencyContacts = ref([]);
const showAddContact = ref(false);
const newContact = ref({
  contact_name: '',
  contact_number: '',
  relation: ''
});
const contactErrors = ref({});

// Phone modal data
const showPhoneModal = ref(false);
const selectedContact = ref(null);
const copySuccess = ref(false);

async function fetchEmergencyContacts() {
  try {

    const response = await fetch(`${backend_url}/api/emergency-contacts`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_id: userDetails.user_id })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    emergencyContacts.value = data.contacts || [];
  } catch (err) {
    console.error('Error fetching emergency contacts:', err);
    emergencyContacts.value = [];
  }
}

function validateContact() {
  contactErrors.value = {};
  
  if (!newContact.value.contact_name?.trim()) {
    contactErrors.value.contact_name = 'Contact name is required';
  }
  
  if (!newContact.value.contact_number?.trim()) {
    contactErrors.value.contact_number = 'Contact number is required';
  } else if (!/^\d{10}$/.test(newContact.value.contact_number)) {
    contactErrors.value.contact_number = 'Contact number must be 10 digits';
  }
  
  return Object.keys(contactErrors.value).length === 0;
}

async function addEmergencyContact() {
  if (!validateContact()) {
    return;
  }

  try {
    const response = await fetch(`${backend_url}/api/emergency-contacts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userDetails.user_id,
        contact_name: newContact.value.contact_name,
        contact_number: newContact.value.contact_number,
        relation: newContact.value.relation || null
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to add emergency contact');
    }

    const result = await response.json();
    
    // Reset form and refresh contacts
    newContact.value = {
      contact_name: '',
      contact_number: '',
      relation: ''
    };
    showAddContact.value = false;
    contactErrors.value = {};
    
    // Refresh the contacts list
    await fetchEmergencyContacts();
    
    success.value = 'Emergency contact added successfully!';
    setTimeout(() => {
      success.value = '';
    }, 3000);
  } catch (err) {
    console.error('Error adding emergency contact:', err);
    error.value = err.message;
  }
}

function cancelAddContact() {
  newContact.value = {
    contact_name: '',
    contact_number: '',
    relation: ''
  };
  contactErrors.value = {};
  showAddContact.value = false;
}

function closePhoneModal() {
  showPhoneModal.value = false;
  selectedContact.value = null;
  copySuccess.value = false;
}

async function copyPhoneNumber() {
  if (selectedContact.value?.number) {
    try {
      const phoneNumber = selectedContact.value.number.replace(/\s+/g, '');
      await navigator.clipboard.writeText(phoneNumber);
      copySuccess.value = true;
      setTimeout(() => {
        copySuccess.value = false;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy phone number:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = selectedContact.value.number.replace(/\s+/g, '');
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      copySuccess.value = true;
      setTimeout(() => {
        copySuccess.value = false;
      }, 2000);
    }
  }
}

function contactEmergency(contact) {
  if (contact.number) {
    selectedContact.value = contact;
    showPhoneModal.value = true;
  } else {
    alert('Phone number not available');
  }
}

const handleAvatarSelect = (avatarId) => {
  editForm.value.avatar = avatarId;
};

const getCurrentAvatar = () => {
  const selectedAvatar = avatarOptions.find(avatar => avatar.id === (user.value.avatar || 'default'));
  return selectedAvatar ? selectedAvatar.src : defaultAvatar;
};

const getEditAvatar = () => {
  const selectedAvatar = avatarOptions.find(avatar => avatar.id === (editForm.value.avatar || 'default'));
  return selectedAvatar ? selectedAvatar.src : defaultAvatar;
};

onMounted(() => {
  if (localStorage.getItem('darkModePreference') === 'dark') {
    document.body.classList.add('dark-mode');
  }
  fetchUserData();
  fetchEmergencyContacts();
});
</script>

<template>
  <div class="profile-container" :class="{ 'dark': isDarkMode }">
    <!-- Phone Modal -->
    <div v-if="showPhoneModal" class="modal-overlay" @click="closePhoneModal">
      <div class="phone-modal" @click.stop>
        <div class="modal-header">
          <h3>📞 Contact Emergency Contact</h3>
          <button class="close-button" @click="closePhoneModal">✕</button>
        </div>
        
        <div class="modal-content">
          <div class="contact-info-modal">
            <h4>{{ selectedContact?.name }}</h4>
            <p class="contact-relation-modal" v-if="selectedContact?.relation">{{ selectedContact?.relation }}</p>
          </div>
          
          <div class="phone-display">
            <span class="phone-number">{{ selectedContact?.number }}</span>
            <button 
              class="copy-button" 
              @click="copyPhoneNumber"
              :class="{ 'copied': copySuccess }"
            >
              {{ copySuccess ? '✓ Copied!' : '📋 Copy' }}
            </button>
          </div>
          
          <div class="modal-actions">
            <button class="cancel-button" @click="closePhoneModal">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="content-section">
      <div class="page-header">
        <h1>👤 My Profile</h1>
        <p class="subtitle">View and manage your personal information</p>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading profile...</p>
      </div>

      <div v-if="error" class="error-state">
        <p>{{ error }}</p>
        <button class="retry-button" @click="fetchUserData">Try Again</button>
      </div>

      <div v-if="success" class="success-state">
        <p>{{ success }}</p>
      </div>

      <div v-if="!loading && user.user_id" class="profile-content">
        <!-- Profile Information Card -->
        <div class="profile-card">
          <div class="profile-header">
            <div class="profile-avatar">
              <img 
                :src="getCurrentAvatar()" 
                :alt="user.user_name + ' avatar'" 
                class="avatar-image"
              />
            </div>
            <div class="profile-title">
              <h2>{{ user.user_name }}</h2>
              <p class="email">{{ user.email }}</p>
            </div>
            <div class="profile-actions">
              <button 
                v-if="!isEditing" 
                class="edit-button" 
                @click="isEditing = true"
              >
                ✏️ Edit Profile
              </button>
              <div v-if="isEditing" class="edit-actions">
                <button class="save-button" @click="updateProfile" :disabled="loading">
                  💾 Save Changes
                </button>
                <button class="cancel-button" @click="cancelEdit">
                  ❌ Cancel
                </button>
              </div>
            </div>
          </div>

          <!-- View Mode -->
          <div v-if="!isEditing" class="profile-details">
            <div class="detail-group">
              <div class="detail-item">
                <span class="detail-label">Username:</span>
                <span class="detail-value">{{ user.user_name || 'Not provided' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Email:</span>
                <span class="detail-value">{{ user.email || 'Not provided' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Mobile Number:</span>
                <span class="detail-value">{{ user.mobile_number || 'Not provided' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Gender:</span>
                <span class="detail-value">{{ user.gender || 'Not provided' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Date of Birth:</span>
                <span class="detail-value">{{ formatDate(user.dob) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Address:</span>
                <span class="detail-value">{{ user.address || 'Not provided' }}</span>
              </div>
            </div>
          </div>

          <!-- Edit Mode -->
          <div v-if="isEditing" class="profile-form">
            <!-- Avatar Selection -->
            <div class="form-group">
              <label>Choose Avatar</label>
              <div class="avatar-selection">
                <div 
                  v-for="avatar in avatarOptions" 
                  :key="avatar.id"
                  class="avatar-option"
                  :class="{ 'selected': editForm.avatar === avatar.id }"
                  @click="handleAvatarSelect(avatar.id)"
                >
                  <img 
                    :src="avatar.src" 
                    :alt="avatar.label" 
                    class="avatar-option-image"
                  />
                  <span class="avatar-label">{{ avatar.label }}</span>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label for="username">Username *</label>
              <input
                id="username"
                type="text"
                v-model="editForm.user_name"
                class="form-input"
                :class="{ 'error': validationErrors.user_name }"
                placeholder="Enter your username"
              />
              <span v-if="validationErrors.user_name" class="error-text">
                {{ validationErrors.user_name }}
              </span>
            </div>

            <div class="form-group">
              <label for="email">Email *</label>
              <input
                id="email"
                type="email"
                v-model="editForm.email"
                class="form-input"
                :class="{ 'error': validationErrors.email }"
                placeholder="Enter your email"
              />
              <span v-if="validationErrors.email" class="error-text">
                {{ validationErrors.email }}
              </span>
            </div>

            <div class="form-group">
              <label for="mobile">Mobile Number *</label>
              <input
                id="mobile"
                type="tel"
                v-model="editForm.mobile_number"
                class="form-input"
                :class="{ 'error': validationErrors.mobile_number }"
                placeholder="Enter your mobile number"
              />
              <span v-if="validationErrors.mobile_number" class="error-text">
                {{ validationErrors.mobile_number }}
              </span>
            </div>

            <div class="form-group">
              <label for="gender">Gender *</label>
              <select
                id="gender"
                v-model="editForm.gender"
                class="form-input"
                :class="{ 'error': validationErrors.gender }"
              >
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
              <span v-if="validationErrors.gender" class="error-text">
                {{ validationErrors.gender }}
              </span>
            </div>

            <div class="form-group">
              <label for="dob">Date of Birth *</label>
              <input
                id="dob"
                type="date"
                v-model="editForm.dob"
                class="form-input"
                :class="{ 'error': validationErrors.dob }"
              />
              <span v-if="validationErrors.dob" class="error-text">
                {{ validationErrors.dob }}
              </span>
            </div>

            <div class="form-group">
              <label for="address">Address</label>
              <textarea
                id="address"
                v-model="editForm.address"
                class="form-input textarea"
                placeholder="Enter your address"
                rows="3"
              ></textarea>
            </div>

            <div class="form-group">
              <label for="password">New Password (optional)</label>
              <input
                id="password"
                type="password"
                v-model="editForm.password"
                class="form-input"
                placeholder="Enter new password (leave blank to keep current)"
              />
            </div>
          </div>
        </div>

        <!-- Emergency Contacts Card -->
        <div class="emergency-contacts-card">
          <div class="card-header">
            <h3>🚨 Emergency Contacts</h3>
            <button 
              v-if="!showAddContact" 
              class="add-contact-button" 
              @click="showAddContact = true"
            >
              ➕ Add Contact
            </button>
          </div>

          <!-- Add Contact Form -->
          <div v-if="showAddContact" class="add-contact-form">
            <h4>Add New Emergency Contact</h4>
            
            <div class="form-group">
              <label for="contact_name">Contact Name *</label>
              <input
                id="contact_name"
                type="text"
                v-model="newContact.contact_name"
                class="form-input"
                :class="{ 'error': contactErrors.contact_name }"
                placeholder="Enter contact name"
              />
              <span v-if="contactErrors.contact_name" class="error-text">
                {{ contactErrors.contact_name }}
              </span>
            </div>

            <div class="form-group">
              <label for="contact_number">Contact Number *</label>
              <input
                id="contact_number"
                type="tel"
                v-model="newContact.contact_number"
                class="form-input"
                :class="{ 'error': contactErrors.contact_number }"
                placeholder="Enter 10-digit contact number"
              />
              <span v-if="contactErrors.contact_number" class="error-text">
                {{ contactErrors.contact_number }}
              </span>
            </div>

            <div class="form-group">
              <label for="relation">Relationship</label>
              <select
                id="relation"
                v-model="newContact.relation"
                class="form-input"
              >
                <option value="">Select relationship (optional)</option>
                <option value="Family">Family</option>
                <option value="Friend">Friend</option>
                <option value="Doctor">Doctor</option>
                <option value="Neighbor">Neighbor</option>
                <option value="Caregiver">Caregiver</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div class="contact-form-actions">
              <button class="save-contact-button" @click="addEmergencyContact">
                💾 Save Contact
              </button>
              <button class="cancel-contact-button" @click="cancelAddContact">
                ❌ Cancel
              </button>
            </div>
          </div>

          <!-- Contacts List -->
          <div v-if="emergencyContacts.length > 0" class="contacts-list">
            <div 
              v-for="contact in emergencyContacts" 
              :key="contact.contact_id" 
              class="contact-item"
            >
              <div class="contact-info">
                <div class="contact-name">{{ contact.name }}</div>
                <div class="contact-details">
                  <span class="contact-number">📞 {{ contact.number }}</span>
                  <span v-if="contact.relation" class="contact-relation">
                    | {{ contact.relation }}
                  </span>
                </div>
              </div>
              <div class="contact-actions">
                <button 
                  class="call-button" 
                  @click="contactEmergency(contact)"
                >
                  📞 Call
                </button>
              </div>
            </div>
          </div>

          <div v-else-if="!showAddContact" class="no-contacts">
            <p>No emergency contacts added yet.</p>
            <p class="suggestion">Add emergency contacts for quick access during emergencies.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:global(html), :global(body) {
  margin: 0; padding: 0; width: 100%; height: 100%;
  overflow-x: hidden; box-sizing: border-box;
}

:global(#app) {
  margin: 0; padding: 0; width: 100%; height: 100%;
}

.profile-container {
  min-height: 100vh; width: 100%;
  background: linear-gradient(135deg, #e0f7fa, #ffe6f0, #f0f9ff);
  font-family: 'Poppins', sans-serif;
  display: flex; flex-direction: column; color: #333;
  margin: 0; padding: 0; position: relative;
  height: auto; overflow: auto;
  padding-top: 80px; /* Add padding to account for global navbar */
}

.dark-mode .profile-container{
  background: linear-gradient(135deg, #1a2435, #2d2d3a, #1a1f2c);
  color: #f1f1f1;
}

/* Remove all navbar-related styles since we're using the global navbar */

.content-section {
  padding: 30px; max-width: 800px;
  margin: 0 auto; width: 100%; flex: 1;
}

.page-header {
  margin-bottom: 25px; text-align: center;
}

h1 {
  color: #1f2937; font-size: 2.2rem;
  margin-bottom: 10px; font-weight: 600;
}

.dark-mode h1 { color: #f3f4f6; }

.subtitle {
  color: #6b7280; font-size: 1.1rem; margin-bottom: 0;
}

.dark-mode .subtitle { color: #d1d5db; }

.loading-state, .error-state, .success-state {
  text-align: center; padding: 40px;
  background-color: white; border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.dark-mode .loading-state, .dark-mode .error-state, .dark-mode .success-state {
  background-color: #2a2a2a;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.loading-spinner {
  display: inline-block; width: 40px; height: 40px;
  border: 4px solid rgba(59, 130, 246, 0.2);
  border-radius: 50%; border-top-color: #3b82f6;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state p {
  color: #ef4444; margin-bottom: 15px;
}

.success-state p {
  color: #10b981; margin-bottom: 0;
}

.retry-button {
  background-color: #3b82f6; color: white;
  border: none; padding: 10px 20px; border-radius: 10px;
  font-weight: 500; cursor: pointer; transition: all 0.3s ease;
}

.retry-button:hover {
  background-color: #2563eb;
}

.profile-card {
  background-color: white; border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.dark-mode .profile-card {
  background-color: #2a2a2a;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.profile-header {
  display: flex; align-items: center;
  padding: 30px; gap: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.dark-mode .profile-header {
  border-bottom-color: #4b5563;
}

.profile-avatar {
  width: 80px; height: 80px;
  border-radius: 50%; display: flex;
  align-items: center; justify-content: center;
  flex-shrink: 0; overflow: hidden;
  border: 3px solid #e5e7eb;
}

.dark-mode .profile-avatar {
  border-color: #4b5563;
}

.avatar-image {
  width: 100%; height: 100%;
  object-fit: cover; border-radius: 50%;
}

.avatar-text {
  color: white; font-size: 2rem; font-weight: 600;
}

/* Avatar Selection Styles */
.avatar-selection {
  display: flex;
  gap: 15px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.avatar-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  padding: 10px;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.avatar-option:hover {
  background-color: #f3f4f6;
  border-color: #d1d5db;
}

.dark-mode .avatar-option:hover {
  background-color: #374151;
  border-color: #6b7280;
}

.avatar-option.selected {
  background-color: #eff6ff;
  border-color: #3b82f6;
}

.dark-mode .avatar-option.selected {
  background-color: #1e3a8a;
  border-color: #60a5fa;
}

.avatar-option-image {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 8px;
  border: 2px solid #e5e7eb;
}

.dark-mode .avatar-option-image {
  border-color: #4b5563;
}

.avatar-option.selected .avatar-option-image {
  border-color: #3b82f6;
}

.avatar-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: #6b7280;
}

.dark-mode .avatar-label {
  color: #9ca3af;
}

.avatar-option.selected .avatar-label {
  color: #3b82f6;
  font-weight: 600;
}

.dark-mode .avatar-option.selected .avatar-label {
  color: #60a5fa;
}

.profile-title {
  flex: 1;
}

.profile-title h2 {
  margin: 0 0 5px 0; font-size: 1.5rem;
  color: #1f2937; font-weight: 600;
}

.dark-mode .profile-title h2 { color: #f3f4f6; }

.email {
  margin: 0; color: #6b7280; font-size: 1rem;
}

.dark-mode .email { color: #9ca3af; }

.profile-actions {
  display: flex; gap: 10px;
}

.edit-button {
  background-color: #3b82f6; color: white;
  border: none; padding: 10px 20px; border-radius: 10px;
  font-weight: 500; cursor: pointer; transition: all 0.3s ease;
}

.edit-button:hover {
  background-color: #2563eb;
}

.edit-actions {
  display: flex; gap: 10px;
}

.save-button {
  background-color: #10b981; color: white;
  border: none; padding: 10px 20px; border-radius: 10px;
  font-weight: 500; cursor: pointer; transition: all 0.3s ease;
}

.save-button:hover:not(:disabled) {
  background-color: #059669;
}

.save-button:disabled {
  opacity: 0.6; cursor: not-allowed;
}

.cancel-button {
  background-color: #ef4444; color: white;
  border: none; padding: 10px 20px; border-radius: 10px;
  font-weight: 500; cursor: pointer; transition: all 0.3s ease;
}

.cancel-button:hover {
  background-color: #dc2626;
}

.profile-details {
  padding: 30px;
}

.detail-group {
  display: flex; flex-direction: column; gap: 20px;
}

.detail-item {
  display: flex; align-items: flex-start;
  padding: 15px 0; border-bottom: 1px solid #f3f4f6;
}

.dark-mode .detail-item {
  border-bottom-color: #374151;
}

.detail-label {
  font-weight: 600; color: #6b7280;
  min-width: 150px; margin-right: 20px;
}

.dark-mode .detail-label { color: #9ca3af; }

.detail-value {
  color: #1f2937; flex: 1;
}

.dark-mode .detail-value { color: #f3f4f6; }

.profile-form {
  padding: 30px; display: flex;
  flex-direction: column; gap: 20px;
}

.form-group {
  display: flex; flex-direction: column; gap: 5px;
}

.form-group label {
  font-weight: 600; color: #374151;
  font-size: 0.9rem;
}

.dark-mode .form-group label { color: #d1d5db; }

.form-input {
  padding: 12px 15px; border: 1px solid #e5e7eb;
  border-radius: 10px; font-size: 1rem; outline: none;
  background-color: #f9fafb; transition: all 0.3s ease;
}

.dark-mode .form-input {
  background-color: #374151; border-color: #4b5563;
  color: #f3f4f6;
}

.form-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.form-input.error {
  border-color: #ef4444;
}

.textarea {
  resize: vertical; min-height: 80px;
}

.error-text {
  color: #ef4444; font-size: 0.85rem;
  margin-top: 2px;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.emergency-contacts-card {
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.dark-mode .emergency-contacts-card {
  background-color: #2a2a2a;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 1px solid #e5e7eb;
}

.dark-mode .card-header {
  border-bottom-color: #4b5563;
}

.card-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #1f2937;
}

.dark-mode .card-header h3 {
  color: #f3f4f6;
}

.add-contact-button {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-contact-button:hover {
  background-color: #059669;
}

.add-contact-form {
  padding: 30px;
  border-bottom: 1px solid #e5e7eb;
}

.dark-mode .add-contact-form {
  border-bottom-color: #4b5563;
}

.add-contact-form h4 {
  margin: 0 0 20px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
}

.dark-mode .add-contact-form h4 {
  color: #f3f4f6;
}

.contact-form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.save-contact-button {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-contact-button:hover {
  background-color: #059669;
}

.cancel-contact-button {
  background-color: #ef4444;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-contact-button:hover {
  background-color: #dc2626;
}

.contacts-list {
  padding: 0 30px 30px 30px;
}

.contact-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #f3f4f6;
}

.dark-mode .contact-item {
  border-bottom-color: #374151;
}

.contact-item:last-child {
  border-bottom: none;
}

.contact-info {
  flex: 1;
}

.contact-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: #1f2937;
  margin-bottom: 5px;
}

.dark-mode .contact-name {
  color: #f3f4f6;
}

.contact-details {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: #6b7280;
}

.dark-mode .contact-details {
  color: #9ca3af;
}

.contact-number {
  font-weight: 500;
}

.contact-relation {
  font-style: italic;
}

.contact-actions {
  display: flex;
  gap: 10px;
}

.call-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.call-button:hover {
  background-color: #2563eb;
}

.no-contacts {
  padding: 40px 30px;
  text-align: center;
}

.no-contacts p {
  margin: 0 0 10px 0;
  color: #6b7280;
}

.dark-mode .no-contacts p {
  color: #9ca3af;
}

.suggestion {
  font-size: 0.9rem;
  font-style: italic;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.phone-modal {
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 400px;
  overflow: hidden;
}

.dark-mode .phone-modal {
  background-color: #2a2a2a;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f8fafc;
}

.dark-mode .modal-header {
  background-color: #374151;
  border-bottom-color: #4b5563;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2937;
}

.dark-mode .modal-header h3 {
  color: #f3f4f6;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: #ef4444;
  background-color: #fee2e2;
  border-radius: 50%;
}

.dark-mode .close-button {
  color: #9ca3af;
}

.dark-mode .close-button:hover {
  background-color: #7f1d1d;
}

.modal-content {
  padding: 25px;
}

.contact-info-modal {
  text-align: center;
  margin-bottom: 20px;
}

.contact-info-modal h4 {
  margin: 0 0 5px 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #1f2937;
}

.dark-mode .contact-info-modal h4 {
  color: #f3f4f6;
}

.contact-relation-modal {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
  font-style: italic;
}

.dark-mode .contact-relation-modal {
  color: #9ca3af;
}

.phone-display {
  background-color: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
}

.dark-mode .phone-display {
  background-color: #374151;
  border-color: #4b5563;
}

.phone-number {
  display: block;
  font-size: 1.4rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 15px;
  letter-spacing: 1px;
}

.dark-mode .phone-number {
  color: #f3f4f6;
}

.copy-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.copy-button:hover {
  background-color: #2563eb;
}

.copy-button.copied {
  background-color: #10b981;
}

.copy-button.copied:hover {
  background-color: #059669;
}

.modal-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.cancel-button {
  background-color: #f3f4f6;
  color: #4b5563;
  border: none;
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.dark-mode .cancel-button {
  background-color: #4b5563;
  color: #f3f4f6;
}

.cancel-button:hover {
  background-color: #e5e7eb;
  color: #1f2937;
}

.dark-mode .cancel-button:hover {
  background-color: #6b7280;
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column; text-align: center;
    gap: 15px;
  }
  
  .profile-actions {
    justify-content: center;
  }
  
  .edit-actions {
    flex-direction: column; width: 100%;
  }
  
  .detail-item {
    flex-direction: column; gap: 5px;
  }
  
  .detail-label {
    min-width: auto; margin-right: 0;
  }
  
  .card-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .contact-item {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .contact-form-actions {
    flex-direction: column;
  }
  
  .contact-details {
    flex-direction: column;
    gap: 5px;
  }
  
  .avatar-selection {
    justify-content: center;
  }
  
  .avatar-option {
    min-width: 80px;
  }
}
</style>