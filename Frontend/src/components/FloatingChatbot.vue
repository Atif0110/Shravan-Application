<template>
  <div class="floating-chatbot" :class="{ 'expanded': isOpen, 'dark-mode': isDarkMode }">
    <!-- Chatbot button (visible when chat is closed) -->
    <button 
      v-if="!isOpen" 
      @click="openChat" 
      class="chat-button"
      :aria-label="'Open chat assistant'"
    >
      <img src="../assets/Sharvan_logo.jpeg" alt="SHRAVAN" class="chat-button-logo" />
      <span>Ask SHRAVAN</span>
    </button>

    <!-- Chatbot container (visible when open) -->
    <div v-if="isOpen" class="chat-container" :class="{ 'expanded-view': isExpanded }">
      <!-- Chat header -->
      <div class="chat-header">
        <div class="chat-info">
          <img src="../assets/Sharvan_logo.jpeg" alt="SHRAVAN" class="chat-avatar" />
          <div>
            <h3>SHRAVAN</h3>
            <p>Your health assistant</p>
          </div>
        </div>
        <div class="header-controls">
          <button 
            @click="toggleExpanded" 
            class="expand-button" 
            :title="isExpanded ? 'Minimize chat' : 'Expand chat'"
          >
            <span class="material-icons">{{ isExpanded ? 'fullscreen_exit' : 'fullscreen' }}</span>
          </button>
          <button 
            @click="clearChatHistory" 
            class="clear-button" 
            title="Clear chat history"
          >
            <span class="material-icons">refresh</span>
          </button>
          <button @click="closeChat" class="close-button" title="Close chat">
            <span class="material-icons">close</span>
          </button>
        </div>
      </div>

      <!-- Chat messages -->
      <div class="chat-messages" ref="messagesContainer">
        <!-- <div v-if="messages.length === 0" class="empty-chat">
          <span class="material-icons">forum</span>
          <p>Ask me anything about your health, medications, or care!</p>
          <div class="suggested-prompts">
            <button 
              v-for="prompt in suggestedPrompts" 
              :key="prompt"
              @click="sendSuggestedMessage(prompt)"
              class="suggested-prompt"
            >
              {{ prompt }}
            </button>
          </div>
        </div> -->
        
        <div v-for="(msg, index) in messages" :key="index" 
             :class="['message-bubble', msg.sender]">
          <div class="message-content">
            <div v-if="msg.sender === 'bot'" 
                 class="markdown-content" 
                 v-html="parseMarkdown(msg.text)">
            </div>
            <p v-else>{{ msg.text }}</p>
            <span class="message-time">{{ msg.time }}</span>
          </div>
        </div>

        <!-- Typing indicator -->
        <div v-if="isProcessing" class="message-bubble bot typing-indicator">
          <div class="message-content">
            <div class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat input -->
      <div class="chat-input">
        <form @submit.prevent="sendMessage" class="input-form">
          <input
            v-model="userInput"
            type="text"
            placeholder="Type your message..."
            :disabled="isProcessing"
            @keydown.enter.prevent="sendMessage"
            ref="inputField"
          />
          <button 
            type="button" 
            @click="startListening" 
            :disabled="!supportsSpeech || isProcessing"
            class="voice-btn"
            :class="{ 'listening': isListening }"
          >
            <span class="material-icons">{{ isListening ? 'mic' : 'mic_none' }}</span>
          </button>
          <button 
            type="button" 
            class="send-btn"
            :disabled="!userInput.trim() || isProcessing"
            @click="sendMessage"
          >
            <span class="material-icons">send</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, computed } from 'vue';
import axios from 'axios';
import { auth } from '../stores/auth';
import { useChatbotStore } from '../stores/chatbotStore';

interface Message {
  text: string;
  sender: 'user' | 'bot';
  time: string;
}

interface ChatHistory {
  user: string;
  assistant: string;
}

const authStore = auth();
const chatbotStore = useChatbotStore();
const isOpen = ref(false);
const userInput = ref('');
const supportsSpeech = ref(false);
const isListening = ref(false);
const isProcessing = ref(false);
const messagesContainer = ref<HTMLElement | null>(null);
const isDarkMode = ref(false); // Dark mode integration
const isExpanded = ref(false);
const inputField = ref<HTMLElement | null>(null);

// Suggested prompts for better UX
const suggestedPrompts = ref([
  "What are common symptoms of diabetes?",
  "How to manage high blood pressure?",
  "Tell me about healthy diet tips",
  "What medications help with anxiety?"
]);

// Use the messages from the store instead of local state
const messages = computed(() => chatbotStore.messages);
// Use the chatHistory from the store
const chatHistory = computed({
  get: () => chatbotStore.chatHistory,
  set: (newVal) => chatbotStore.updateChatHistory(newVal)
});

let recognition: any = null;

// Open the chat widget
const openChat = () => {
  isOpen.value = true;
  nextTick(() => {
    scrollToBottom();
    if (inputField.value) {
      (inputField.value as HTMLInputElement).focus();
    }
  });
};

// Close the chat widget
const closeChat = () => {
  isOpen.value = false;
  isExpanded.value = false; // Reset expanded state when closing
};

onMounted(() => {
  // Initialize with a welcome message only when first opened
  if (messages.value.length === 0) {
    chatbotStore.addMessage({ 
      text: "Hello! I'm SHRAVAN, your health assistant. How can I help you today?", 
      sender: 'bot',
      time: getCurrentTime()
    });
  }
  
  // Initialize speech recognition
  const SpeechRecognitionClass =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
  if (SpeechRecognitionClass) {
    supportsSpeech.value = true;
    recognition = new SpeechRecognitionClass();
    recognition.lang = 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      isListening.value = true;
    };

    recognition.onend = () => {
      isListening.value = false;
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      userInput.value = transcript;
      sendMessage();
    };
    
    recognition.onerror = () => {
      isListening.value = false;
    };
  }

  // Initialize dark mode from localStorage
  initializeDarkMode();
  
  // Listen for localStorage changes
  window.addEventListener('storage', handleStorageChange);
  
  // Listen for dark mode changes from the navbar
  window.addEventListener('darkModeChanged', initializeDarkMode);
});

// Watch for new messages and scroll to bottom
watch(messages, () => {
  nextTick(() => {
    scrollToBottom();
  });
});

// Get current time for message timestamp
const getCurrentTime = () => {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

//Parse html with proper color classes
const parseMarkdown = (text: string): string => {
  if (!text) return '';
  
  // Split by lines to handle line-by-line processing
  let lines = text.split('\n');
  let html = '';
  let inList = false;
  let listItems: string[] = [];
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trim();
    
    // Handle headers with explicit color styling
    if (line.startsWith('### ')) {
      if (inList) {
        html += '<ul class="markdown-list">' + listItems.map(item => `<li class="markdown-item">${item}</li>`).join('') + '</ul>';
        listItems = [];
        inList = false;
      }
      html += `<h3 class="markdown-header">${line.substring(4)}</h3>`;
    } else if (line.startsWith('## ')) {
      if (inList) {
        html += '<ul class="markdown-list">' + listItems.map(item => `<li class="markdown-item">${item}</li>`).join('') + '</ul>';
        listItems = [];
        inList = false;
      }
      html += `<h2 class="markdown-header">${line.substring(3)}</h2>`;
    } else if (line.startsWith('# ')) {
      if (inList) {
        html += '<ul class="markdown-list">' + listItems.map(item => `<li class="markdown-item">${item}</li>`).join('') + '</ul>';
        listItems = [];
        inList = false;
      }
      html += `<h1 class="markdown-header">${line.substring(2)}</h1>`;
    }
    // Handle bullet points with color classes
    else if (line.startsWith('- ') || line.startsWith('* ')) {
      let itemText = line.substring(2);
      // Process bold and italic with color classes
      itemText = itemText.replace(/\*\*(.*?)\*\*/g, '<strong class="markdown-bold">$1</strong>');
      itemText = itemText.replace(/\*(.*?)\*/g, '<em class="markdown-italic">$1</em>');
      listItems.push(itemText);
      inList = true;
    }
    // Handle numbered lists with color classes
    else if (/^\d+\.\s/.test(line)) {
      let itemText = line.replace(/^\d+\.\s/, '');
      // Process bold and italic with color classes
      itemText = itemText.replace(/\*\*(.*?)\*\*/g, '<strong class="markdown-bold">$1</strong>');
      itemText = itemText.replace(/\*(.*?)\*/g, '<em class="markdown-italic">$1</em>');
      listItems.push(itemText);
      inList = true;
    }
    // Handle regular paragraphs with color classes
    else if (line.length > 0) {
      if (inList) {
        html += '<ul class="markdown-list">' + listItems.map(item => `<li class="markdown-item">${item}</li>`).join('') + '</ul>';
        listItems = [];
        inList = false;
      }
      
      // Process bold and italic with color classes
      line = line.replace(/\*\*(.*?)\*\*/g, '<strong class="markdown-bold">$1</strong>');
      line = line.replace(/\*(.*?)\*/g, '<em class="markdown-italic">$1</em>');
      
      // Process inline code with color classes
      line = line.replace(/`(.*?)`/g, '<code class="markdown-code">$1</code>');
      
      html += `<p class="markdown-paragraph">${line}</p>`;
    }
    // Handle empty lines
    else {
      if (inList) {
        html += '<ul class="markdown-list">' + listItems.map(item => `<li class="markdown-item">${item}</li>`).join('') + '</ul>';
        listItems = [];
        inList = false;
      }
      if (html && !html.endsWith('</h1>') && !html.endsWith('</h2>') && !html.endsWith('</h3>') && !html.endsWith('</ul>')) {
        html += '<br class="markdown-break">';
      }
    }
  }
  
  // Close any remaining list with color classes
  if (inList) {
    html += '<ul class="markdown-list">' + listItems.map(item => `<li class="markdown-item">${item}</li>`).join('') + '</ul>';
  }
  
  // Handle code blocks with color classes (after line processing)
  html = html.replace(/```([\s\S]*?)```/g, '<pre class="markdown-pre"><code class="markdown-code-block">$1</code></pre>');
  
  return html;
};

// Send message to backend
const sendMessage = async () => {
  if (!userInput.value?.trim() || isProcessing.value) {
    return;
  }

  const messageText = userInput.value;
  userInput.value = '';
  isProcessing.value = true;

  // Add user message
  chatbotStore.addMessage({
    text: messageText,
    sender: 'user',
    time: getCurrentTime()
  });

  try {
    // Prepare the request payload
    const payload = {
      question: messageText,
      history: chatHistory.value
    };
    
    // Make API call to backend
    const response = await axios.post(`${authStore.backend_url}/api/chatbot`, payload, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (response.status === 200 && response.data.response) {
      const botResponse = response.data.response;
      
      // Add bot message
      chatbotStore.addMessage({
        text: botResponse,
        sender: 'bot',
        time: getCurrentTime()
      });

      // Update chat history for the current session
      chatbotStore.updateChatHistory({
        user: messageText,
        assistant: botResponse
      });
    } else {
      throw new Error('Invalid response from server');
    }

    isProcessing.value = false;
  } catch (error) {
    console.error('Error sending message:', error);
    
    let errorMessage = "Sorry, I couldn't process your request. Please try again.";
    
    // Handle specific error cases
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 400) {
        errorMessage = "Please enter a valid question.";
      } else if (error.response?.status === 404) {
        errorMessage = "API endpoint not found. Please check if the backend is running.";
      } else if (error.response?.status === 500) {
        errorMessage = "Server error occurred. Please try again later.";
      } else if (!error.response) {
        errorMessage = "Network error. Please check your connection.";
      }
    }

    chatbotStore.addMessage({
      text: errorMessage,
      sender: 'bot',
      time: getCurrentTime()
    });
    
    isProcessing.value = false;
  }
};

// Trigger voice input
const startListening = () => {
  if (recognition && !isListening.value) {
    recognition.start();
  } else if (recognition && isListening.value) {
    recognition.stop();
  }
};

// Scroll to the bottom of the chat
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// Toggle expanded view
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value;
  nextTick(() => {
    scrollToBottom();
    // Focus input field after expanding/minimizing
    if (inputField.value) {
      (inputField.value as HTMLInputElement).focus();
    }
  });
};

// Send suggested message
const sendSuggestedMessage = (prompt: string) => {
  userInput.value = prompt;
  sendMessage();
};

// Enhanced clear chat history
const clearChatHistory = () => {
  chatbotStore.clearChat();
  // Add welcome message after clearing
  setTimeout(() => {
    chatbotStore.addMessage({ 
      text: "Hello! I'm SHRAVAN, your health assistant. How can I help you today?", 
      sender: 'bot',
      time: getCurrentTime()
    });
  }, 100);
};

// Dark mode integration functions
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

function handleStorageChange(e) {
  if (e.key === 'darkModePreference') {
    initializeDarkMode();
  }
}
</script>

<style scoped>
.floating-chatbot {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
  font-family: 'Poppins', sans-serif;
  transition: all 0.3s ease;
}

.expanded {
  transform: scale(1);
  opacity: 1;
}

/* Chat button style - matching landing page theme */
.chat-button {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: linear-gradient(135deg, #3b82f6, #10b981);
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
  transition: all 0.3s ease;
  animation: pulse-glow-blue 2s infinite;
  font-weight: 600;
  position: relative;
  overflow: hidden;
}

.chat-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.chat-button:hover::before {
  left: 100%;
}

.chat-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
  background: linear-gradient(135deg, #2563eb, #059669);
}

@keyframes pulse-glow-blue {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
  }
  50% {
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.6), 0 0 30px rgba(59, 130, 246, 0.3);
  }
}

.chat-button-logo {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 10px;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.chat-button span {
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* Chat container style - matching landing page */
.chat-container {
  width: 350px;
  height: 500px;
  background-color: white;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.chat-container.expanded-view {
  width: 500px;
  height: 700px;
  max-height: 85vh;
  max-width: 90vw;
}

.dark-mode .chat-container {
  background-color: rgb(30, 41, 59);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: linear-gradient(135deg, #3b82f6, #10b981);
  color: white;
  transition: background 0.3s ease;
  min-height: 70px;
}

.header-controls {
  display: flex;
  gap: 6px;
  align-items: center;
}

.expand-button, .clear-button {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
  width: 32px;
  height: 32px;
  position: relative;
}

.expand-button:hover, .clear-button:hover, .close-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.expand-button .material-icons, .clear-button .material-icons {
  font-size: 18px;
}

/* Tooltip effect for buttons */
.expand-button::after, .clear-button::after, .close-button::after {
  content: attr(title);
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
  z-index: 1001;
}

.expand-button:hover::after, .clear-button:hover::after, .close-button:hover::after {
  opacity: 1;
}

.chat-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.chat-info h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.chat-info p {
  margin: 0;
  font-size: 0.8rem;
  opacity: 0.9;
}

.close-button {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.close-button .material-icons {
  font-size: 20px;
}

/* Chat messages area - matching landing page theme */
.chat-messages {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  background-color: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: background-color 0.3s ease;
  color: #000000;
}

.dark-mode .chat-messages {
  background-color: rgb(30, 41, 59);
  color: #ffffff;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #000000;
  text-align: center;
  padding: 20px;
  transition: color 0.3s ease;
}

.dark-mode .empty-chat {
  color: #cbd5e1;
}

.empty-chat .material-icons {
  font-size: 48px;
  margin-bottom: 10px;
  opacity: 0.5;
  color: #3b82f6;
  transition: color 0.3s ease;
}

.dark-mode .empty-chat .material-icons {
  color: #60a5fa;
}

.message-bubble {
  max-width: 75%;
  padding: 10px 15px;
  border-radius: 18px;
  position: relative;
  animation: fadeIn 0.3s ease-out;
  word-wrap: break-word;
  transition: all 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-bubble.user {
  align-self: flex-end;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.message-bubble.bot {
  align-self: flex-start;
  background-color: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.dark-mode .message-bubble.bot {
  background-color: rgb(30, 41, 59);
  color: #f1f5f9;
  border: 1px solid #475569;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.message-content {
  display: flex;
  flex-direction: column;
}

.message-content p {
  margin: 0;
  line-height: 1.5;
  font-weight: 500;
}

.message-time {
  font-size: 0.7rem;
  margin-top: 4px;
  opacity: 0.7;
  align-self: flex-end;
}

/* Chat input area - matching landing page */
.chat-input {
  padding: 15px;
  border-top: 1px solid #e5e7eb;
  background-color: white;
  transition: all 0.3s ease;
}

.dark-mode .chat-input {
  background-color: rgb(30, 41, 59);
  border-top: 1px solid #475569;
}

.input-form {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #f8fafc;
  border-radius: 24px;
  padding: 5px 10px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.dark-mode .input-form {
  background-color: rgb(30, 41, 59);
  border: 1px solid #475569;
}

.input-form input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 10px;
  font-size: 0.95rem;
  color: #333;
  transition: color 0.3s ease;
}

.dark-mode .input-form input {
  color: #f1f5f9;
}

.input-form input::placeholder {
  color: #666;
  transition: color 0.3s ease;
}

.dark-mode .input-form input::placeholder {
  color: #94a3b8;
}

.voice-btn, .send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.voice-btn {
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.voice-btn:hover {
  background-color: rgba(59, 130, 246, 0.2);
  transform: scale(1.1);
}

.dark-mode .voice-btn {
  background-color: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
}

.dark-mode .voice-btn:hover {
  background-color: rgba(96, 165, 250, 0.3);
}

.voice-btn.listening {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.send-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.send-btn:hover {
  background: linear-gradient(135deg, #059669, #047857);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.dark-mode .send-btn {
  background: linear-gradient(135deg, #34d399, #10b981);
}

.dark-mode .send-btn:hover {
  background: linear-gradient(135deg, #10b981, #059669);
}

.voice-btn:disabled, .send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Enhanced markdown content styling with explicit color overrides */
.markdown-content {
  line-height: 1.6;
  color: #333 !important;
}

.dark-mode .markdown-content {
  color: #f1f5f9 !important;
}

/* Markdown elements with explicit colors */
.markdown-content .markdown-header,
.markdown-content h1, 
.markdown-content h2, 
.markdown-content h3 {
  margin: 10px 0 5px 0;
  color: #1f2937 !important;
  font-weight: 600;
}

.dark-mode .markdown-content .markdown-header,
.dark-mode .markdown-content h1,
.dark-mode .markdown-content h2,
.dark-mode .markdown-content h3 {
  color: #f9fafb !important;
}

.markdown-content h1 { font-size: 1.2em; }
.markdown-content h2 { font-size: 1.1em; }
.markdown-content h3 { font-size: 1.05em; }

.markdown-content .markdown-paragraph,
.markdown-content p {
  margin: 6px 0;
  color: #374151 !important;
}

.dark-mode .markdown-content .markdown-paragraph,
.dark-mode .markdown-content p {
  color: #e5e7eb !important;
}

.markdown-content .markdown-list,
.markdown-content ul {
  margin: 8px 0;
  padding-left: 20px;
  color: #374151 !important;
}

.dark-mode .markdown-content .markdown-list,
.dark-mode .markdown-content ul {
  color: #e5e7eb !important;
}

.markdown-content .markdown-item,
.markdown-content li {
  margin: 4px 0;
  color: #374151 !important;
}

.dark-mode .markdown-content .markdown-item,
.dark-mode .markdown-content li {
  color: #e5e7eb !important;
}

.markdown-content .markdown-bold,
.markdown-content strong {
  font-weight: 700;
  color: #1f2937 !important;
}

.dark-mode .markdown-content .markdown-bold,
.dark-mode .markdown-content strong {
  color: #f3f4f6 !important;
}

.markdown-content .markdown-italic,
.markdown-content em {
  font-style: italic;
  color: #374151 !important;
}

.dark-mode .markdown-content .markdown-italic,
.dark-mode .markdown-content em {
  color: #d1d5db !important;
}

.markdown-content .markdown-code,
.markdown-content code {
  background: rgba(59, 130, 246, 0.1) !important;
  color: #1e40af !important;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.9em;
}

.dark-mode .markdown-content .markdown-code,
.dark-mode .markdown-content code {
  background: rgba(96, 165, 250, 0.2) !important;
  color: #93c5fd !important;
}

.markdown-content .markdown-pre,
.markdown-content pre {
  background: rgba(0, 0, 0, 0.05) !important;
  color: #1f2937 !important;
  padding: 10px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.dark-mode .markdown-content .markdown-pre,
.dark-mode .markdown-content pre {
  background: rgba(255, 255, 255, 0.05) !important;
  color: #f3f4f6 !important;
}

.markdown-content .markdown-code-block,
.markdown-content pre code {
  background: none !important;
  color: inherit !important;
  padding: 0;
}

/* Message bubble specific overrides */
.message-bubble.bot .markdown-content,
.message-bubble.bot .markdown-content * {
  color: #333 !important;
}

.dark-mode .message-bubble.bot .markdown-content,
.dark-mode .message-bubble.bot .markdown-content * {
  color: #f1f5f9 !important;
}

/* Override any default styles */
.markdown-content * {
  color: inherit !important;
}
</style>