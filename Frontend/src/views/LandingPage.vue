<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { auth } from '@/stores/auth';
import axios from 'axios';

const router = useRouter();
const auth_store = auth();

// Dark mode integration using localStorage
const isDarkMode = ref(false);

// Check localStorage for dark mode preference
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

// Data for statistics
const stats = ref({
  users: 0,
  doctors: 0,
  reminders: 0,
  emergencyContacts: 0
});

// Data for testimonials/feedback
const testimonials = ref([
  {
    id: 1,
    name: "Rajesh Kumar",
    age: 72,
    location: "Delhi",
    image: "/testimonials/user1.jpg",
    text: "SHRAVAN has been a lifesaver for me. The medicine reminders help me take my medications on time, and the emergency contact feature gives me peace of mind."
  },
  {
    id: 2,
    name: "Sunita Sharma",
    age: 68,
    location: "Mumbai",
    image: "/testimonials/user2.jpg",
    text: "The yoga videos have helped improve my flexibility. I love how I can filter them based on difficulty level. The interface is so easy to use, even for someone not tech-savvy like me!"
  },
  {
    id: 3,
    name: "Anand Verma",
    age: 75,
    location: "Bangalore",
    image: "/testimonials/user3.jpg",
    text: "The health monitoring features are excellent. I can track my medicine intake and share reports with my doctor. The chatbot feature is also very helpful."
  }
]);

// Features data
const features = ref([
  {
    id: 1,
    title: "Medicine Reminders",
    description: "Never miss a dose with our intelligent reminder system, designed specifically for seniors.",
    icon: "medication",
    animation: "fade-up"
  },
  {
    id: 2,
    title: "Personalised AI Chatbot",
    description: "Get personalized assistance and support for your health needs.",
    icon: "monitor_heart",
    animation: "fade-up"
  },
  {
    id: 3,
    title: "Doctors",
    description: "Quickly reach out to nearby Doctors in your locality.",
    icon: "emergency",
    animation: "fade-up"
  },
  {
    id: 4,
    title: "Yoga & Wellness",
    description: "Access age-appropriate yoga videos and wellness content to stay active and healthy.",
    icon: "self_improvement",
    animation: "fade-up"
  },
  {
    id: 5,
    title: "Pharmacy",
    description: "Locate nearby pharmacies and medical stores with real-time availability information.",
    icon: "local_pharmacy",
    animation: "fade-up"
  },
  {
    id: 6,
    title: "Hospitals",
    description: "Find nearby hospitals, clinics, and healthcare facilities with contact details and directions.",
    icon: "local_hospital",
    animation: "fade-up"
  }
]);

// Animation control
const isAnimated = ref(false);
const animationObserver = ref(null);

// Current testimonial
const currentTestimonialIndex = ref(0);
const testimonialInterval = ref(null);

onMounted(async () => {
  // Initialize dark mode from localStorage
  initializeDarkMode();
  
  // Listen for localStorage changes
  window.addEventListener('storage', handleStorageChange);
  
  // Listen for dark mode changes from the navbar
  window.addEventListener('darkModeChanged', initializeDarkMode);

  // Fetch statistics from the backend
  try {
    const response = await axios.get(`${auth_store.backend_url}/api/stats`);
    stats.value = response.data;
  } catch (error) {
    console.error('Error fetching statistics:', error);
    // Fallback to demo numbers if API fails
    stats.value = {
      users: 1500,
      doctors: 75,
      reminders: 8400,
      emergencyContacts: 3200
    };
  }

  // Set up intersection observer for animations
  animationObserver.value = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animated');
      }
    });
  }, { threshold: 0.1 });

  // Observe all elements with animation classes
  document.querySelectorAll('.animate').forEach(el => {
    animationObserver.value.observe(el);
  });

  // Start testimonial rotation
  startTestimonialRotation();

  // Add scroll event for parallax effect
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  // Clean up
  if (animationObserver.value) {
    animationObserver.value.disconnect();
  }
  
  if (testimonialInterval.value) {
    clearInterval(testimonialInterval.value);
  }
  
  window.removeEventListener('scroll', handleScroll);
  
  // Clean up event listeners
  window.removeEventListener('storage', handleStorageChange);
  window.removeEventListener('darkModeChanged', initializeDarkMode);
});

function startTestimonialRotation() {
  testimonialInterval.value = setInterval(() => {
    currentTestimonialIndex.value = (currentTestimonialIndex.value + 1) % testimonials.value.length;
  }, 5000);
}

function setTestimonial(index) {
  // Clear the automatic rotation interval
  if (testimonialInterval.value) {
    clearInterval(testimonialInterval.value);
  }
  
  // Set the new testimonial
  currentTestimonialIndex.value = index;
  
  // Restart the rotation
  startTestimonialRotation();
}

function handleScroll() {
  const scrollPosition = window.scrollY;
  
  // Parallax effect for hero section
  const heroSection = document.querySelector('.hero-section');
  if (heroSection) {
    heroSection.style.backgroundPositionY = `${scrollPosition * 0.5}px`;
  }
  
  // Animate counter when in view
  const statsSection = document.querySelector('.stats-section');
  if (statsSection && isElementInViewport(statsSection) && !isAnimated.value) {
    animateCounters();
    isAnimated.value = true;
  }
}

function isElementInViewport(el) {
  const rect = el.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
}

function animateCounters() {
  const counters = document.querySelectorAll('.counter');
  const speed = 200;

  counters.forEach(counter => {
    const target = +counter.getAttribute('data-target');
    const count = +counter.innerText;
    const increment = target / speed;

    if (count < target) {
      counter.innerText = Math.ceil(count + increment);
      setTimeout(() => animateCounters(), 1);
    } else {
      counter.innerText = target.toLocaleString();
    }
  });
}

function navigateToLogin() {
  router.push('/userlogin');
}

function navigateToRegister() {
  router.push('/register');
}

function navigateToDownloadApp() {
  router.push('/download-app');
}
</script>

<template>
  <div class="landing-page" :class="{ 'dark-mode': isDarkMode }">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-left">
        <div class="overlay-left"></div>
        <div class="hero-content">
          <div class="logo-container">
            <img src="../assets/Sharvan_logo.jpeg" alt="SHRAVAN Logo" class="logo">
            <h1 class="app-name">SHRAVAN</h1>
          </div>
          <h2 class="hero-tagline">Empowering Seniors for a Healthier, Happier Life</h2>
          <p class="hero-description">
            A comprehensive healthcare companion designed specifically for the elderly, providing medicine reminders, health monitoring, emergency contacts, and more.
          </p>
          <div class="cta-buttons">
            <button @click="navigateToLogin" class="btn btn-transparent">Sign In</button>
            <button @click="navigateToRegister" class="btn btn-transparent">Create Account</button>
            <button @click="navigateToDownloadApp" class="btn btn-mobile-highlight">Get Mobile App</button>
          </div>
        </div>
      </div>
      <div class="hero-right">
        <div class="hero-image-background"></div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="section-header">
        <h2>Our Features</h2>
        <p>SHRAVAN comes with a variety of features tailored for seniors' unique needs</p>
      </div>
      <div class="features-grid">
        <div 
          v-for="feature in features" 
          :key="feature.id" 
          class="feature-card animate"
          :class="feature.animation"
        >
          <div class="feature-icon">
            <span class="material-icons">{{ feature.icon }}</span>
          </div>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section class="about-section">
      <div class="section-header">
        <h2>About SHRAVAN</h2>
        <p>Our mission and vision for elderly healthcare</p>
      </div>
      <div class="about-content">
        <div class="about-image animate fade-right">
          <img src="../assets/about.png" alt="Elderly people using technology">
        </div>
        <div class="about-text animate fade-left">
          <h3>Our Mission</h3>
          <p>
            SHRAVAN is dedicated to empowering seniors with technology that enhances their quality of life, promotes independence, and provides peace of mind to both them and their loved ones.
          </p>
          <h3>Our Vision</h3>
          <p>
            We envision a world where aging is associated with dignity, independence, and continued engagement with life, supported by accessible and intuitive technology solutions.
          </p>
          <h3>Our Approach</h3>
          <p>
            By focusing on simple, intuitive design and essential healthcare features, we've created an application that truly meets the needs of seniors, even those who may not be tech-savvy.
          </p>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="testimonials-section">
      <div class="section-header">
        <h2>What Our Users Say</h2>
        <p>Hear from seniors who have transformed their healthcare experience with SHRAVAN</p>
      </div>
      <div class="testimonials-carousel">
        <div class="testimonial-card animate fade-up">
          <div class="testimonial-content">
            <p>{{ testimonials[currentTestimonialIndex].text }}</p>
          </div>
          <div class="testimonial-author">
            <div class="author-image">
              <img :src="'https://placehold.co/200x200/' + (currentTestimonialIndex === 0 ? '4f46e5' : currentTestimonialIndex === 1 ? 'f97316' : '10b981') + '/FFFFFF/png?text=' + testimonials[currentTestimonialIndex].name.charAt(0)" :alt="testimonials[currentTestimonialIndex].name">
            </div>
            <div class="author-info">
              <h4>{{ testimonials[currentTestimonialIndex].name }}</h4>
              <p>{{ testimonials[currentTestimonialIndex].age }} years, {{ testimonials[currentTestimonialIndex].location }}</p>
            </div>
          </div>
        </div>
        <div class="testimonial-navigation">
          <div 
            v-for="(testimonial, index) in testimonials" 
            :key="testimonial.id"
            class="nav-dot"
            :class="{ active: index === currentTestimonialIndex }"
            @click="setTestimonial(index)"
          ></div>
        </div>
      </div>
    </section>

    <!-- Download App Section -->
    <section class="download-section">
      <div class="download-content animate">
        <h2>Take SHRAVAN with you</h2>
        <p>Download our mobile app for a seamless experience on the go. Get all features in your pocket.</p>
        <div class="app-buttons">
          <button class="app-btn" @click="navigateToDownloadApp">
            <span class="material-icons">android</span>
            <div>
              <small>Get it on</small>
              <strong>Google Play</strong>
            </div>
          </button>
          <button class="app-btn" @click="navigateToDownloadApp">
            <span class="material-icons">qr_code_2</span>
            <div>
              <small>Scan</small>
              <strong>QR Code</strong>
            </div>
          </button>
        </div>
      </div>
      <div class="phone-mockup animate fade-left">
        <img src="../assets/mobile_preview.jpg" alt="SHRAVAN Mobile App">
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-logo">
          <img src="../assets/Sharvan_logo.jpeg" alt="SHRAVAN Logo" class="logo">
          <h3>SHRAVAN</h3>
          <p>Healthcare companion for seniors</p>
        </div>
        <div class="footer-links">
          <div class="footer-column">
            <h4>Features</h4>
            <ul>
              <li>Medicine Reminders</li>
              <li>Health Monitoring</li>
              <li>Emergency Contacts</li>
              <li>Yoga & Wellness</li>
              <li>Pharmacy Finder</li>
              <li>Hospital Finder</li>
            </ul>
          </div>
          <div class="footer-column">
            <h4>Company</h4>
            <ul>
              <li>About Us</li>
              <li>Our Team</li>
              <li>Terms of Service</li>
            </ul>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <div class="footer-bottom-left">
          <p>&copy; 2025 SHRAVAN. All rights reserved.</p>
        </div>
        <div class="footer-bottom-center">
          <div class="footer-contact">
            <h4>Get in Touch</h4>
            <div class="footer-contact-items">
              <div class="footer-contact-item">
                <span class="material-icons">email</span>
                <span>support@shravan.in</span>
              </div>
              <div class="footer-contact-item">
                <span class="material-icons">phone</span>
                <span>+91 1800-SHRAVAN</span>
              </div>
            </div>
          </div>
        </div>
        <div class="footer-bottom-right">
          <div class="social-icons">
            <span class="material-icons">facebook</span>
            <span class="material-icons">twitter</span>
            <span class="material-icons">instagram</span>
            <span class="material-icons">youtube</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Base Styles */
.landing-page {
  font-family: 'Poppins', sans-serif;
  color: #333;
  overflow-x: hidden;
  transition: all 0.3s ease;

}

.landing-page.dark-mode {
  color: #f1f1f1;
  background: linear-gradient(135deg, #0f172a, #1e293b, #0f1419) !important;
}

section {
  padding: 80px 0;
  transition: all 0.3s ease;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-header h2 {
  font-size: 2.5rem;
  margin-bottom: 15px;
  color: #2d3644;
  position: relative;
  display: inline-block;
  transition: color 0.3s ease;
}

.dark-mode .section-header h2 {
  color: #bbd0f0;
}

.section-header h2::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 70px;
  height: 3px;
  background-color: #3b82f6;
  transition: background-color 0.3s ease;
}

.dark-mode .section-header h2::after {
  background-color: #60a5fa;
}

.section-header p {
  font-size: 1.2rem;
  color: #666;
  max-width: 700px;
  margin: 0 auto;
  transition: color 0.3s ease;
}

.dark-mode .section-header p {
  color: #cbd5e1;
}

.btn {
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  font-size: 1rem;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(59, 130, 246, 0.2);
}

.btn-secondary {
  background-color: #10b981;
  color: white;
}

.btn-secondary:hover {
  background-color: #059669;
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(16, 185, 129, 0.2);
}

.btn-transparent {
  background-color: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
}

.btn-transparent:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border: 2px solid white;
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(255, 255, 255, 0.2);
}

.btn-outline {
  background-color: transparent;
  color: #3b82f6;
  border: 2px solid #3b82f6;
}

.btn-outline:hover {
  background-color: #3b82f6;
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(59, 130, 246, 0.2);
}

/* Enhanced Mobile App Button */
.btn-mobile-highlight {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  position: relative;
  overflow: hidden;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
  animation: pulse-glow-green 2s infinite;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.btn-mobile-highlight::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.btn-mobile-highlight:hover::before {
  left: 100%;
}

.btn-mobile-highlight:hover {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5);
}

@keyframes pulse-glow-green {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
  }
  50% {
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.6), 0 0 30px rgba(16, 185, 129, 0.3);
  }
}

/* Animations */
.animate {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease;
}

.animated {
  opacity: 1;
  transform: translateY(0);
}

.fade-right {
  transform: translateX(-30px);
}

.fade-left {
  transform: translateX(30px);
}

.fade-up {
  transform: translateY(30px);
}

/* Hero Section */
.hero-section {
  position: relative;
  min-height: 75vh;
  display: flex;
  padding: 0;
  overflow: hidden;
}

.hero-left {
  position: relative;
  width: 50%;
  background: linear-gradient(135deg, #dbeafe, #eff6ff);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s ease;
}

.dark-mode .hero-left {
  background: linear-gradient(135deg, #1e293b, #0f172a);
}

.overlay-left {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.8), rgba(16, 185, 129, 0.8));
  z-index: 1;
  transition: background 0.3s ease;
}

.dark-mode .overlay-left {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.9), rgba(16, 185, 129, 0.9));
}

.hero-content {
  position: relative;
  z-index: 2;
  color: white;
  max-width: 600px;
  padding: 0 40px;
  width: 100%;
}

.hero-right {
  position: relative;
  width: 50%;
  overflow: hidden;
}

.hero-image-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('../assets/landing.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  filter: drop-shadow(0 20px 30px rgba(0, 0, 0, 0.3));
}

.logo-container {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.logo {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.app-name {
  font-size: 3rem;
  margin: 0 0 0 20px;
  letter-spacing: 1px;
  font-weight: 700;
}

.hero-tagline {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 20px;
}

.hero-description {
  font-size: 1.2rem;
  margin-bottom: 40px;
  line-height: 1.6;
}

.cta-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

/* Features Section */
.features-section {
  background-color: #f8fafc;
  padding: 100px 0;
  transition: background-color 0.3s ease;
}

.dark-mode .features-section {
  background-color: rgb(30, 41, 59);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.feature-card {
  background-color: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  text-align: center;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.dark-mode .feature-card {
  background-color: rgb(30, 41, 59);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  color: #f1f5f9;
}

.feature-card:hover {
  background-color: #f0fdf4;
  border: 2px solid #10b981;
  box-shadow: 0 15px 40px rgba(16, 185, 129, 0.15);
}

.dark-mode .feature-card:hover {
  background-color: rgba(30, 41, 59, 0.8);
  border: 2px solid #34d399;
  box-shadow: 0 15px 40px rgba(52, 211, 153, 0.25);
}

.feature-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #10b981);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.feature-icon .material-icons {
  font-size: 40px;
  color: white;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #333;
  transition: color 0.3s ease;
}

.dark-mode .feature-card h3 {
  color: #f1f5f9;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
  transition: color 0.3s ease;
}

.dark-mode .feature-card p {
  color: #cbd5e1;
}

/* About Section - Enhanced dark mode */
.about-section {
  padding: 100px 0;
  background: linear-gradient(135deg, #3b82f6, #10b981, #059669);
  color: white;
  position: relative;
  overflow: hidden;
  transition: background 0.3s ease;
}

.dark-mode .about-section {
  background: linear-gradient(135deg, #1e40af, #047857, #065f46);
}

.about-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1));
  z-index: 1;
  transition: background 0.3s ease;
}

.dark-mode .about-section::before {
  background: linear-gradient(45deg, rgba(30, 64, 175, 0.2), rgba(4, 120, 87, 0.2));
}

.about-content {
  display: flex;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  gap: 60px;
  position: relative;
  z-index: 2;
}

.about-image {
  flex: 1;
}

.about-image img {
  width: 100%;
  border-radius: 15px;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
  border: 3px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.about-image img:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.about-text {
  flex: 1;
}

.about-text h3 {
  font-size: 1.8rem;
  color: white;
  margin-bottom: 15px;
  margin-top: 30px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  position: relative;
}

.about-text h3::before {
  content: '';
  position: absolute;
  left: -20px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #60a5fa, #34d399);
  border-radius: 2px;
}

.about-text h3:first-child {
  margin-top: 0;
}

.about-text p {
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.8;
  margin-bottom: 20px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  font-size: 1.1rem;
}

/* Testimonials Section */
.testimonials-section {
  background-color: #f8fafc;
  padding: 100px 0;
  transition: background-color 0.3s ease;
}

.dark-mode .testimonials-section {
  background-color: rgb(30, 41, 59);
}

.testimonials-carousel {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.testimonial-card {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.dark-mode .testimonial-card {
  background-color: rgba(30, 41, 59, 0.3);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
}

.testimonial-content {
  text-align: center;
  margin-bottom: 30px;
}

.testimonial-content p {
  font-size: 1.2rem;
  color: #555;
  line-height: 1.8;
  font-style: italic;
  position: relative;
  transition: color 0.3s ease;
}

.dark-mode .testimonial-content p {
  color: #cbd5e1;
}

.testimonial-content p::before,
.testimonial-content p::after {
  content: '"';
  font-size: 2rem;
  color: #3b82f6;
  position: absolute;
  transition: color 0.3s ease;
}

.dark-mode .testimonial-content p::before,
.dark-mode .testimonial-content p::after {
  color: #60a5fa;
}

.testimonial-author {
  display: flex;
  align-items: center;
  justify-content: center;
}

.author-image {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 20px;
  border: 3px solid #3b82f6;
}

.author-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-info h4 {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 5px;
  transition: color 0.3s ease;
}

.dark-mode .author-info h4 {
  color: #f1f5f9;
}

.author-info p {
  color: #666;
  transition: color 0.3s ease;
}

.dark-mode .author-info p {
  color: #94a3b8;
}

.testimonial-navigation {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.nav-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #cbd5e1;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dark-mode .nav-dot {
  background-color: #475569;
}

.nav-dot.active {
  background-color: #3b82f6;
  transform: scale(1.2);
}

.dark-mode .nav-dot.active {
  background-color: #60a5fa;
}

/* Download App Section */
.download-section {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  padding: 100px 0;
  transition: background 0.3s ease;
}

.dark-mode .download-section {
  background: linear-gradient(135deg, #0c4a6e, #164e63);
}

.download-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0 20px;
}

.download-content h2 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 20px;
  transition: color 0.3s ease;
}

.dark-mode .download-content h2 {
  color: #f1f5f9;
}

.download-content p {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 30px;
  max-width: 500px;
  line-height: 1.6;
  transition: color 0.3s ease;
}

.dark-mode .download-content p {
  color: #cbd5e1;
}

.phone-mockup {
  flex: 1;
  display: flex;
  justify-content: center;
}

.phone-mockup img {
  max-height: 600px;
  filter: drop-shadow(0 20px 30px rgba(0, 0, 0, 0.2));
}

.app-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.app-btn {
  display: flex;
  align-items: center;
  color: white;
  border: none;
  padding: 15px 25px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.app-btn:first-child {
  background: linear-gradient(135deg, #3b82f6, #1e40af);
  animation: pulse-glow-blue 2s infinite;
}

.app-btn:last-child {
  background: linear-gradient(135deg, #10b981, #047857);
  animation: pulse-glow-green 2s infinite;
}

.dark-mode .app-btn:first-child {
  background: linear-gradient(135deg, #2563eb, #1e40af);
}

.dark-mode .app-btn:last-child {
  background: linear-gradient(135deg, #059669, #047857);
}

.app-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.app-btn:hover::before {
  left: 100%;
}

.app-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.app-btn:first-child:hover {
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
}

.app-btn:last-child:hover {
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

@keyframes pulse-glow-blue {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
  }
  50% {
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.5), 0 0 30px rgba(59, 130, 246, 0.3);
  }
}

@keyframes pulse-glow-green {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
  }
  50% {
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.5), 0 0 30px rgba(16, 185, 129, 0.3);
  }
}

.app-btn .material-icons {
  font-size: 30px;
  margin-right: 10px;
}

.app-btn div {
  text-align: left;
}

.app-btn small {
  display: block;
  font-size: 0.7rem;
  opacity: 0.8;
}

.app-btn strong {
  font-size: 1rem;
}

/* Footer */
.footer {
  background-color: #1e293b;
  color: white;
  padding: 60px 0 30px;
  transition: background-color 0.3s ease;
}

.dark-mode .footer {
  background-color: #0f172a;
  border-top: 1px solid #334155;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 60px;
  margin-bottom: 50px;
}

.footer-logo {
  flex: 1;
  min-width: 300px;
}

.footer-logo .logo {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  margin-bottom: 15px;
}

.footer-logo h3 {
  font-size: 1.8rem;
  margin-bottom: 10px;
}

.footer-logo p {
  color: rgba(255, 255, 255, 0.7);
}

.footer-links {
  flex: 2;
  display: flex;
  flex-wrap: wrap;
  gap: 40px;
}

.footer-column {
  flex: 1;
  min-width: 150px;
}

.footer-column h4 {
  font-size: 1.2rem;
  margin-bottom: 20px;
  position: relative;
  padding-bottom: 10px;
}

.footer-column h4::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 2px;
  background-color: #3b82f6;
  transition: background-color 0.3s ease;
}

.dark-mode .footer-column h4::after {
  background-color: #60a5fa;
}

.footer-column ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-column li {
  margin-bottom: 10px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: color 0.3s ease;
}

.footer-column li:hover {
  color: #3b82f6;
}

.dark-mode .footer-column li:hover {
  color: #60a5fa;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 30px;
  max-width: 1200px;
  margin: 0 auto;
  padding-left: 20px;
  padding-right: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 30px;
}

.footer-bottom-left {
  flex: 1;
  min-width: 200px;
}

.footer-bottom-left p {
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.footer-bottom-center {
  flex: 2;
  min-width: 300px;
}

.footer-contact h4 {
  color: white;
  font-size: 1.1rem;
  margin-bottom: 15px;
  text-align: center;
}

.footer-contact-items {
  display: flex;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
}

.footer-contact-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.footer-contact-item .material-icons {
  font-size: 18px;
  color: #3b82f6;
}

.footer-bottom-right {
  flex: 1;
  min-width: 200px;
  display: flex;
  justify-content: flex-end;
}

.social-icons {
  display: flex;
  gap: 15px;
}

.social-icons .material-icons {
  font-size: 24px;
  cursor: pointer;
  transition: color 0.3s ease;
  color: rgba(255, 255, 255, 0.7);
}

.social-icons .material-icons:hover {
  color: #3b82f6;
}

.dark-mode .social-icons .material-icons:hover {
  color: #60a5fa;
}

/* Enhanced responsive design for dark mode */
@media (max-width: 992px) {
  .landing-page {
    padding-top: 5rem; /* Adjust for smaller navbar on mobile */
  }
  
  .dark-mode .landing-page {
    padding-top: 5rem;
  }
}

/* Responsive Design */
@media (max-width: 1200px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .hero-content {
    padding: 0 30px;
  }
}

@media (max-width: 992px) {
  .hero-section {
    flex-direction: column;
    min-height: auto;
  }
  
  .hero-left {
    width: 100%;
    min-height: 52.5vh;
  }
  
  .hero-right {
    width: 100%;
    min-height: 30vh;
  }
  
  .hero-content {
    text-align: center;
    padding: 40px 20px;
  }
  
  .logo-container {
    justify-content: center;
  }
  
  .cta-buttons {
    justify-content: center;
  }
  
  .about-content,
  .contact-content {
    flex-direction: column;
    gap: 40px;
  }
  
  .download-section {
    flex-direction: column;
    text-align: center;
  }
  
  .download-content {
    padding: 20px;
    margin-bottom: 50px;
  }
  
  .app-buttons {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header h2 {
    font-size: 2rem;
  }
  
  .hero-tagline {
    font-size: 2rem;
  }
  
  .hero-right {
    min-height: 30vh;
  }
  
  .feature-card {
    padding: 20px;
  }
  
  .stat-card h3 {
    font-size: 2.5rem;
  }
  
  .testimonial-card {
    padding: 30px 20px;
  }
  
  .footer-content {
    gap: 40px;
  }
}

@media (max-width: 576px) {
  .hero-tagline {
    font-size: 1.8rem;
  }
  
  .hero-description {
    font-size: 1rem;
  }
  
  .cta-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .btn {
    width: 100%;
  }
  
  .app-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .app-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>