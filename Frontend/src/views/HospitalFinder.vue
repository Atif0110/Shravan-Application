<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const backend_url = 'http://127.0.0.1:5000';
const GOOGLE_MAPS_API_KEY = 'AIzaSyDo4xYc0nxuba48917YsgfEsbfk03qEm88';

const isDarkMode = ref(localStorage.getItem('darkModePreference') === 'dark');
const hospitals = ref([]);
const loading = ref(false);
const error = ref('');
const locationFetched = ref(false);
const locationSearch = ref('');
const searchPerformed = ref(false);
const userLocation = ref({ lat: null, lon: null });
const searchRadius = ref(1000);
const selectedHospital = ref(null);
const showPhoneModal = ref(false);
const copySuccess = ref(false);

const displayedHospitals = computed(() => {
  if (locationSearch.value.trim() === '') {
    return hospitals.value;
  }
  
  const search = locationSearch.value.toLowerCase();
  return hospitals.value.filter(hospital => 
    hospital.name.toLowerCase().includes(search) || 
    (hospital.address && hospital.address.toLowerCase().includes(search)) ||
    (hospital.vicinity && hospital.vicinity.toLowerCase().includes(search))
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
        lat: location.lat,
        lng: location.lng,
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

async function fetchHospitals(lat, lon, radius = 1000) {
  loading.value = true;
  error.value = '';

  try {
    const response = await fetch(`${backend_url}/api/hospital-finder`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        latitude: lat,
        longitude: lon,
        radius: radius,
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('API Response:', data);
    
    if (data.status === 'success') {
      const hospitalData = [];
      
      for (const [placeId, details] of Object.entries(data.response || {})) {
        const hospitalLat = details.geometry?.location?.lat;
        const hospitalLng = details.geometry?.location?.lng;
        
        let geocodedAddress = null;
        if (hospitalLat && hospitalLng) {
          geocodedAddress = await reverseGeocode(hospitalLat, hospitalLng);
        }
        
        const hospital = {
          id: placeId,
          place_id: placeId,
          name: details.name || 'Unknown Hospital',
          address: geocodedAddress || details.formatted_address || details.vicinity || 'Address not available',
          originalAddress: details.formatted_address || details.vicinity || 'Address not available',
          geocodedAddress: geocodedAddress,
          vicinity: details.vicinity || '',
          rating: details.rating || 'N/A',
          user_ratings_total: details.user_ratings_total || 0,
          phone: details.formatted_phone_number || details.international_phone_number || null,
          website: details.website || null,
          opening_hours_raw: details.opening_hours || null,
          opening_hours: processOpeningHours(details.opening_hours),
          price_level: details.price_level || null,
          business_status: details.business_status || 'OPERATIONAL',
          location: {
            lat: hospitalLat || null,
            lng: hospitalLng || null
          },
          types: details.types || [],
          photos: details.photos || [],
          plus_code: details.plus_code || null
        };
        
        hospitalData.push(hospital);
      }
      
      hospitals.value = hospitalData;
      searchPerformed.value = true;
    } else if (data.status === 'no_places_found') {
      hospitals.value = [];
      error.value = 'No hospitals found in your area. Try expanding your search radius.';
    } else {
      throw new Error(data.error || 'Failed to fetch hospital information');
    }
    
  } catch (err) {
    console.error('Error fetching hospitals:', err);
    error.value = `Failed to fetch hospitals: ${err.message}`;
    hospitals.value = [];
  } finally {
    loading.value = false;
  }
}

function getOpenStatus(opening_hours_raw) {
  if (!opening_hours_raw || opening_hours_raw.open_now === undefined) {
    return { status: 'Unknown', isOpen: null };
  }
  
  return {
    status: opening_hours_raw.open_now ? 'Open now' : 'Closed now',
    isOpen: opening_hours_raw.open_now
  };
}

function processOpeningHours(opening_hours) {
  if (!opening_hours) return 'Hours not available';
  
  if (opening_hours.open_now !== undefined) {
    const status = opening_hours.open_now ? 'Open now' : 'Closed now';
    
    if (opening_hours.weekday_text && opening_hours.weekday_text.length > 0) {
      const today = new Date().getDay();
      const dayIndex = today === 0 ? 6 : today - 1;
      const todayHours = opening_hours.weekday_text[dayIndex] || opening_hours.weekday_text[0];
      return `${todayHours}`;
    }
    
    return status;
  }
  
  return 'Hours not available';
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
      userLocation.value = { lat: latitude, lon: longitude };
      locationFetched.value = true;
      fetchHospitals(latitude, longitude, searchRadius.value);
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
      userLocation.value = { lat: geocodedLocation.lat, lon: geocodedLocation.lng };
      fetchHospitals(geocodedLocation.lat, geocodedLocation.lng, searchRadius.value);
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
    
    fetchHospitals(userLocation.value.lat, userLocation.value.lon, searchRadius.value);
  }
}

function contactHospital(hospital) {
  if (hospital.phone) {
    selectedHospital.value = hospital;
    showPhoneModal.value = true;
  } else {
    alert('Phone number not available');
  }
}

function openWebsite(hospital) {
  if (hospital.website) {
    window.open(hospital.website, '_blank');
  } else {
    alert('Website not available');
  }
}

function openInMaps(hospital) {
  if (hospital.location.lat && hospital.location.lng) {
    const url = `https://www.google.com/maps/search/?api=1&query=${hospital.location.lat},${hospital.location.lng}`;
    window.open(url, '_blank');
  } else {
    alert('Location coordinates not available');
  }
}

function closePhoneModal() {
  showPhoneModal.value = false;
  selectedHospital.value = null;
  copySuccess.value = false;
}

async function copyPhoneNumber() {
  if (selectedHospital.value?.phone) {
    try {
      const phoneNumber = selectedHospital.value.phone.replace(/\s+/g, '');
      await navigator.clipboard.writeText(phoneNumber);
      copySuccess.value = true;
      setTimeout(() => {
        copySuccess.value = false;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy phone number:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = selectedHospital.value.phone.replace(/\s+/g, '');
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

function makeCall() {
  if (selectedHospital.value?.phone) {
    window.open(`tel:${selectedHospital.value.phone.replace(/\s+/g, '')}`, '_self');
  }
}

function formatRating(rating, total) {
  if (rating === 'N/A' || !rating) return 'No rating';
  return `⭐ (${rating}/5)`;
}

onMounted(() => {
  if (localStorage.getItem('darkModePreference') === 'dark') {
    document.body.classList.add('dark-mode');
  }
  getLocation();
});
</script>

<template>
  <div class="hospital-finder-container" :class="{ 'dark': isDarkMode }">
    <div class="content-section">
      <div class="page-header">
        <h1>🏥 Find Nearby Hospitals</h1>
        <p class="subtitle">Discover hospitals, clinics, and medical centers in your area</p>
      </div>

      <div class="search-section">
        <div class="search-row">
          <div class="location-search">
            <label for="location" class="search-label">Search Pharmacy:</label>
            <input
              id="location" 
              type="text" 
              v-model="locationSearch" 
              placeholder="Search by location (e.g., 'Chennai', 'Taj Mahal') or leave empty for current location" 
              class="location-input"
              @keyup.enter="manualSearch"
            >
          </div>
          
          <div class="radius-control">
            <label for="radius">Search Radius:</label>
            <select v-model="searchRadius" id="radius" class="radius-select" @change="manualSearch">
              <option value="500">500m</option>
              <option value="1000">1km</option>
              <option value="2000">2km</option>
              <option value="5000">5km</option>
            </select>
          </div>
        </div>

        <div class="action-buttons">
          <button class="search-button" @click="manualSearch">
            🔍 Search Hospitals
          </button>
          <button class="location-button" @click="getLocation">
            📍 Use Current Location
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Finding hospitals...</p>
      </div>

      <div v-if="error" class="error-state">
        <p>{{ error }}</p>
        <button class="retry-button" @click="getLocation">Try Again</button>
      </div>

      <div v-if="!loading && !error && displayedHospitals.length === 0 && searchPerformed" class="empty-state">
        <p>No hospitals found in this area. Try expanding your search radius or different location.</p>
      </div>

      <div v-if="!loading && displayedHospitals.length > 0" class="hospitals-list">
        <div class="results-header">
          <h3>Found {{ displayedHospitals.length }} hospital(s) within {{ searchRadius/1000 }}km</h3>
        </div>

        <div v-for="hospital in displayedHospitals" :key="hospital.id" class="hospital-card">
          <div class="hospital-photo">
            <img src="../assets/hospital.png" alt="Hospital" class="hospital-image" />
          </div>
          
          <div class="hospital-info">
            <h3 class="hospital-name">{{ hospital.name }}</h3>
            
            <div class="hospital-details">
              <div class="detail-item">
                <span class="detail-label">Rating:</span>
                <span class="rating">{{ formatRating(hospital.rating) }}</span>
              </div>
              
              <div class="detail-item" v-if="hospital.opening_hours_raw">
                <span class="detail-label">Status:</span>
                <span class="status" :class="{ 
                  'open': getOpenStatus(hospital.opening_hours_raw).isOpen === true,
                  'closed': getOpenStatus(hospital.opening_hours_raw).isOpen === false 
                }">
                  {{ getOpenStatus(hospital.opening_hours_raw).status }}
                </span>
              </div>
              
              <div class="detail-item" v-if="hospital.business_status && hospital.business_status !== 'OPERATIONAL'">
                <span class="detail-label">Business:</span>
                <span class="business-status">{{ hospital.business_status }}</span>
              </div>
              
              <div class="detail-item" v-if="hospital.opening_hours">
                <span class="detail-label">Hours:</span>
                <span class="hours">{{ hospital.opening_hours }}</span>
              </div>
            </div>
            
            <div class="hospital-location">
              <span class="location-icon">📍</span> 
              <span>{{ hospital.address }}</span>
            </div>
            
            <div class="contact-info" v-if="hospital.phone || hospital.website">
              <div class="contact-item" v-if="hospital.phone">
                <span class="contact-label">📞 Phone:</span>
                <span>{{ hospital.phone }}</span>
              </div>
              <div class="contact-item" v-if="hospital.website">
                <span class="contact-label">🌐 Website:</span>
                <span class="website-text">{{ hospital.website.replace(/^https?:\/\//, '') }}</span>
              </div>
            </div>
            
            <div class="action-buttons">
              <button class="contact-button" @click="contactHospital(hospital)" v-if="hospital.phone">
                📞 Call
              </button>
              <button class="website-button" @click="openWebsite(hospital)" v-if="hospital.website">
                🌐 Website
              </button>
              <button class="maps-button" @click="openInMaps(hospital)" v-if="hospital.location.lat">
                🗺️ Directions
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Phone Modal -->
    <div v-if="showPhoneModal" class="modal-overlay" @click="closePhoneModal">
      <div class="phone-modal" @click.stop>
        <div class="modal-header">
          <h3>📞 Contact Hospital</h3>
          <button class="close-button" @click="closePhoneModal">✕</button>
        </div>
        
        <div class="modal-content">
          <div class="hospital-info-modal">
            <h4>{{ selectedHospital?.name }}</h4>
            <p class="hospital-address">{{ selectedHospital?.address }}</p>
          </div>
          
          <div class="phone-display">
            <span class="phone-number">{{ selectedHospital?.phone }}</span>
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
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Base styles - similar to PharmacyFinder */
:global(html), :global(body) {
  margin: 0; padding: 0; width: 100%; height: 100%;
  overflow-x: hidden; box-sizing: border-box;
}

:global(#app) {
  margin: 0; padding: 0; width: 100%; height: 100%;
}

.hospital-finder-container {
  min-height: 100vh; 
  width: 100%;
  background: linear-gradient(135deg, #e0f7fa, #ffe6f0, #f0f9ff);
  font-family: 'Poppins', sans-serif;
  color: #333;
  padding-top: 0;
}

.dark-mode .hospital-finder-container{
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
  display: flex; gap: 15px; width: 100%;
}

.search-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 5px;
  margin-left: 2px;
}

.location-search {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.radius-control {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.radius-control label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #6b7280;
}

.dark-mode .radius-control label {
  color: #9ca3af;
}

.location-input, .radius-select {
  width: 100%; padding: 12px 15px;
  border: 1px solid #e5e7eb; border-radius: 10px;
  font-size: 1rem; outline: none;
  background-color: #f9fafb; transition: all 0.3s ease;
}

.radius-select {
  width: 100%; padding: 12px 15px;
  border: 1px solid #e5e7eb; border-radius: 10px;
  font-size: 1rem; outline: none;
  background-color: #f9fafb; transition: all 0.3s ease;
}

.dark-mode .radius-select {
  background-color: #374151; border-color: #4b5563; color: #f3f4f6;
}

.radius-select:focus {
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
  border: 4px solid rgba(0, 130, 246, 0.2);
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

.hospitals-list {
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

.hospital-card {
  display: flex; background-color: white;
  border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.dark-mode .hospital-card {
  background-color: #2a2a2a;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.hospital-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.hospital-photo {
  width: 150px; background-color: #f3f4f6;
  display: flex; align-items: center; justify-content: center;
  padding: 10px;
}

.dark-mode .hospital-photo {
  background-color: #374151;
}

.hospital-image {
  width: 100px; height: 100px;
  object-fit: contain; border-radius: 8px;
}

.hospital-info {
  flex: 1; padding: 20px;
  display: flex; flex-direction: column; gap: 12px;
}

.hospital-name {
  font-size: 1.3rem; font-weight: 600;
  color: #1f2937; margin: 0;
}

.dark-mode .hospital-name { color: #f3f4f6; }

.hospital-details {
  display: flex; flex-direction: column; gap: 8px;
}

.detail-item {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.95rem;
}

.detail-label {
  font-weight: 600; color: #6b7280;
  min-width: 80px;
}

.dark-mode .detail-label { color: #9ca3af; }

.rating {
  color: #f59e0b; font-weight: 500;
}

.status.open {
  color: #10b981; font-weight: 500;
}

.status.closed {
  color: #ef4444; font-weight: 500;
}

.hospital-location {
  display: flex; align-items: flex-start; gap: 8px;
  color: #6b7280; font-size: 0.95rem; line-height: 1.4;
}

.dark-mode .hospital-location { color: #9ca3af; }

.contact-info {
  display: flex; flex-direction: column; gap: 6px;
  font-size: 0.9rem;
}

.contact-item {
  display: flex; align-items: center; gap: 8px;
}

.contact-label {
  font-weight: 500; color: #6b7280;
  min-width: 80px;
}

.dark-mode .contact-label { color: #9ca3af; }

.website-text {
  color: #3b82f6; text-decoration: underline;
}

.doctor-info {
  background-color: #f8fafc; padding: 15px;
  border-radius: 10px; border-left: 4px solid #3b82f6;
}

.dark-mode .doctor-info {
  background-color: #374151;
}

.doctor-info h4 {
  margin: 0 0 10px 0; color: #1f2937;
  font-size: 1rem; font-weight: 600;
}

.dark-mode .doctor-info h4 { color: #f3f4f6; }

.doctor-item {
  margin-bottom: 8px;
}

.doctor-name {
  font-weight: 600; color: #1f2937; font-size: 0.9rem;
}

.dark-mode .doctor-name { color: #f3f4f6; }

.doctor-specialty {
  color: #6b7280; font-size: 0.85rem;
  margin-left: 20px; font-style: italic;
}

.dark-mode .doctor-specialty { color: #9ca3af; }

.action-buttons {
  display: flex; gap: 10px; margin-top: 8px;
}

.contact-button, .website-button, .maps-button {
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

.maps-button {
  background-color: #f59e0b; color: white;
}

.maps-button:hover {
  background-color: #d97706;
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

.phone-modal {
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
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

.hospital-info-modal {
  margin-bottom: 25px;
  text-align: center;
}

.hospital-info-modal h4 {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2937;
}

.dark-mode .hospital-info-modal h4 {
  color: #f3f4f6;
}

.hospital-address {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.4;
}

.dark-mode .hospital-address {
  color: #9ca3af;
}

.phone-display {
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

.dark-mode .phone-display {
  background-color: #374151;
  border-color: #4b5563;
}

.phone-number {
  font-size: 1.4rem;
  font-weight: 600;
  color: #1f2937;
  letter-spacing: 1px;
  flex: 1;
}

.dark-mode .phone-number {
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

.call-now-button {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 14px 20px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.call-now-button:hover {
  background-color: #059669;
  transform: translateY(-1px);
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
  .search-row {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .hospital-card {
    flex-direction: column;
  }
  
  .hospital-photo {
    width: 100%; height: 80px;
    padding: 15px;
  }
  
  .hospital-image {
    width: 50px; height: 50px;
  }
  
  .action-buttons {
    flex-direction: row;
  }
  
  .phone-modal {
    margin: 20px;
    width: calc(100% - 40px);
  }
  
  .phone-display {
    flex-direction: column;
    text-align: center;
  }
  
  .phone-number {
    font-size: 1.2rem;
  }
  
  .modal-actions {
    gap: 10px;
  }
}
</style>