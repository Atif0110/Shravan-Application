<script setup>
import { RouterLink } from 'vue-router';
import { auth } from '@/stores/auth';
import { messageStore } from '@/stores/messageStore';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');

const router = useRouter();
const auth_store = auth();
const message_store = messageStore();

async function onSubmit() {
  const data = {
    email: email.value,
    password: password.value
  };

  auth_store.login(data).then((resp) => {
  message_store.setmessage(resp.message);
  // console.log(auth_store)
  // const role = auth_store.role;
  // console.log(role);
  if (resp.status && resp.role === 'user') {
    router.push({ path: '/userdashboard' });
  } else if (resp.status && resp.role === 'caretaker') {
    router.push({ path: '/caretaker' });
  } else if (resp.status && resp.role === 'ngo') {
    router.push({ path: '/tertiaryuser' });
  } else {
    router.push({ path: '/' });
  }
  });

}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="card-left">
        <img src="../assets/login.png" alt="Expert Caretaker" class="caretaker-image">
      </div>
      <div class="card-right">
      <h1 class="text-center">Login to SHRAVAN</h1>
      <p class="text-center subtitle">Your wellness, our priority</p>
      <form @submit.prevent="onSubmit" class="form-wrapper">
        <div class="form-group">
          <label for="email">Email Address</label>
          <input type="email" id="email" placeholder="Enter your email" v-model="email" required />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" placeholder="Enter your password" v-model="password" required />
        </div>

        <button type="submit" class="login-button">Login</button>
      </form>

        <br>
        <div class="d-flex justify-content-center mt-2">
          <span class="me-2">Don't have an account?</span>
          <RouterLink class="btn btn-outline-light" to="/register">Register</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #10b981, #3b82f6, #06b6d4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
  position: fixed; 
  inset: 0;
  margin: 0;
  padding: 0;
}

.form-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 400px;
}

.form-group label {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #ffffff;
  font-family: 'Inter', sans-serif;
}

.form-group input {
  padding: 14px 16px;
  font-size: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  width: 100%;
  background: transparent;
  color: #ffffff;
  font-family: 'Inter', sans-serif;
  transition: all 0.3s ease;
}

.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
}

.form-group input:focus {
  outline: none;
  border-color: #ffffff;
  background: transparent;
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.2);
}

.login-card {
  width: 85%;
  max-width: 1000px;
  height: 600px;
  display: flex;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.card-left {
  flex: 0.5;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(59, 130, 246, 0.1));
  position: relative;
  display: flex;
  justify-content: center;
  align-items: stretch;
  padding: 0;
  overflow: hidden;
}

.card-left::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  width: 1px;
  background: linear-gradient(to bottom, transparent, rgba(0, 0, 0, 0.1), transparent);
  z-index: 2;
}

.caretaker-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition: transform 0.5s ease;
}

.caretaker-image:hover {
  transform: scale(1.02);
}

.card-right {
  flex: 0.5;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 40px;
  color: #1f2937;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.text-center {
  text-align: center;
}

h1 {
  color: #1f2937;
  margin-bottom: 10px;
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 2.2rem;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 1rem;
  color: #6b7280;
  margin-bottom: 35px;
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  letter-spacing: 0.2px;
  position: relative;
  display: inline-block;
}

.subtitle::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -10px;
  transform: translateX(-50%);
  width: 50px;
  height: 2px;
  background: linear-gradient(90deg, #10b981, #3b82f6);
}

.login-button {
  background: linear-gradient(135deg, #10b981, #3b82f6);
  border: none;
  color: #fff;
  padding: 14px 32px;
  border-radius: 12px;
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  width: 100%;
  margin-top: 10px;
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
  position: relative;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: all 0.5s ease;
}

.login-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(16, 185, 129, 0.4);
  background: linear-gradient(135deg, #059669, #2563eb);
}

.login-button:hover::before {
  left: 100%;
}

.btn-outline-light {
  color: #ffffff;
  border: 2px solid #feffff;
  margin: 0 10px;
  background-color: transparent;
  border-radius: 12px;
  padding: 8px 20px;
  font-weight: 500;
  transition: all 0.3s ease;
  font-family: 'Inter', sans-serif;
  text-decoration: none;
  position: relative;
  overflow: hidden;
}

.btn-outline-light::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(218, 236, 230, 0.3), transparent);
  transition: all 0.5s ease;
  z-index: -1;
}

.btn-outline-light:hover {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.1));
  color: #eaf5f1;
  border-color: #e8fff8;
  transform: translateY(-2px);
  text-decoration: none;
  box-shadow: 0 8px 15px rgba(16, 185, 129, 0.3);
  animation: pulse 2s infinite;
}

.btn-outline-light:hover::before {
  left: 100%;
}

.btn-outline-light:active {
  transform: translateY(0);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.2);
}

@keyframes pulse {
  0% {
    box-shadow: 0 8px 15px rgba(16, 185, 129, 0.3);
  }
  50% {
    box-shadow: 0 12px 25px rgba(16, 185, 129, 0.4);
  }
  100% {
    box-shadow: 0 8px 15px rgba(16, 185, 129, 0.3);
  }
}

.me-2 {
  color: #6b7280;
  margin-top: 10px;
  font-weight: 400;
  font-family: 'Inter', sans-serif;
}

.d-flex {
  display: flex;
}

.justify-content-center {
  justify-content: center;
}

.mt-2 {
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .login-card {
    width: 95%;
    height: auto;
    flex-direction: column;
  }
  
  .card-left {
    height: 250px;
    flex: none;
  }
  
  .card-left::after {
    top: auto;
    right: 10%;
    bottom: 0;
    height: 1px;
    width: 80%;
    background: linear-gradient(to right, transparent, rgba(0, 0, 0, 0.1), transparent);
  }
  
  .card-right {
    padding: 30px 25px;
    flex: none;
  }
  
  h1 {
    font-size: 1.8rem;
  }
  
  .form-group input {
    padding: 12px 14px;
    font-size: 0.95rem;
  }
  
  .form-group label {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .login-card {
    width: 98%;
    margin: 10px;
  }
  
  .card-right {
    padding: 25px 20px;
  }
  
  .card-left {
    height: 200px;
  }
  
  h1 {
    font-size: 1.6rem;
  }
}
</style>
