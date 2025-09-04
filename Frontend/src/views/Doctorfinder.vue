<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const backend_url = 'http://127.0.0.1:5000';
const GOOGLE_MAPS_API_KEY = 'AIzaSyDo4xYc0nxuba48917YsgfEsbfk03qEm88';

const isDarkMode = ref(localStorage.getItem('darkModePreference') === 'dark');
const doctors = ref([]);
const loading = ref(false);
const error = ref('');
const locationFetched = ref(false);
const locationSearch = ref('');
const searchPerformed = ref(false);
const userLocation = ref({ lat: null, lon: null });
const searchRadius = ref(1000);
const selectedSpecialist = ref('general physician');
const selectedDoctor = ref(null);
const showContactModal = ref(false);
const copySuccess = ref(false);

const specialistTypes = [
  { value: 'general physician', label: 'General Physician' },
  { value: 'cardiologist', label: 'Cardiologist' },
  { value: 'dermatologist', label: 'Dermatologist' },
  { value: 'neurologist', label: 'Neurologist' },
  { value: 'orthopedic', label: 'Orthopedic' },
  { value: 'pediatrician', label: 'Pediatrician' },
  { value: 'gynecologist', label: 'Gynecologist' },
  { value: 'obstetrician', label: 'Obstetrician' },
  { value: 'psychiatrist', label: 'Psychiatrist' },
  { value: 'dentist', label: 'Dentist' },
  { value: 'ophthalmologist', label: 'Ophthalmologist' },
  { value: 'ent specialist', label: 'ENT Specialist' }
];

const displayedDoctors = computed(() => {
  if (locationSearch.value.trim() === '') {
    return doctors.value;
  }

  return doctors.value.filter(doctor => 
    doctor.name.toLowerCase() || 
    (doctor.specialization && doctor.specialization.toLowerCase()) ||
    (doctor.hospital_name && doctor.hospital_name.toLowerCase()) ||
    (doctor.designation && doctor.designation.toLowerCase())
  );
});

async function reverseGeocode(lat, lng) {
  try {
    const response = await fetch(
      `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${GOOGLE_MAPS_API_KEY}`
    );

    if (!response.ok) {
      throw new Error('Geocoding request failed');
    }
    
    const data = await response.json();
    
    if (data.status === 'OK' && data.results.length > 0) {
      return data.results[0].formatted_address;
    } else {
      console.warn('Geocoding failed:', data.status);
      return null;
    }
  } catch (error) {
    console.error('Error in reverse geocoding:', error);
    return null;
  }
}

async function geocodePlace(placeName) {
  try {
    const response = await fetch(
      `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(placeName)}&key=${GOOGLE_MAPS_API_KEY}`
    );

    if (!response.ok) {
      throw new Error('Geocoding request failed');
    }
    
    const data = await response.json();
    
    if (data.status === 'OK' && data.results.length > 0) {
      const location = data.results[0].geometry.location;
      return {
        lat: parseFloat(location.lat.toFixed(4)),
        lng: parseFloat(location.lng.toFixed(4)),
        formatted_address: data.results[0].formatted_address
      };
    } else {
      console.warn('Geocoding failed:', data.status);
      return null;
    }
  } catch (error) {
    console.error('Error in geocoding:', error);
    return null;
  }
}

async function fetchDoctors(lat, lon, radius = 1000, specialist = 'general physician') {
  loading.value = true;
  error.value = '';

  try {
    const response = await fetch(`${backend_url}/api/doctor-finder`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        latitude: lat,
        longitude: lon,
        radius: radius
        // latitude: "12.993298",
        // longitude: "80.231686",
        // radius: 5000
        // specialist: specialist
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Doctor Finder API Response:', data);
    
    const doctorData = [];
    
    // Process the response which is directly the scraped data
    for (const [placeId, hospitalData] of Object.entries(data || {})) {
      const hospitalName = hospitalData.name || 'Unknown Hospital';
      const hospitalWebsite = hospitalData.website || null;

      // Process doctor_scrape data if available
      if (hospitalData.doctor_scrape && Array.isArray(hospitalData.doctor_scrape)) {
        hospitalData.doctor_scrape.forEach((doctorList, pageIndex) => {
          if (Array.isArray(doctorList)) {
            doctorList.forEach((doctor, doctorIndex) => {
              const doctorEntry = {
                id: `${placeId}_${pageIndex}_${doctorIndex}`,
                place_id: placeId,
                name: doctor.Name || 'Unknown Doctor',
                specialization: doctor.Specialization !== 'none' ? doctor.Specialization : specialist,
                designation: doctor.Designation || 'Doctor',
                contact: doctor.Contact !== 'none' ? doctor.Contact : null,
                hospital_name: hospitalName,
                hospital_website: hospitalWebsite,
                doctor_image: doctor.Doctor_Image !== 'none' ? doctor.Doctor_Image : null,
                type: 'doctor'
              };
              doctorData.push(doctorEntry);
            });
          }
        });
        console.log("DoctorData", doctorData);
      }
    }
    
    doctors.value = doctorData;
    searchPerformed.value = true;

    console.log("Doctors:", doctors.value);

    if (doctorData.length === 0) {
      error.value = 'No doctors found for the selected specialty in your area. Try expanding your search radius or selecting a different specialty.';
    }
    
  } catch (err) {
    console.error('Error fetching doctors:', err);
    error.value = `Failed to fetch doctors: ${err.message}`;
    doctors.value = [];
  } finally {
    loading.value = false;
  }
}

function getLocation() {
  if (!navigator.geolocation) {
    error.value = 'Geolocation is not supported by your browser.';
    return;
  }

  loading.value = true;
  error.value = '';

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords;
      userLocation.value = { 
        lat: parseFloat(latitude.toFixed(4)), 
        lon: parseFloat(longitude.toFixed(4)) 
      };
      locationFetched.value = true;
      fetchDoctors(userLocation.value.lat, userLocation.value.lon, searchRadius.value, selectedSpecialist.value);
    },
    (err) => {
      loading.value = false;
      error.value = `Unable to retrieve your location: ${err.message}`;
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000
    }
  );
}

async function manualSearch() {
  loading.value = true;
  error.value = '';
  searchPerformed.value = true;
  
  if (locationSearch.value.trim() !== '') {
    const geocodedLocation = await geocodePlace(locationSearch.value.trim());
    
    if (geocodedLocation) {
      userLocation.value = { 
        lat: parseFloat(geocodedLocation.lat.toFixed(4)), 
        lon: parseFloat(geocodedLocation.lng.toFixed(4)) 
      };
      fetchDoctors(userLocation.value.lat, userLocation.value.lon, searchRadius.value, selectedSpecialist.value);
    } else {
      loading.value = false;
      error.value = 'Could not find the location you entered. Please try a different location.';
      return;
    }
  } else {
    if (!userLocation.value.lat || !userLocation.value.lon) {
      error.value = 'Please enter a location or allow location access';
      loading.value = false;
      return;
    }
    
    fetchDoctors(userLocation.value.lat, userLocation.value.lon, searchRadius.value, selectedSpecialist.value);
  }
}

function contactDoctor(doctor) {
  if (doctor.contact) {
    selectedDoctor.value = doctor;
    showContactModal.value = true;
  } else {
    alert('Contact information not available');
  }
}

function openHospitalWebsite(doctor) {
  if (doctor.hospital_website) {
    window.open(doctor.hospital_website, '_blank');
  } else {
    alert('Hospital website not available');
  }
}

function closeContactModal() {
  showContactModal.value = false;
  selectedDoctor.value = null;
  copySuccess.value = false;
}

async function copyContact() {
  if (selectedDoctor.value?.contact) {
    try {
      await navigator.clipboard.writeText(selectedDoctor.value.contact);
      copySuccess.value = true;
      setTimeout(() => {
        copySuccess.value = false;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy contact:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = selectedDoctor.value.contact;
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

onMounted(() => {
  if (localStorage.getItem('darkModePreference') === 'dark') {
    document.body.classList.add('dark-mode');
  }
  getLocation();
});
</script>

<template>
  <div class="doctor-finder-container" :class="{ 'dark': isDarkMode }">
    <div class="content-section">
      <div class="page-header">
        <h1>👨‍⚕️ Find Nearby Doctors</h1>
        <p class="subtitle">Discover healthcare professionals and specialists in your area</p>
      </div>

      <div class="search-section">
        <div class="search-row">
          <div class="location-search">
            <label for="location" class="search-label">Search Location:</label>
            <input 
              id="location"
              type="text" 
              v-model="locationSearch" 
              placeholder="Search by location (e.g., 'Chennai', 'Taj Mahal') or leave empty for current location" 
              class="location-input"
              @keyup.enter="manualSearch"
            >
          </div>
          
          <div class="filter-controls">
            <div class="filter-group">
              <label for="specialist">Specialty:</label>
              <select v-model="selectedSpecialist" id="specialist" class="filter-select">
                <option v-for="specialist in specialistTypes" :key="specialist.value" :value="specialist.value">
                  {{ specialist.label }}
                </option>
              </select>
            </div>
            
            <div class="filter-group">
              <label for="radius">Radius:</label>
              <select v-model="searchRadius" id="radius" class="filter-select" @change="manualSearch">
                <option value="500">500m</option>
                <option value="1000">1km</option>
                <option value="2000">2km</option>
                <option value="5000">5km</option>
              </select>
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <button class="search-button" @click="manualSearch">
            🔍 Search Doctors
          </button>
          <button class="location-button" @click="getLocation">
            📍 Use Current Location
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Finding doctors...</p>
      </div>

      <div v-if="error" class="error-state">
        <p>{{ error }}</p>
        <button class="retry-button" @click="getLocation">Try Again</button>
      </div>

      <div v-if="!loading && !error && displayedDoctors.length === 0" class="empty-state">
        <p>No doctors found for the selected specialty. Try expanding your search radius or selecting a different specialty.</p>
      </div>

      <div v-if="!loading && displayedDoctors.length > 0" class="doctors-list">
        <div class="results-header">
          <h3>Found {{ displayedDoctors.length }} doctor(s) within {{ searchRadius/1000 }}km</h3>
        </div>

        <div v-for="doctor in displayedDoctors" :key="doctor.id" class="doctor-card">
          <div class="doctor-photo">
            <div class="doctor-avatar">
              {{ doctor.type === 'doctor' ? '👨‍⚕️' : '🏥' }}
            </div>
          </div>
          
          <div class="doctor-info">
            <h3 class="doctor-name">{{ doctor.name }}</h3>
            
            <div class="doctor-details">
              <div class="detail-item">
                <span class="detail-label">Specialty:</span>
                <span class="specialty-tag">{{ doctor.specialization }}</span>
              </div>
              
              <div class="detail-item" v-if="doctor.designation">
                <span class="detail-label">Designation:</span>
                <span>{{ doctor.designation }}</span>
              </div>
              
              <div class="detail-item" v-if="doctor.hospital_name">
                <span class="detail-label">Hospital:</span>
                <span>{{ doctor.hospital_name }}</span>
              </div>
              
              <div class="detail-item" v-if="doctor.contact">
                <span class="detail-label">Contact:</span>
                <span class="contact-info">{{ doctor.contact }}</span>
              </div>
              
              <div class="detail-item" v-if="doctor.error_message">
                <span class="detail-label">Note:</span>
                <span class="error-note">{{ doctor.error_message }}</span>
              </div>
            </div>
            
            <div class="action-buttons">
              <button class="contact-button" @click="contactDoctor(doctor)" v-if="doctor.contact">
                📧 Contact
              </button>
              <button class="website-button" @click="openHospitalWebsite(doctor)" v-if="doctor.hospital_website">
                🌐 Hospital Website
              </button>
              <button class="info-button" v-if="!doctor.contact && !doctor.hospital_website">
                ℹ️ Info Available
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contact Modal -->
    <div v-if="showContactModal" class="modal-overlay" @click="closeContactModal">
      <div class="contact-modal" @click.stop>
        <div class="modal-header">
          <h3>📧 Contact Doctor</h3>
          <button class="close-button" @click="closeContactModal">✕</button>
        </div>
        
        <div class="modal-content">
          <div class="doctor-info-modal">
            <h4>{{ selectedDoctor?.name }}</h4>
            <p class="doctor-specialty">{{ selectedDoctor?.specialization }}</p>
            <p class="doctor-hospital">{{ selectedDoctor?.hospital_name }}</p>
          </div>
          
          <div class="contact-display">
            <span class="contact-info">{{ selectedDoctor?.contact }}</span>
            <button 
              class="copy-button" 
              @click="copyContact"
              :class="{ 'copied': copySuccess }"
            >
              {{ copySuccess ? '✓ Copied!' : '📋 Copy' }}
            </button>
          </div>
          
          <div class="modal-actions">
            <button class="cancel-button" @click="closeContactModal">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Base styles - similar to HospitalFinder */
:global(html), :global(body) {
  margin: 0; padding: 0; width: 100%; height: 100%;
  overflow-x: hidden; box-sizing: border-box;
}

:global(#app) {
  margin: 0; padding: 0; width: 100%; height: 100%;
}

.doctor-finder-container {
  min-height: 100vh; 
  width: 100%;
  background: linear-gradient(135deg, #e0f7fa, #ffe6f0, #f0f9ff);
  font-family: 'Poppins', sans-serif;
  color: #333;
  padding-top: 0;
}

.dark-mode .doctor-finder-container{
  background: linear-gradient(135deg, #1a2435, #2d2d3a, #1a1f2c);
  color: #f1f1f1;
}

.content-section {
  padding: 30px; 
  max-width: 1200px;
  margin: 0 auto; 
  width: 100%; 
  flex: 1;
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

.search-section {
  display: flex; flex-direction: column;
  gap: 15px; margin-bottom: 30px;
  background-color: white; padding: 20px;
  border-radius: 16px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.dark-mode .search-section {
  background-color: #2a2a2a;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.search-row {
  display: flex; flex-direction: column; gap: 15px;
}

.location-search {
  display: flex; flex-direction: column; gap: 5px;
}

.search-label {
  font-size: 0.85rem; font-weight: 500;
  color: #6b7280; margin-bottom: 5px; margin-left: 2px;
}

.dark-mode .search-label {
  color: #9ca3af;
}

.filter-controls {
  display: flex; gap: 15px; flex-wrap: wrap;
}

.filter-group {
  flex: 1; min-width: 150px;
  display: flex; flex-direction: column; gap: 5px;
}

.filter-group label {
  font-size: 0.9rem; font-weight: 500; color: #6b7280;
}

.dark-mode .filter-group label {
  color: #9ca3af;
}

.location-input, .filter-select {
  width: 100%; padding: 12px 15px;
  border: 1px solid #e5e7eb; border-radius: 10px;
  font-size: 1rem; outline: none;
  background-color: #f9fafb; transition: all 0.3s ease;
}

.dark-mode .location-input, .dark-mode .filter-select {
  background-color: #374151; border-color: #4b5563; color: #f3f4f6;
}

.location-input:focus, .filter-select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.action-buttons {
  display: flex; gap: 10px;
}

.search-button, .location-button {
  flex: 1; padding: 12px 20px;
  border: none; border-radius: 10px;
  font-weight: 500; cursor: pointer;
  transition: all 0.3s ease; display: flex;
  align-items: center; justify-content: center;
  font-size: 0.95rem;
}

.search-button {
  background-color: #3b82f6; color: white;
}

.search-button:hover {
  background-color: #2563eb;
}

.location-button {
  background-color: #10b981; color: white;
}

.location-button:hover {
  background-color: #059669;
}

.loading-state, .error-state, .empty-state {
  text-align: center; padding: 40px;
  background-color: white; border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.dark-mode .loading-state, .dark-mode .error-state, .dark-mode .empty-state {
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

.retry-button {
  background-color: #3b82f6; color: white;
  border: none; padding: 10px 20px; border-radius: 10px;
  font-weight: 500; cursor: pointer; transition: all 0.3s ease;
}

.retry-button:hover {
  background-color: #2563eb;
}

.doctors-list {
  display: flex; flex-direction: column; gap: 20px;
}

.results-header {
  text-align: center; margin-bottom: 10px;
}

.results-header h3 {
  color: #4b5563; font-size: 1.1rem; margin: 0;
}

.dark-mode .results-header h3 {
  color: #d1d5db;
}

.doctor-card {
  display: flex; background-color: white;
  border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.dark-mode .doctor-card {
  background-color: #2a2a2a;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.doctor-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.doctor-photo {
  width: 120px; background-color: #f3f4f6;
  display: flex; align-items: center; justify-content: center;
  padding: 10px;
}

.dark-mode .doctor-photo {
  background-color: #374151;
}

.doctor-avatar {
  font-size: 4rem;
}

.doctor-info {
  flex: 1; padding: 20px;
  display: flex; flex-direction: column; gap: 12px;
}

.doctor-name {
  font-size: 1.3rem; font-weight: 600;
  color: #1f2937; margin: 0;
}

.dark-mode .doctor-name { color: #f3f4f6; }

.doctor-details {
  display: flex; flex-direction: column; gap: 8px;
}

.detail-item {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.95rem;
}

.detail-label {
  font-weight: 600; color: #6b7280;
  min-width: 90px;
}

.dark-mode .detail-label { color: #9ca3af; }

.specialty-tag {
  background-color: #dbeafe; color: #1e40af;
  padding: 4px 8px; border-radius: 12px;
  font-size: 0.85rem; font-weight: 500;
}

.dark-mode .specialty-tag {
  background-color: #1e3a8a; color: #bfdbfe;
}

.contact-info {
  color: #3b82f6; font-weight: 500;
}

.error-note {
  color: #f59e0b; font-style: italic;
}

.action-buttons {
  display: flex; gap: 10px; margin-top: 8px;
}

.contact-button, .website-button, .info-button {
  padding: 8px 16px; border: none; border-radius: 8px;
  font-weight: 500; cursor: pointer; transition: all 0.3s ease;
  font-size: 0.9rem;
}

.contact-button {
  background-color: #10b981; color: white;
}

.contact-button:hover {
  background-color: #059669;
}

.website-button {
  background-color: #3b82f6; color: white;
}

.website-button:hover {
  background-color: #2563eb;
}

.info-button {
  background-color: #6b7280; color: white;
}

.info-button:hover {
  background-color: #4b5563;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.contact-modal {
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.dark-mode .contact-modal {
  background-color: #2a2a2a;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #e5e7eb;
}

.dark-mode .modal-header {
  border-bottom-color: #4b5563;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
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
  padding: 5px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.dark-mode .close-button {
  color: #9ca3af;
}

.close-button:hover {
  background-color: #f3f4f6;
  color: #1f2937;
}

.dark-mode .close-button:hover {
  background-color: #374151;
  color: #f3f4f6;
}

.modal-content {
  padding: 25px;
}

.doctor-info-modal {
  margin-bottom: 25px;
  text-align: center;
}

.doctor-info-modal h4 {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2937;
}

.dark-mode .doctor-info-modal h4 {
  color: #f3f4f6;
}

.doctor-specialty {
  margin: 0 0 8px 0;
  color: #3b82f6;
  font-weight: 500;
}

.doctor-hospital {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.dark-mode .doctor-hospital {
  color: #9ca3af;
}

.contact-display {
  background-color: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  border: 2px solid #e5e7eb;
}

.dark-mode .contact-display {
  background-color: #374151;
  border-color: #4b5563;
}

.contact-display .contact-info {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2937;
  flex: 1;
}

.dark-mode .contact-display .contact-info {
  color: #f3f4f6;
}

.copy-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  min-width: 90px;
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
  gap: 12px;
  flex-direction: column;
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
  .filter-controls {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .doctor-card {
    flex-direction: column;
  }
  
  .doctor-photo {
    width: 100%; height: 80px;
    padding: 15px;
  }
  
  .doctor-avatar {
    font-size: 2.5rem;
  }
  
  .action-buttons {
    flex-direction: row;
  }
  
  .contact-modal {
    margin: 20px;
    width: calc(100% - 40px);
  }
  
  .contact-display {
    flex-direction: column;
    text-align: center;
  }
}
</style>
