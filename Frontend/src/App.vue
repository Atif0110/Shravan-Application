<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { messageStore } from './stores/messageStore';
import FloatingChatbot from './components/FloatingChatbot.vue';
import Navbar from './components/Navbar.vue';
import { onMounted, watch } from 'vue';

const message_store = messageStore();

// Auto-hide flash message after 3 seconds
onMounted(() => {
  if (message_store.flash_message) {
    setTimeout(() => {
      message_store.clearMessage();
    }, 3000);
  }
});

// Watch for new flash messages and auto-hide them
watch(() => message_store.flash_message, (newMessage) => {
  if (newMessage) {
    setTimeout(() => {
      message_store.clearMessage();
    }, 3000);
  }
});
</script>

<template>
  <div id="app">
    <!-- Flash Message -->
    <div v-if="message_store.flash_message" class="flash-message">
      <div class="flash-content">
        <span class="flash-icon">✓</span>
        <p>{{ message_store.flash_message }}</p>
      </div>
    </div>
    
    <!-- Navbar - shown on all pages -->
    <Navbar />
    
    <!-- Main Content -->
    <main class="main-content">
      <RouterView />
    </main>
    
    <!-- Floating Chatbot -->
    <FloatingChatbot />
  </div>
</template>

<style>
/* Import Base Theme */
@import './components/BaseTheme.css';

/* App Specific Styles */
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #10b981, #3b82f6, #06b6d4);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
}

/* Flash Message Styles - Enhanced with Landing Page theme */
.flash-message {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1001;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.flash-content {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  padding: 16px 24px;
  border-radius: 15px;
  box-shadow: 0 15px 30px rgba(16, 185, 129, 0.3);
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 400px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.flash-icon {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.flash-content p {
  margin: 0;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 1rem;
  color: white;
}

/* Main Content Styles */
.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  /* min-height: calc(100vh - 70px); */
  background: transparent;
}

/* Dark Mode Global Styles - Enhanced */
:global(.dark-mode) {
  background: linear-gradient(135deg, #1a2435, #2d2d3a, #1a1f2c) !important;
  color: #e2e8f0 !important;
}

:global(.dark-mode) #app {
  background: linear-gradient(135deg, #1a2435, #2d2d3a, #1a1f2c);
}

:global(.dark-mode) .flash-content {
  background: linear-gradient(135deg, #059669, #047857);
  box-shadow: 0 15px 30px rgba(5, 150, 105, 0.4);
  border-color: rgba(255, 255, 255, 0.1);
}

:global(.dark-mode) h1,
:global(.dark-mode) h2,
:global(.dark-mode) h3,
:global(.dark-mode) h4,
:global(.dark-mode) h5,
:global(.dark-mode) h6 {
  color: #f7fafc;
}

:global(.dark-mode) p {
  color: #cbd5e0;
}

/* Smooth Transitions */
* {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

/* Enhanced Focus States */
*:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #3b82f6, #10b981);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #2563eb, #059669);
}

:global(.dark-mode) ::-webkit-scrollbar-track {
  background: #374151;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .main-content {
    min-height: calc(100vh - 60px);
  }

  .flash-content {
    min-width: 320px;
    padding: 14px 20px;
    font-size: 0.9rem;
  }

  .flash-message {
    left: 10px;
    right: 10px;
    transform: none;
    width: calc(100% - 20px);
  }

  .flash-content {
    min-width: auto;
    width: 100%;
  }
}

@media (max-width: 480px) {
  .flash-content {
    padding: 12px 16px;
    font-size: 0.85rem;
  }

  .flash-icon {
    width: 20px;
    height: 20px;
    font-size: 12px;
  }
}

/* Override any default margins/paddings that might conflict */
.main-content > * {
  margin: 0;
  padding: 0;
}

/* Enhanced Button Hover Effects */
.btn:hover {
  transform: translateY(-2px);
}

.btn:active {
  transform: translateY(0);
}

/* Enhanced Card Shadows */
.card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card:hover {
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);
}

/* Loading States */
.loading {
  opacity: 0.7;
  pointer-events: none;
}

/* High Contrast Mode Support */
@media (prefers-contrast: high) {
  .btn {
    border: 2px solid currentColor;
  }
  
  .card {
    border: 2px solid var(--gray-300);
  }
}

/* Reduced Motion Support */
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
    animation: none !important;
  }
}
</style>