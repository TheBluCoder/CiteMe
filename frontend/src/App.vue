<!--
  App.vue - Root Component
  This is the main application component that serves as the entry point for the UI.
  It manages the main layout and global state for citation forms and styles.
-->

<script setup>
import MainLayout from '@/layouts/MainLayout.vue'
import { ref } from 'vue'

// Global state for selected citation form and style
const selectedForm = ref('') // Tracks the currently selected citation form
const citationStyle = ref('') // Tracks the selected citation style format
</script>

<template>
    <MainLayout
        v-model:selected-form="selectedForm"
        v-model:citation-style="citationStyle"
    />
</template>

<style>
/* Global styles can be added here if needed */
</style>
