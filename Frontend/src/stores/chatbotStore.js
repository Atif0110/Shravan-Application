import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatbotStore = defineStore('chatbot', () => {
  // Messages history
  const messages = ref([]);
  
  // Chat history for the AI context
  const chatHistory = ref({
    user: '',
    assistant: ''
  });
  
  // Add a message to the chat
  function addMessage(message) {
    messages.value.push(message);
  }
  
  // Update chat history
  function updateChatHistory(newHistory) {
    chatHistory.value = newHistory;
  }
  
  // Clear all messages and history
  function clearChat() {
    messages.value = [];
    chatHistory.value = {
      user: '',
      assistant: ''
    };
  }
  
  return {
    messages,
    chatHistory,
    addMessage,
    updateChatHistory,
    clearChat
  }
})
