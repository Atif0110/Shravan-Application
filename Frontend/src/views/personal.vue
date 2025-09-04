<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
    <!-- Navbar -->
    <nav class="bg-white shadow-lg border-b">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <h1 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Personal Chatbot</h1>
          </div>
          <button 
            @click="showModal = true"
            class="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 font-medium shadow-md hover:shadow-lg"
          >
            Update AI Persona
          </button>
        </div>
      </div>
    </nav>

    <!-- Main Chat Interface -->
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-4xl mx-auto">
        <div class="bg-white/10 backdrop-blur-md rounded-xl shadow-lg h-[600px] flex flex-col border border-white/20">
          <!-- Chat Header -->
          <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-xl">
            <h2 class="text-lg font-semibold">
              Chat with {{ currentPersonaName || 'Your AI Persona' }}
            </h2>
          </div>

          <!-- Messages Area -->
          <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-gray-50/50 to-white/50">
            <div v-if="messages.length === 0 && !isPersonaConfigured" class="text-center text-gray-500 mt-20">
              <div class="text-6xl mb-4">🤖</div>
              <p class="text-lg">Configure your persona to start chatting!</p>
              <button 
                @click="showModal = true"
                class="mt-4 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 font-medium"
              >
                Update AI Persona
              </button>
            </div>

            <div v-if="messages.length === 0 && isPersonaConfigured" class="text-center text-gray-500 mt-20">
              <div class="text-6xl mb-4">💬</div>
              <p class="text-lg">Start your conversation with {{ currentPersonaName }}!</p>
            </div>
            
            <div v-for="(message, index) in messages" :key="index" class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
              <div class="max-w-xs lg:max-w-md px-4 py-3 rounded-xl shadow-md" 
                   :class="message.role === 'user' ? 
                           'bg-gradient-to-r from-blue-500 to-blue-600 text-white' : 
                           'bg-white/80 backdrop-blur-sm text-gray-800 border border-gray-200/50'">
                <p class="whitespace-pre-wrap">{{ message.content }}</p>
              </div>
            </div>

            <div v-if="isLoading" class="flex justify-start">
              <div class="bg-white/80 backdrop-blur-sm text-gray-800 border border-gray-200/50 shadow-md max-w-xs lg:max-w-md px-4 py-3 rounded-xl">
                <div class="flex items-center space-x-2">
                  <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                    <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  </div>
                  <span class="text-sm text-gray-500">{{ currentPersonaName || 'AI' }} is thinking...</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Input Area -->
          <div class="p-4 border-t border-white/20 bg-white/5 backdrop-blur-sm rounded-b-xl">
            <form @submit.prevent="sendMessage" class="flex gap-3">
              <input 
                v-model="currentMessage" 
                :disabled="isLoading || !isPersonaConfigured" 
                type="text" 
                placeholder="Type your message..." 
                class="flex-1 px-4 py-3 border-2 border-gray-200/60 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100/50 disabled:cursor-not-allowed transition-all duration-200 bg-transparent hover:border-gray-300 placeholder-gray-400"
              >
              <button 
                type="submit" 
                :disabled="isLoading || !currentMessage.trim() || !isPersonaConfigured" 
                class="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:transform-none"
              >
                Send
              </button>
            </form>
            <p v-if="!isPersonaConfigured" class="text-sm text-gray-500 mt-2">
              Please configure your persona to start chatting
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Persona Configuration Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-gray-800">Configure AI Persona</h2>
            <button 
              @click="showModal = false"
              class="text-gray-400 hover:text-gray-600 text-2xl"
            >
              &times;
            </button>
          </div>

          <form @submit.prevent="updatePersona" class="space-y-4">
            <!-- Gender -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Gender</label>
              <select 
                v-model="persona.gender" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                required
              >
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="non-binary">Non-binary</option>
              </select>
            </div>

            <!-- Age -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Age</label>
              <input 
                v-model="persona.age" 
                type="number" 
                min="1" 
                max="120" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                required
              >
            </div>

            <!-- Profession -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Profession</label>
              <input 
                v-model="persona.profession" 
                type="text" 
                placeholder="e.g., Software Engineer" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                required
              >
            </div>

            <!-- Personality Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Personality Type</label>
              <select 
                v-model="persona.personality_type" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                required
              >
                <option value="">Select Personality</option>
                <option value="friendly">Friendly</option>
                <option value="professional">Professional</option>
                <option value="creative">Creative</option>
                <option value="analytical">Analytical</option>
                <option value="empathetic">Empathetic</option>
              </select>
            </div>

            <!-- Communication Style -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Communication Style</label>
              <select 
                v-model="persona.communication_style" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              >
                <option value="casual">Casual</option>
                <option value="formal">Formal</option>
                <option value="humorous">Humorous</option>
                <option value="direct">Direct</option>
                <option value="detailed">Detailed</option>
              </select>
            </div>

            <!-- Expertise Areas -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Expertise Areas</label>
              <div class="flex gap-2 mb-3">
                <input 
                  v-model="newExpertise" 
                  @keyup.enter="addExpertise" 
                  type="text" 
                  placeholder="Add expertise area" 
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                >
                <button 
                  type="button" 
                  @click="addExpertise" 
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add
                </button>
              </div>
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="(area, index) in persona.expertise_areas" 
                  :key="index" 
                  class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center gap-2"
                >
                  {{ area }}
                  <button 
                    type="button" 
                    @click="removeExpertise(index)" 
                    class="text-blue-600 hover:text-red-500 font-bold"
                  >
                    &times;
                  </button>
                </span>
              </div>
            </div>

            <div class="flex gap-3 pt-4">
              <button 
                type="button" 
                @click="showModal = false"
                class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                class="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
              >
                Update Persona
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'PersonalChatbot',
  data() {
    return {
      showModal: false,
      persona: {
        gender: '',
        age: '',
        profession: '',
        personality_type: '',
        communication_style: 'casual',
        expertise_areas: []
      },
      newExpertise: '',
      currentPersonaName: '',
      messages: [],
      currentMessage: '',
      isLoading: false
    }
  },
  computed: {
    isPersonaConfigured() {
      return this.persona.gender && this.persona.age && this.persona.profession && this.persona.personality_type
    }
  },
  methods: {
    addExpertise() {
      if (this.newExpertise.trim() && !this.persona.expertise_areas.includes(this.newExpertise.trim())) {
        this.persona.expertise_areas.push(this.newExpertise.trim())
        this.newExpertise = ''
      }
    },
    removeExpertise(index) {
      this.persona.expertise_areas.splice(index, 1)
    },
    updatePersona() {
      this.showModal = false
      this.$toast.success('Persona configuration updated!')
    },
    async sendMessage() {
      if (!this.currentMessage.trim() || !this.isPersonaConfigured) return

      const userMessage = this.currentMessage.trim()
      this.messages.push({
        role: 'user',
        content: userMessage
      })
      this.currentMessage = ''
      this.isLoading = true
      this.scrollToBottom()

      try {
        const response = await axios.post('http://localhost:5000/api/personal-chatbot', {
          question: userMessage,
          history: this.messages.slice(0, -1),
          gender: this.persona.gender,
          age: parseInt(this.persona.age),
          profession: this.persona.profession,
          personality_type: this.persona.personality_type,
          expertise_areas: this.persona.expertise_areas,
          communication_style: this.persona.communication_style
        })

        if (response.data.status === 'success') {
          this.messages.push({
            role: 'assistant',
            content: response.data.response
          })
          this.currentPersonaName = response.data.persona_name
        } else {
          throw new Error(response.data.error || 'Unknown error occurred')
        }
      } catch (error) {
        console.error('Error sending message:', error)
        this.messages.push({
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.'
        })
        this.$toast.error('Failed to send message. Please try again.')
      } finally {
        this.isLoading = false
        this.scrollToBottom()
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    }
  }
}
</script>

<style scoped>
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #2563eb, #7c3aed);
}
</style>