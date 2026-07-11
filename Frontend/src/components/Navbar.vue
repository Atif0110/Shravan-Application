<template>
  <nav class="navbar" :class="{ 'dark': isDarkMode }">
    <div class="nav-left">
      <div class="logo" @click="goHome">
        <img src="../assets/Sharvan_logo.jpeg" alt="Sharvan Logo" class="logo-image" />
        <span class="logo-text">SHRAVAN</span>
      </div>
    </div>
    
    <div class="nav-center">
      <!-- Empty center section -->
    </div>
    
    <div class="nav-right">
      <div class="nav-features">
        <button class="nav-feature" @click="goHome">Home</button>
        <button class="nav-feature" @click="goToPharmacy">Pharmacy</button>
        <button class="nav-feature" @click="goToHospitals">Hospitals</button>
        <button class="nav-feature" @click="goToDoctors">Doctors</button>
        <button class="nav-feature" @click="goChatbot">Chatbot</button>
        <button class="nav-feature" @click="goToYoga">Yoga</button>
        
        <!-- Profile Dropdown -->
        <div class="profile-dropdown" @click="toggleProfileDropdown" v-click-outside="closeProfileDropdown">
          <button class="nav-feature profile-button" :class="{ 'active': showProfileDropdown }">
            Profile <span class="dropdown-arrow" :class="{ 'rotated': showProfileDropdown }">▼</span>
          </button>
          
          <div v-if="showProfileDropdown" class="dropdown-menu">
            <div v-if="!isAuthenticated" class="dropdown-item login-item" @click="goToLogin">
              Login
            </div>
            <template v-else>
              <div class="dropdown-item" @click="goToProfile">
                My Profile
              </div>
              <div class="dropdown-item logout-item" @click="logout">
                Logout
              </div>
            </template>
          </div>
        </div>
      </div>
      
      <button class="nav-button theme-button" @click="toggleTheme" title="Toggle theme">
        {{ isDarkMode ? '☀️' : '🌙' }}
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { auth } from '../stores/auth';

const router = useRouter();
const route = useRoute();
const auth_store = auth();
const isDarkMode = ref(false);
const showProfileDropdown = ref(false);
const userDetailsRef = ref({});

const isAuthenticated = computed(() => {
  // Check if userDetails is an empty object
  if (Object.keys(userDetailsRef.value).length === 0) {
    return false;
  } else {
    return true;
  }
});

// Watch for changes in localStorage
function updateUserDetails() {
  const userDetails = localStorage.getItem('user_details') 
    ? JSON.parse(localStorage.getItem('user_details')) 
    : {};
  userDetailsRef.value = userDetails;
}

// Custom directive for clicking outside
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value();
      }
    };
    document.addEventListener('click', el._clickOutside);
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside);
  }
};


onMounted(() => {
  // Initialize user details
  updateUserDetails();
  
  // Listen for storage changes (when localStorage is updated from other tabs/windows)
  window.addEventListener('storage', updateUserDetails);
  
  const savedTheme = localStorage.getItem('darkModePreference');
  if (savedTheme === 'dark') {
    isDarkMode.value = true;
    document.body.classList.add('dark-mode');
  }
});

// Watch for route changes to update user details
watch(() => route.path, () => {
  updateUserDetails();
});

function toggleProfileDropdown() {
  showProfileDropdown.value = !showProfileDropdown.value;
}

function closeProfileDropdown() {
  showProfileDropdown.value = false;
}

function goToProfile() {
  router.push('/profile');
  closeProfileDropdown();
}

function goHome() {
  // Navigate based on authentication status
  if (isAuthenticated.value) {
    // Get user role from localStorage
    const userDetails = localStorage.getItem('user_details')
      ? JSON.parse(localStorage.getItem('user_details'))
      : {};
    const role = userDetails.role;

    // Check user role and navigate to appropriate dashboard
    if (role === 'caretaker') {
      router.push('/caretaker');
    } else if (role === 'ngo') {
      router.push('/tertiaryuser');
    } else {
      router.push('/userdashboard');
    }
  } else {
    router.push('/');
  }
}

function goToLogin() {
  router.push('/userlogin');
}

function toggleTheme() {
  isDarkMode.value = !isDarkMode.value;
  document.body.classList.toggle('dark-mode', isDarkMode.value);
  localStorage.setItem('darkModePreference', isDarkMode.value ? 'dark' : 'light');
}

function logout() {
  auth_store.logout().then(() => {
    // Update user details immediately after logout
    updateUserDetails();
    router.push('/');
    closeProfileDropdown();
  });
}

function goToPharmacy() {
  router.push('/pharmacy-finder');
}

function goToHospitals() {
  router.push('/hospital-finder');
}

function goToDoctors() {
  router.push('/doctor-finder');
}

function goChatbot() {
  router.push('/chatbot');
}

function goToYoga() {
  router.push('/animation');
}
</script>

<style scoped>
.navbar {
  background-color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  width: 100%;
  box-sizing: border-box;
  transition: all 0.3s ease;
  min-height: 6rem;
}

.navbar.dark {
  background-color: rgb(30, 41, 59);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.nav-left,
.nav-center,
.nav-right {
  display: flex;
  align-items: center;
  height: 100%;
}

.nav-left {
  flex: 1;
  justify-content: flex-start;
}

.nav-center {
  flex: 2;
  justify-content: center;
}

.nav-right {
  flex: 2;
  justify-content: flex-end;
  gap: 10px;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #3b82f6;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.navbar.dark .logo {
  color: #60a5fa;
}

.logo-image {
  height: 36px;
  width: auto;
  object-fit: contain;
  display: inline-block;
  vertical-align: middle;
  border-radius: 6px;
}

.logo-text {
  margin-left: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.nav-features {
  display: flex;
  align-items: center;
  gap: 50px;
  margin-right: 30px;
}

.nav-feature {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 1.1rem;
  font-weight: 500;
  cursor: pointer;
  padding: 10px 0;
  position: relative;
  transition: all 0.3s ease;
  text-decoration: none;
}

.nav-feature::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background-color: #3b82f6;
  transition: width 0.3s ease;
}

.nav-feature:hover {
  color: #2563eb;
}

.nav-feature:hover::after {
  width: 100%;
}

.navbar.dark .nav-feature {
  color: #60a5fa;
}

.navbar.dark .nav-feature:hover {
  color: #93c5fd;
}

.navbar.dark .nav-feature::after {
  background-color: #60a5fa;
}

.nav-button {
  background-color: #f3f4f6;
  color: #4b5563;
  border: none;
  padding: 10px 15px;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 5px;
}

.navbar.dark .nav-button {
  background-color: #4b5563;
  color: #f3f4f6;
}

.nav-button:hover {
  background-color: #e5e7eb;
  color: #1f2937;
  transform: translateY(-2px);
}

.navbar.dark .nav-button:hover {
  background-color: #6b7280;
}

.theme-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  font-size: 1.2rem;
}

.theme-button:hover {
  background-color: #fef3c7;
  color: #92400e;
}

.navbar.dark .theme-button:hover {
  background-color: #451a03;
  color: #fbbf24;
}

.logout-button {
  background-color: #fee2e2;
  color: #dc2626;
}

.navbar.dark .logout-button {
  background-color: #7f1d1d;
  color: #fca5a5;
}

.logout-button:hover {
  background-color: #fecaca;
  color: #b91c1c;
}

.navbar.dark .logout-button:hover {
  background-color: #991b1b;
  color: #fef2f2;
}

.profile-dropdown {
  position: relative;
  display: inline-block;
}

.profile-button {
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.profile-button.active {
  color: #2563eb;
}

.navbar.dark .profile-button.active {
  color: #93c5fd;
}

.dropdown-arrow {
  transition: transform 0.3s ease;
  font-size: 0.8rem;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  min-width: 160px;
  z-index: 1000;
  margin-top: 8px;
  overflow: hidden;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.navbar.dark .dropdown-menu {
  background-color: #374151;
  border-color: #4b5563;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.dropdown-item {
  padding: 14px 18px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #374151;
  font-size: 0.95rem;
  font-weight: 500;
  border-bottom: 1px solid #f3f4f6;
  position: relative;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: #f8fafc;
  padding-left: 22px;
}

.navbar.dark .dropdown-item {
  color: #e5e7eb;
  border-bottom-color: #4b5563;
}

.navbar.dark .dropdown-item:hover {
  background-color: #4b5563;
}

.login-item {
  background-color: #dbeafe;
  color: #1e40af;
  font-weight: 600;
}

.login-item:hover {
  background-color: #bfdbfe;
  color: #1e3a8a;
}

.navbar.dark .login-item {
  background-color: #1e3a8a;
  color: #bfdbfe;
}

.navbar.dark .login-item:hover {
  background-color: #1e40af;
  color: #dbeafe;
}

.logout-item {
  color: #dc2626;
}

.navbar.dark .logout-item {
  color: #fca5a5;
}

.logout-item:hover {
  background-color: #fee2e2;
  color: #b91c1c;
}

.navbar.dark .logout-item:hover {
  background-color: #7f1d1d;
  color: #fef2f2;
}

/* Responsive Design */
@media (max-width: 768px) {
  .navbar {
    padding: 0 15px;
    flex-wrap: wrap;
    min-height: 5rem;
  }
  
  .nav-right {
    order: 3;
    width: 100%;
    margin-top: 10px;
    flex: none;
    justify-content: space-between;
  }
  
  .nav-features {
    gap: 25px;
    margin-right: 0;
  }
  
  .nav-feature {
    font-size: 0.9rem;
  }
  
  .logo-text {
    font-size: 1rem;
    margin-left: 8px;
  }
  
  .logo-image {
    height: 32px;
  }
  
  .nav-button {
    padding: 8px 12px;
    font-size: 0.8rem;
  }
  
  .dropdown-menu {
    right: -10px;
    min-width: 140px;
  }
  
  .dropdown-item {
    padding: 12px 16px;
    font-size: 0.9rem;
  }
  
  .dropdown-item:hover {
    padding-left: 20px;
  }
}

@media (max-width: 480px) {
  .navbar {
    padding: 8px 12px;
  }
  
  .logo-text {
    display: none;
  }
  
  .nav-features {
    gap: 20px;
    flex-wrap: wrap;
  }
  
  .nav-feature {
    font-size: 0.8rem;
  }
  
  .nav-button {
    padding: 6px 10px;
    font-size: 0.75rem;
  }
  
  .theme-button {
    width: 35px;
    height: 35px;
  }
  
  .dropdown-menu {
    right: -5px;
    min-width: 120px;
  }
  
  .dropdown-item {
    padding: 10px 14px;
    font-size: 0.8rem;
  }
  
  .dropdown-item:hover {
    padding-left: 18px;
  }
}
</style>