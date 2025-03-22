/**
 * Main application entry point
 * This file initializes the Vue application and configures core plugins
 */

// Style imports
import './assets/main.css'

// Vue core imports
import { createApp } from 'vue'
import App from './App.vue'

// Plugin imports
import { createPinia } from 'pinia'
import Toast from 'vue-toastification'
import "vue-toastification/dist/index.css"
import router from './router'

// Toast notification configuration
const toastOptions = {
  position: 'bottom-right',
  timeout: 3000,
  closeOnClick: true,
  pauseOnHover: true,
};

// Create and configure the Vue application
const app = createApp(App)

// Register plugins
app.use(Toast, toastOptions)
app.use(createPinia()) // State management
app.use(router)       // Router configuration

// Mount the application
app.mount('#app')
