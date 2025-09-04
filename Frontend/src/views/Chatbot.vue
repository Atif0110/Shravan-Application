<template>
  <div class="chatbot-page" :class="{ 'dark-mode': isDarkMode }">
    <div class="chatbot-container">
      <div class="chat-header">
        <div class="chat-info">
          <img src="../assets/Sharvan_logo.jpeg" alt="SHRAVAN" class="chat-avatar" />
          <div>
            <h2>SHRAVAN</h2>
            <p>Your health assistant</p>
          </div>
        </div>
        <div class="header-controls">
          <button 
            @click="clearChatHistory" 
            class="clear-button" 
            title="Clear chat history"
          >
            <span class="material-icons">refresh</span>
          </button>
        </div>
      </div>

      <div class="chat-messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-chat">
        </div>
        
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
            :title="isListening ? 'Stop recording' : 'Voice input'"
          >
            <span class="material-icons">{{ isListening ? 'mic' : 'mic_none' }}</span>
          </button>
          <button 
            type="button" 
            class="send-btn"
            :disabled="!userInput.trim() || isProcessing"
            @click="sendMessage"
            title="Send message"
          >
            <span class="material-icons">send</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { auth } from '../stores/auth';

interface Message {
  text: string;
  sender: 'user' | 'bot';
  time: string;
}

interface ChatHistory {
  user: string;
  assistant: string;
}

const router = useRouter();
const authStore = auth();
const messages = ref<Message[]>([]);
const userInput = ref('');
const supportsSpeech = ref(false);
const isListening = ref(false);
const isProcessing = ref(false);
const messagesContainer = ref<HTMLElement | null>(null);
const isDarkMode = ref(localStorage.getItem('darkModePreference') === 'dark');
const chatHistory = ref<ChatHistory>({ user: '', assistant: '' });
//const darkMode = ref(localStorage.getItem('darkMode') === 'true');

let recognition: any = null;

onMounted(() => {
  
  // Reset chat history for new session
  chatHistory.value = { user: '', assistant: '' };
  
  // Initialize with a welcome message
  messages.value.push({ 
    text: "Hello! I'm SHARVAN, your health assistant. How can I help you today?", 
    sender: 'bot',
    time: getCurrentTime()
  });



  scrollToBottom();
  

  document.body.classList.toggle('dark-mode', isDarkMode.value);
  

  // Scroll to bottom of messages
  scrollToBottom();
  
  // Check for dark mode preference
  document.body.classList.toggle('dark-mode', isDarkMode.value);
  
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



// Send message to backend
const sendMessage = async () => {
  console.log("=== SEND MESSAGE FUNCTION CALLED ===");
  console.log("User input:", userInput.value);
  console.log("User input trimmed:", userInput.value?.trim());
  console.log("Is processing:", isProcessing.value);
  
  if (!userInput.value?.trim() || isProcessing.value) {
    console.log("Early return - empty input or processing");
    return;
  }

  const messageText = userInput.value;
  console.log("Message text:", messageText);
  userInput.value = '';
  isProcessing.value = true;

  // Add user message
  messages.value.push({
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
    console.log('Sending payload:', payload);
    console.log('Backend URL:', authStore.backend_url);
    
    // Make API call to backend
    const response = await axios.post(`${authStore.backend_url}/api/chatbot`, payload, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log('Response received:', response);

    if (response.status === 200 && response.data.response) {
      const botResponse = response.data.response;
      
      // Add bot message
      messages.value.push({
        text: botResponse,
        sender: 'bot',
        time: getCurrentTime()
      });

      // Update chat history for the current session
      chatHistory.value = {
        user: messageText,
        assistant: botResponse
      };
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

    messages.value.push({
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

// Clear chat history for new conversation
const clearChatHistory = () => {
  messages.value = [];
  chatHistory.value = { user: '', assistant: '' };
  // Add welcome message after clearing
  setTimeout(() => {
    messages.value.push({ 
      text: "Hello! I'm SHRAVAN, your health assistant. How can I help you today?", 
      sender: 'bot',
      time: getCurrentTime()
    });
  }, 100);
};

// Parse markdown to HTML with proper color inheritance
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

// Test function for debugging (kept for potential future debugging)
const testFunction = () => {
  console.log("=== TEST FUNCTION CALLED ===");
  console.log("Auth store available:", !!authStore);
  console.log("Backend URL:", authStore?.backend_url);
  console.log("User input:", userInput.value);
  console.log("Messages:", messages.value);
  
  // Test the sendMessage function
  if (userInput.value?.trim()) {
    console.log("Calling sendMessage directly...");
    sendMessage();
  } else {
    console.log("No user input to test");
  }
};

// Remove goBack function since navigation is handled by global navbar
</script>

<style scoped>
.chatbot-page {
  display: flex;
  flex-direction: column;
  min-height: 90vh;
  background-color: #f8fafc;
  padding: 20px;
  font-family: 'Poppins', sans-serif;
  transition: all 0.3s ease;
}

.dark-mode .chatbot-page {
  background-color: rgb(15, 23, 42);
}

.chatbot-container {
  display: flex;
  flex-direction: column;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  flex: 1;
  border-radius: 15px;
  background-color: white;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
  transition: all 0.3s ease;
}

.dark-mode .chatbot-container {
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
  padding: 20px;
  background: linear-gradient(135deg, #3b82f6, #10b981);
  color: white;
  transition: background 0.3s ease;
  min-height: 80px;
}

.dark-mode .chat-header {
  background: linear-gradient(135deg, #1e40af, #047857);
}

.chat-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.chat-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.chat-info h2 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.chat-info p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.9;
}

.header-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.clear-button {
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
  width: 36px;
  height: 36px;
}

.clear-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.clear-button .material-icons {
  font-size: 20px;
}

.chat-messages {
  color: #000000;
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: background-color 0.3s ease;
  min-height: 400px;
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
  padding: 40px 20px;
  transition: color 0.3s ease;
}

.dark-mode .empty-chat {
  color: #cbd5e1;
}

.empty-chat .material-icons {
  font-size: 56px;
  margin-bottom: 15px;
  opacity: 0.5;
  color: #3b82f6;
  transition: color 0.3s ease;
}

.dark-mode .empty-chat .material-icons {
  color: #60a5fa;
}

.suggested-prompts {
  margin-top: 25px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  max-width: 400px;
}

.suggested-prompt {
  padding: 12px 20px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 25px;
  color: #3b82f6;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  text-align: left;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
}

.suggested-prompt:hover {
  background: rgba(59, 130, 246, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.dark-mode .suggested-prompt {
  background: rgba(96, 165, 250, 0.2);
  border: 1px solid rgba(96, 165, 250, 0.3);
  color: #60a5fa;
}

.dark-mode .suggested-prompt:hover {
  background: rgba(96, 165, 250, 0.3);
}

.message-bubble {
  max-width: 80%;
  padding: 12px 18px;
  border-radius: 20px;
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
  border-bottom-right-radius: 6px;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.message-bubble.bot {
  align-self: flex-start;
  background-color: white;
  color: #333;
  border-bottom-left-radius: 6px;
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
  line-height: 1.6;
  font-weight: 500;
}

.message-time {
  font-size: 0.75rem;
  margin-top: 6px;
  opacity: 0.7;
  align-self: flex-end;
}

.chat-input {
  padding: 20px;
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
  gap: 10px;
  background-color: #f8fafc;
  border-radius: 30px;
  padding: 6px 15px;
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
  padding: 12px;
  font-size: 1rem;
  color: #333;
  transition: color 0.3s ease;
  font-family: 'Poppins', sans-serif;
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
  width: 40px;
  height: 40px;
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

/* Typing indicator */
.typing-indicator {
  align-self: flex-start;
  background-color: white;
  border: 1px solid #e5e7eb;
  animation: fadeIn 0.3s ease-out;
}

.dark-mode .typing-indicator {
  background-color: rgb(30, 41, 59);
  border: 1px solid #475569;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 5px 0;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  30% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* Enhanced markdown content styling */
.markdown-content {
  line-height: 1.7;
  color: #333 !important;
}

.dark-mode .markdown-content {
  color: #f1f5f9 !important;
}

/* Markdown headers with explicit colors */
.markdown-content .markdown-header,
.markdown-content h1, 
.markdown-content h2, 
.markdown-content h3 {
  margin: 12px 0 6px 0;
  color: #1f2937 !important;
  font-weight: 600;
}

.dark-mode .markdown-content .markdown-header,
.dark-mode .markdown-content h1,
.dark-mode .markdown-content h2,
.dark-mode .markdown-content h3 {
  color: #f9fafb !important;
}

.markdown-content h1,
.markdown-content .markdown-header:first-child { 
  font-size: 1.3em; 
}

.markdown-content h2 { 
  font-size: 1.2em; 
}

.markdown-content h3 { 
  font-size: 1.1em; 
}

/* Markdown paragraphs with explicit colors */
.markdown-content .markdown-paragraph,
.markdown-content p {
  margin: 8px 0;
  color: #374151 !important;
  line-height: 1.6;
}

.dark-mode .markdown-content .markdown-paragraph,
.dark-mode .markdown-content p {
  color: #e5e7eb !important;
}

/* Markdown lists with explicit colors */
.markdown-content .markdown-list,
.markdown-content ul {
  margin: 10px 0;
  padding-left: 24px;
  color: #374151 !important;
}

.dark-mode .markdown-content .markdown-list,
.dark-mode .markdown-content ul {
  color: #e5e7eb !important;
}

.markdown-content .markdown-item,
.markdown-content li {
  margin: 6px 0;
  color: #374151 !important;
}

.dark-mode .markdown-content .markdown-item,
.dark-mode .markdown-content li {
  color: #e5e7eb !important;
}

/* Markdown text formatting with explicit colors */
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

/* Markdown code with explicit colors */
.markdown-content .markdown-code,
.markdown-content code {
  background: rgba(59, 130, 246, 0.1) !important;
  color: #1e40af !important;
  padding: 3px 8px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.9em;
}

.dark-mode .markdown-content .markdown-code,
.dark-mode .markdown-content code {
  background: rgba(96, 165, 250, 0.2) !important;
  color: #93c5fd !important;
}

/* Markdown code blocks with explicit colors */
.markdown-content .markdown-pre,
.markdown-content pre {
  background: rgba(0, 0, 0, 0.05) !important;
  color: #1f2937 !important;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 10px 0;
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

/* Markdown breaks */
.markdown-content .markdown-break,
.markdown-content br {
  line-height: 1.5;
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

/* Additional specificity for stubborn elements */
.message-bubble.bot .markdown-content .markdown-paragraph,
.message-bubble.bot .markdown-content .markdown-item,
.message-bubble.bot .markdown-content .markdown-header {
  color: #333 !important;
}

.dark-mode .message-bubble.bot .markdown-content .markdown-paragraph,
.dark-mode .message-bubble.bot .markdown-content .markdown-item,
.dark-mode .message-bubble.bot .markdown-content .markdown-header {
  color: #f1f5f9 !important;
}

/* Override any default browser styles */
.markdown-content * {
  color: inherit !important;
}

/* Ensure proper contrast for code elements */
.message-bubble.bot .markdown-content .markdown-code {
  background: rgba(59, 130, 246, 0.15) !important;
  color: #1e40af !important;
}

.dark-mode .message-bubble.bot .markdown-content .markdown-code {
  background: rgba(96, 165, 250, 0.25) !important;
  color: #93c5fd !important;
}

/* Responsive design */
@media (max-width: 768px) {
  .chatbot-page {
    padding: 10px;
  }
  
  .chatbot-container {
    max-width: 100%;
    border-radius: 12px;
  }
  
  .chat-header {
    padding: 15px;
    min-height: 70px;
  }
  
  .chat-avatar {
    width: 40px;
    height: 40px;
  }
  
  .chat-info h2 {
    font-size: 1.1rem;
  }
  
  .chat-messages {
    padding: 15px;
    min-height: 300px;
  }
  
  .suggested-prompts {
    max-width: 300px;
  }
  
  .suggested-prompt {
    font-size: 0.85rem;
    padding: 10px 16px;
  }
}

@media (max-width: 480px) {
  .chatbot-page {
    padding: 5px;
  }
  
  .chat-header {
    padding: 12px;
  }
  
  .chat-info h2 {
    font-size: 1rem;
  }
  
  .chat-info p {
    font-size: 0.8rem;
  }
  
  .chat-messages {
    padding: 12px;
    gap: 10px;
  }
  
  .message-bubble {
    max-width: 85%;
    padding: 10px 15px;
  }
  
  .chat-input {
    padding: 15px;
  }
  
  .input-form {
    padding: 4px 12px;
  }
  
  .voice-btn, .send-btn {
    width: 36px;
    height: 36px;
  }
}
</style>