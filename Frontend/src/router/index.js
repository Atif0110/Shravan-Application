import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../views/LandingPage.vue'
import TertiaryUserDashboard from '@/views/TertiaryUserDashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: LandingPage,
    },
    {
      path: '/userlogin',
      name: 'userlogin',
      component: () => import('../views/Login.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/Register.vue'),
    },
    {
      path: '/userdashboard',
      name: 'userdashboard',
      component: () => import('../views/UserDashboard.vue'),
    },
    {
      path: '/caretaker',
      name: 'caretaker',
     component: () => import('../views/CareTakerDashboard.vue'),
    },
    {
      path: '/tertiaryuser',
      name: 'tertiaryuser',
      component: () => import('../views/TertiaryUserDashboard.vue'),
    },
    {
      path: '/chatbot',
      name: 'chatbot',
      component: () => import('../views/Chatbot.vue'),
    },
    {
      path: '/medicinereminders',
      name: 'medicinereminders',
      component: () => import('../views/MedicineReminders.vue'),
    },
    {
      path: '/download-app',
      name: 'downloadapp',
      component: () => import('../views/DownloadApp.vue'),
    },
    {
      path: '/doctor-finder',
      name: 'doctorfinder',
      component: () => import('../views/Doctorfinder.vue'),
    },
    {
      path: '/yoga-videos',
      name: 'videos',
      component: () => import('../views/Yogavideos.vue'),
    },
    {
      path: '/pharmacy-finder',
      name: 'pharmacy-finder',
      component: () => import('../views/pharmacyfinder.vue'),
    },
    {
      path: '/missedmedicinealert',
      name: 'missedmedicinealert',
      component: () => import('../views/missedmedicinealerts.vue'),
    },
    {
      path: '/locationfinder',
      name: 'locationfinder',
      component: () => import('../views/Locationfinder.vue'),
    },
    {
      path: '/addmedicinealert',
      name: 'addmedicinealert',
      component: () => import('../views/Addmedicine.vue')
    },
    {
      path: '/deletemedicinealert',
      name: 'deletemedicinealert',
      component: () => import('../views/Deletemedicine.vue')
    },
    {
      path: '/sharehealthtips',
      name: 'sharehealthtips',
      component: () => import('../views/Sharehealthtips.vue'),
    },
    {
      path: '/share-yoga-videos',
      name: 'share-yoga-videos',
      component: () => import('../views/ShareYogaVideos.vue'),
    },
    {
      path: '/voice-reminders',
      name: 'voice-remainders',
      component: () => import('../views/Voiceremainders.vue')
    },
    {
      path: '/daily-health',
      name: 'daily-health',
      component: () => import('../views/DailyHealth.vue')
    },

    {
      path: '/animation',
      name: 'animation',
      component: () => import('../views/YogaAnimation.vue')
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/profile',
      name: 'UserProfile',
      component: () => import('../views/UserProfile.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/hospital-finder',
      name: 'HospitalFinder',
      component: () => import('../views/HospitalFinder.vue'),

    },
    {
      path: '/personal-chatbot',
      name: 'PersonalChatbot',
      component: () => import('../views/PersonalChatbot.vue'),
      meta: { requiresAuth: true }
    },
  ],
})

export default router
