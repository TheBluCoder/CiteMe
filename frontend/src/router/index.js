/**
 * Router Configuration
 * Defines the application's routing structure and navigation behavior
 */

import { createRouter, createWebHistory } from 'vue-router'
import Editor from '@/views/Editor.vue'
import Preview from '@/views/Preview.vue'

// Route definitions
const routes = [
  {
    path: '/',
    redirect: '/editor',
    meta: {
      title: 'Home'
    }
  },
  {
    path: '/editor',
    name: 'Editor',
    component: Editor,
    meta: {
      title: 'Citation Editor'
    }
  },
  {
    path: '/preview',
    name: 'Preview',
    component: Preview,
    meta: {
      title: 'Citation Preview'
    }
  }
]

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard to update document title
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'Citation App'}`
  next()
})

export default router
