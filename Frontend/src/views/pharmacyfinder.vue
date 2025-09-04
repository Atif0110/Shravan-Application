<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const backend_url = 'http://127.0.0.1:5000';
const GOOGLE_MAPS_API_KEY = 'AIzaSyDo4xYc0nxuba48917YsgfEsbfk03qEm88'; // Add your API key here

const isDarkMode = ref(localStorage.getItem('darkModePreference') === 'dark');
const pharmacies = ref([]);
const loading = ref(false);
const error = ref('');
const locationFetched = ref(false);
const locationSearch = ref('');
const searchPerformed = ref(false);
const userLocation = ref({ lat: null, lon: null });
const searchRadius = ref(1000); // Default 1km radius

// Phone modal data
const showPhoneModal = ref(false);
const selectedPharmacy = ref(null);
const copySuccess = ref(false);

const displayedPharmacies = computed(() => {
  if (locationSearch.value.trim() === '') {
    return pharmacies.value;
  }
  
  const search = locationSearch.value.toLowerCase();
  return pharmacies.value.filter(pharmacy => 
    pharmacy.name.toLowerCase().includes(search) || 
    (pharmacy.address && pharmacy.address.toLowerCase().includes(search)) ||
    (pharmacy.vicinity && pharmacy.vicinity.toLowerCase().includes(search))
  );
});

// Add reverse geocoding function
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

// Add geocoding function for place names
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

async function fetchPharmacies(lat, lon, radius = 1000) {
  loading.value = true;
  error.value = '';

  try {
    const response = await fetch(`${backend_url}/api/pharmacy-finder`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        latitude: lat,
        longitude: lon,
        type: 'pharmacy',
        radius: radius
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('API Response:', data);
    if (data.status === 'success') {
      // Process the API response
      const pharmacyData = [];
      
      // Process each pharmacy and add geocoded address
      for (const [placeId, details] of Object.entries(data.response || {})) {
        const pharmacyLat = details.geometry?.location?.lat;
        const pharmacyLng = details.geometry?.location?.lng;
        
        // Get geocoded address if coordinates are available
        let geocodedAddress = null;
        if (pharmacyLat && pharmacyLng) {
          geocodedAddress = await reverseGeocode(pharmacyLat, pharmacyLng);
        }
        
        const pharmacy = {
          id: placeId,
          place_id: placeId,
          name: details.name || 'Unknown Pharmacy',
          // Use geocoded address if available, otherwise fall back to original
          address: geocodedAddress || details.formatted_address || details.vicinity || 'Address not available',
          originalAddress: details.formatted_address || details.vicinity || 'Address not available',
          geocodedAddress: geocodedAddress,
          vicinity: details.vicinity || '',
          rating: details.rating || 'N/A',
          user_ratings_total: details.user_ratings_total || 0,
          phone: details.formatted_phone_number || details.international_phone_number || null,
          website: details.website || null,
          // Store both original opening_hours object AND processed string
          opening_hours_raw: details.opening_hours || null,
          opening_hours: processOpeningHours(details.opening_hours),
          price_level: details.price_level || null,
          business_status: details.business_status || 'OPERATIONAL',
          location: {
            lat: pharmacyLat || null,
            lng: pharmacyLng || null
          },
          types: details.types || [],
          photos: details.photos || [],
          plus_code: details.plus_code || null
        };
        
        pharmacyData.push(pharmacy);
      }
      
      pharmacies.value = pharmacyData;
      searchPerformed.value = true;
    } else if (data.status === 'no_places_found') {
      pharmacies.value = [];
      error.value = 'No pharmacies found in your area. Try expanding your search radius.';
    } else {
      throw new Error(data.error || 'Failed to fetch pharmacy information');
    }
    
  } catch (err) {
    console.error('Error fetching pharmacies:', err);
    error.value = `Failed to fetch pharmacies: ${err.message}`;
    pharmacies.value = [];
  } finally {
    loading.value = false;
  }
}

// Add this function to get the open/closed status
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
  
  // Access the open_now property directly
  if (opening_hours.open_now !== undefined) {
    const status = opening_hours.open_now ? 'Open now' : 'Closed now';
    
    if (opening_hours.weekday_text && opening_hours.weekday_text.length > 0) {
      // Get today's hours
      const today = new Date().getDay();
      const dayIndex = today === 0 ? 6 : today - 1; // Convert Sunday (0) to Saturday (6)
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
      fetchPharmacies(latitude, longitude, searchRadius.value);
    },
    (err) => {
      loading.value = false;
      error.value = `Unable to retrieve your location: ${err.message}`;
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000 // 5 minutes
    }
  );
}

async function manualSearch() {
  loading.value = true;
  error.value = '';
  searchPerformed.value = true;
  
  // Check if user entered a location to search
  if (locationSearch.value.trim() !== '') {
    // Geocode the entered location
    const geocodedLocation = await geocodePlace(locationSearch.value.trim());
    
    if (geocodedLocation) {
      // Use geocoded coordinates
      userLocation.value = { lat: geocodedLocation.lat, lon: geocodedLocation.lng };
      fetchPharmacies(geocodedLocation.lat, geocodedLocation.lng, searchRadius.value);
    } else {
      loading.value = false;
      error.value = 'Could not find the location you entered. Please try a different location.';
      return;
    }
  } else {
    // Use current location
    if (!userLocation.value.lat || !userLocation.value.lon) {
      error.value = 'Please enter a location or allow location access';
      loading.value = false;
      return;
    }
    
    fetchPharmacies(userLocation.value.lat, userLocation.value.lon, searchRadius.value);
  }
}

function copyPhoneNumber() {
  if (selectedPharmacy.value?.phone) {
    try {
      const phoneNumber = selectedPharmacy.value.phone.replace(/\s+/g, '');
      navigator.clipboard.writeText(phoneNumber);
      copySuccess.value = true;
      setTimeout(() => {
        copySuccess.value = false;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy phone number:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = selectedPharmacy.value.phone.replace(/\s+/g, '');
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

function closePhoneModal() {
  showPhoneModal.value = false;
  selectedPharmacy.value = null;
  copySuccess.value = false;
}

function contactPharmacy(pharmacy) {
  if (pharmacy.phone) {
    selectedPharmacy.value = pharmacy;
    showPhoneModal.value = true;
  } else {
    alert('Phone number not available');
  }
}

function openWebsite(pharmacy) {
  if (pharmacy.website) {
    window.open(pharmacy.website, '_blank');
  } else {
    alert('Website not available');
  }
}

function openInMaps(pharmacy) {
  if (pharmacy.location.lat && pharmacy.location.lng) {
    const url = `https://www.google.com/maps/search/?api=1&query=${pharmacy.location.lat},${pharmacy.location.lng}`;
    window.open(url, '_blank');
  } else {
    alert('Location coordinates not available');
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
  <div class="pharmacy-finder-container" :class="{ 'dark': isDarkMode }">
    <!-- Phone Modal -->
    <div v-if="showPhoneModal" class="modal-overlay" @click="closePhoneModal">
      <div class="phone-modal" @click.stop>
        <div class="modal-header">
          <h3>📞 Contact Pharmacy</h3>
          <button class="close-button" @click="closePhoneModal">✕</button>
        </div>
        
        <div class="modal-content">
          <div class="pharmacy-info-modal">
            <h4>{{ selectedPharmacy?.name }}</h4>
            <p class="pharmacy-address">{{ selectedPharmacy?.address }}</p>
          </div>
          
          <div class="phone-display">
            <span class="phone-number">{{ selectedPharmacy?.phone }}</span>
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
        <h1>💊 Find Nearby Pharmacies</h1>
        <p class="subtitle">Discover pharmacies and medical stores in your area</p>
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
            🔍 Search Pharmacies
          </button>
          <button class="location-button" @click="getLocation">
            📍 Use Current Location
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Finding pharmacies...</p>
      </div>

      <div v-if="error" class="error-state">
        <p>{{ error }}</p>
        <button class="retry-button" @click="getLocation">Try Again</button>
      </div>

      <div v-if="!loading && !error && displayedPharmacies.length === 0 && searchPerformed" class="empty-state">
        <p>No pharmacies found in this area. Try expanding your search radius or different location.</p>
      </div>

      <div v-if="!loading && displayedPharmacies.length > 0" class="pharmacies-list">
        <div class="results-header">
          <h3>Found {{ displayedPharmacies.length }} pharmacy(ies) within {{ searchRadius/1000 }}km</h3>
        </div>

        <div v-for="pharmacy in displayedPharmacies" :key="pharmacy.id" class="pharmacy-card">
          <div class="pharmacy-photo">
            <img src="../assets/PharmacyImage.png" alt="Pharmacy" class="pharmacy-image" />
          </div>
          
          <div class="pharmacy-info">
            <h3 class="pharmacy-name">{{ pharmacy.name }}</h3>
            
            <div class="pharmacy-details">
              <div class="detail-item">
                <span class="detail-label">Rating:</span>
                <span class="rating">{{ formatRating(pharmacy.rating) }}</span>
              </div>
              
              <!-- Update this section to use opening_hours_raw.open_now instead of business_status -->
              <div class="detail-item" v-if="pharmacy.opening_hours_raw">
                <span class="detail-label">Status:</span>
                <span class="status" :class="{ 
                  'open': getOpenStatus(pharmacy.opening_hours_raw).isOpen === true,
                  'closed': getOpenStatus(pharmacy.opening_hours_raw).isOpen === false 
                }">
                  {{ getOpenStatus(pharmacy.opening_hours_raw).status }}
                </span>
              </div>
              
              <!-- Keep business status separate if you want to show it -->
              <div class="detail-item" v-if="pharmacy.business_status && pharmacy.business_status !== 'OPERATIONAL'">
                <span class="detail-label">Business:</span>
                <span class="business-status">
                  {{ pharmacy.business_status }}
                </span>
              </div>
              
              <div class="detail-item" v-if="pharmacy.opening_hours">
                <span class="detail-label">Hours:</span>
                <span class="hours">{{ pharmacy.opening_hours }}</span>
              </div>
              
              <div class="detail-item" v-if="pharmacy.price_level">
                <span class="detail-label">Price Level:</span>
                <span class="price-level">{{ '💰'.repeat(pharmacy.price_level) }}</span>
              </div>
            </div>
            
            <div class="pharmacy-location">
              <span class="location-icon">📍</span> 
              <span>{{ pharmacy.address }}</span>
            </div>
            
            <div class="contact-info" v-if="pharmacy.phone || pharmacy.website">
              <div class="contact-item" v-if="pharmacy.phone">
                <span class="contact-label">📞 Phone:</span>
                <span>{{ pharmacy.phone }}</span>
              </div>
              <div class="contact-item" v-if="pharmacy.website">
                <span class="contact-label">🌐 Website:</span>
                <span class="website-text">{{ pharmacy.website.replace(/^https?:\/\//, '') }}</span>
              </div>
            </div>
            
            <div class="action-buttons">
              <button class="contact-button" @click="contactPharmacy(pharmacy)" v-if="pharmacy.phone">
                📞 Call
              </button>
              <button class="website-button" @click="openWebsite(pharmacy)" v-if="pharmacy.website">
                🌐 Website
              </button>
              <button class="maps-button" @click="openInMaps(pharmacy)" v-if="pharmacy.location.lat">
                🗺️ Directions
              </button>
            </div>
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

.pharmacy-finder-container {
  min-height: 100vh; 
  width: 100%;
  background: linear-gradient(135deg, #e0f7fa, #ffe6f0, #f0f9ff);
  font-family: 'Poppins', sans-serif;
  color: #333;
  padding-top: 0;
}

.dark-mode .pharmacy-finder-container{
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

.location-search {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.search-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 5px;
  margin-left: 2px;
}

.dark-mode .search-label {
  color: #9ca3af;
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

.dark-mode .location-input, .dark-mode .radius-select {
  background-color: #374151; border-color: #4b5563;
  color: #f3f4f6;
}

.location-input:focus, .radius-select:focus {
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

.pharmacies-list {
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

.pharmacy-card {
  display: flex; background-color: white;
  border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.dark-mode .pharmacy-card {
  background-color: #2a2a2a;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.pharmacy-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.pharmacy-photo {
  width: 150px; background-color: #f3f4f6;
  display: flex; align-items: center; justify-content: center;
  padding: 10px;
}

.dark-mode .pharmacy-photo {
  background-color: #374151;
}

.pharmacy-image {
  width: 100px;
  height: 100px;
  object-fit: contain;
  border-radius: 8px;
}

.pharmacy-info {
  flex: 1; padding: 20px;
  display: flex; flex-direction: column; gap: 12px;
}

.pharmacy-name {
  font-size: 1.3rem; font-weight: 600;
  color: #1f2937; margin: 0;
}

.dark-mode .pharmacy-name { color: #f3f4f6; }

.pharmacy-details {
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

.price-level {
  color: #f59e0b;
}

.pharmacy-location {
  display: flex; align-items: flex-start; gap: 8px;
  color: #6b7280; font-size: 0.95rem; line-height: 1.4;
}

.dark-mode .pharmacy-location { color: #9ca3af; }

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

.address-source {
  font-size: 0.8rem;
  color: #10b981;
  font-weight: 500;
  margin-left: 8px;
}

.dark-mode .address-source {
  color: #34d399;
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

.pharmacy-info-modal {
  text-align: center;
  margin-bottom: 20px;
}

.pharmacy-info-modal h4 {
  margin: 0 0 10px 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #1f2937;
}

.dark-mode .pharmacy-info-modal h4 {
  color: #f3f4f6;
}

.pharmacy-address {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.4;
}

.dark-mode .pharmacy-address {
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
  .search-row {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .pharmacy-card {
    flex-direction: column;
  }
  
  .pharmacy-photo {
    width: 100%; height: 80px;
    padding: 15px;
  }
  
  .pharmacy-image {
    width: 50px;
    height: 50px;
  }
  
  .action-buttons {
    flex-direction: row;
  }
}
</style>