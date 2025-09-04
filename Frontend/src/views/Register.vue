<script setup>
import { RouterLink } from 'vue-router';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { auth } from '@/stores/auth';
import { messageStore } from '@/stores/messageStore';

const name = ref('');
const email = ref('');
const password = ref('');
const mobile = ref('');
const address = ref('');
const pin = ref('');
const gender = ref('');
const dob = ref('');
const selectedRole = ref('user');

const router = useRouter();
const auth_store = auth();
const message_store = messageStore();

const roleInfo = computed(() => {
  switch (selectedRole.value) {
    case 'caretaker':
      return [
        "Receive missed medicine alerts.",
        "Get daily health summaries.",
        "View live location (with consent)."
      ];
    case 'ngo':
      return [
        "Send preventive health tips.",
        "View community health trends."
      ];
    default:
      return [
        "As a senior, you can receive care and assistance via the app."
      ];
  }
});

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

async function onSubmit() {
  if (!isValidEmail(email.value)) {
    alert("Please enter a valid email.");
    return;
  }
  if (password.value.length < 6) {
    alert("Password must be at least 6 characters.");
    return;
  }
  if (!mobile.value.match(/^\d{10}$/)) {
    alert("Enter a valid 10-digit mobile number.");
    return;
  }

  const data = {
    user_name: name.value,
    email: email.value,
    password: password.value,
    mobile_number: mobile.value,
    address: address.value,
    pincode: pin.value,
    gender: gender.value,
    dob: dob.value,
    role: selectedRole.value
  };

  auth_store.register(data).then((resp) => {
    message_store.setmessage(resp.message);
    if (resp.status) {
      router.push('/userlogin');
    }
  });
}
</script>

<template>
  <div class="register-container">
    <div class="register-card">
      <div class="card-left">
        <img src="../assets/login.png" alt="Elderly care" class="caretaker-image">
      </div>
      <div class="card-right">
        <h1 class="text-center">Register for SHRAVAN</h1>
        <p class="text-center subtitle">Connecting Care with Compassion</p>

        <form @submit.prevent="onSubmit">
          <div class="mb-3">
            <label for="name" class="form-label">Name</label>
            <input type="text" class="form-control" id="name" v-model="name" placeholder="Enter your name" required>
          </div>

          <div class="form-row">
            <div class="mb-3 form-col">
              <label for="email" class="form-label">Email</label>
              <input type="email" class="form-control" id="email" v-model="email" placeholder="Enter your email" required>
            </div>

            <div class="mb-3 form-col">
              <label for="password" class="form-label">Password (min 6 chars)</label>
              <input type="password" class="form-control" id="password" v-model="password" placeholder="Enter a strong password" required>
            </div>
          </div>

          <div class="form-row">
            <div class="mb-3 form-col">
              <label for="mobile" class="form-label">Mobile Number</label>
              <input type="tel" class="form-control" id="mobile" v-model="mobile" placeholder="Enter your mobile number" required>
            </div>

            <div class="mb-3 form-col">
              <label for="gender" class="form-label">Gender</label>
              <select class="form-select" id="gender" v-model="gender" required>
                <option disabled value="">Select</option>
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
            </div>
          </div>

          <div class="mb-3">
            <label for="dob" class="form-label">Date of Birth</label>
            <input type="date" class="form-control" id="dob" v-model="dob" required>
          </div>

          <div class="mb-3">
            <label for="address" class="form-label">Address</label>
            <textarea class="form-control" id="address" rows="2" v-model="address" placeholder="City"></textarea>
          </div>

          <div class="mb-3">
            <label for="pin" class="form-label">Pincode</label>
            <input type="text" class="form-control" id="pin" v-model="pin" placeholder="Enter pincode">
          </div>

          <div class="mb-3">
            <label for="role" class="form-label">Select Your Role</label>
            <select class="form-select" id="role" v-model="selectedRole">
              <option value="user">Senior Citizen (Primary)</option>
              <option value="caretaker">Care Taker (Secondary)</option>
              <option value="ngo">NGO / Health Center (Tertiary)</option>
            </select>
          </div>

          <div class="d-flex justify-content-center mb-3">
            <button type="submit" class="btn register-button">Register</button>
          </div>
        </form>

        <div class="d-flex justify-content-center mt-2">
          <span class="me-2">Already have an account?</span>
          <RouterLink class="btn btn-outline-light" to="/userlogin">Login</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #10b981, #3b82f6, #06b6d4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
  position: fixed;
  inset: 0;
  overflow-y: auto;
  padding: 20px 0;
  margin-top: 80px;
}

.register-card {
  width: 90%;
  max-width: 1100px;
  display: flex;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin: auto;
  min-height: 600px;
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
  overflow-y: auto;
  max-height: 90vh;
}

.card-right::-webkit-scrollbar {
  width: 6px;
}

.card-right::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.card-right::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #10b981, #3b82f6);
  border-radius: 4px;
}

.card-right::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #059669, #2563eb);
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

.form-label {
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 8px;
  display: block;
  font-size: 1rem;
  font-family: 'Inter', sans-serif;
}

.form-control, .form-select {
  border-radius: 12px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  padding: 12px 16px;
  margin-bottom: 20px;
  background: transparent;
  color: #ffffff;
  width: 100%;
  font-family: 'Inter', sans-serif;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.form-control::placeholder {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
}

.form-control:focus, .form-select:focus {
  outline: none;
  border-color: #ffffff;
  background: transparent;
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.2);
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-col {
  flex: 1;
}

.register-button {
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

.register-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: all 0.5s ease;
}

.register-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(16, 185, 129, 0.4);
  background: linear-gradient(135deg, #059669, #2563eb);
}

.register-button:hover::before {
  left: 100%;
}

.btn-outline-light {
  color: #ffffff;
  border: 2px solid #ffffff;
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
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
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
  color: #ffffff;
  font-weight: 400;
  font-family: 'Inter', sans-serif;
}

.role-info-box {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.role-info-title {
  color: #ffffff;
  font-weight: 600;
  margin-bottom: 10px;
  font-size: 1rem;
  font-family: 'Inter', sans-serif;
}

.role-info-list {
  list-style: none;
  padding-left: 5px;
  margin: 0;
}

.role-info-list li {
  margin-bottom: 5px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  font-family: 'Inter', sans-serif;
}

.role-info-list li::before {
  content: '✓ ';
  color: #10b981;
  font-weight: bold;
  margin-right: 5px;
}

.mb-3 {
  margin: 0px;
}

.d-flex {
  display: flex;
}

.justify-content-center {
  justify-content: center;
}

.mt-2 {
  margin-top: 15px;
}


@media (max-width: 992px) {
  .register-card {
    width: 95%;
    flex-direction: column;
    min-height: auto;
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
    max-height: unset;
    flex: none;
  }
  
  h1 {
    font-size: 1.8rem;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }
}

@media (max-width: 480px) {
  .register-container {
    padding: 10px;
  }

  .register-card {
    width: 98%;
    border-radius: 15px;
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
  
  .subtitle {
    font-size: 0.9rem;
  }
}
</style>
