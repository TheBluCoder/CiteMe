/**
 * Citation Store
 * Central state management for the citation application
 * Handles document content, citations, navigation, and UI state
 */

import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useToast } from 'vue-toastification'
import { cleanCitationData } from '@/constants/cleanCitationData.js'
import { useRouter } from 'vue-router'

// Constants
const STORAGE_KEYS = {
  EDITOR_CONTENT: 'editorContent'
}

const API_ENDPOINTS = {
  GENERATE_CITATION: import.meta.env.VITE_BACKEND_URL + '/citation/get_citation'
}

export const useCitationStore = defineStore('citation', () => {
    const router = useRouter()
    const toast = useToast()

    // UI State
    const isLeftSidebarOpen = ref(false)
    const isRightSidebarOpen = ref(true)
    const isCitationLoading = ref(false)
    const disableCiteMeBtn = ref(false)

    // Document State
    const documentTitle = ref('')
    const editorContent = ref(localStorage.getItem(STORAGE_KEYS.EDITOR_CONTENT) || '')
    const credibilityScore = ref(0)
    const sources = ref([])
    const wordCount = ref(0)
    const charCount = ref(0)

    // Preview State
    const previewContent = ref({
        title: computed(() => documentTitle.value),
        content: []
    })

    // Computed Properties
    const isPreviewMode = computed(() =>
        router.currentRoute.value.path === '/preview'
    )

    /**
     * Updates word and character counts for given content
     * @param {string} content - The content to analyze
     */
    function updateCounts(content) {
        if (!content) {
            wordCount.value = charCount.value = 0
            return
        }

        const plainText = content.replace(/<[^>]*>/g, ' ')
        charCount.value = plainText.replace(/\s/g, '').length

        const words = plainText.trim().split(/\s+/)
        wordCount.value = words.length > 1 || (words.length === 1 && words[0] !== '') ? words.length : 0
    }

    // Watchers
    watch(editorContent, (newContent) => {
        if (!newContent) {
            localStorage.removeItem(STORAGE_KEYS.EDITOR_CONTENT)
            wordCount.value = charCount.value = 0
        } else {
            localStorage.setItem(STORAGE_KEYS.EDITOR_CONTENT, newContent)
            updateCounts(newContent)
        }
    })

    watch(() => previewContent.value.content, (newContent) => {
        if (!newContent?.length) {
            wordCount.value = charCount.value = 0
            return
        }
        updateCounts(newContent[0])
    }, { deep: true })

    // UI Actions
    const toggleLeftSidebar = () => {
        isLeftSidebarOpen.value = !isLeftSidebarOpen.value
        if (isLeftSidebarOpen.value) isRightSidebarOpen.value = false
    }

    const toggleRightSidebar = () => {
        isRightSidebarOpen.value = !isRightSidebarOpen.value
        if (isRightSidebarOpen.value) isLeftSidebarOpen.value = false
    }

    // Navigation Actions
    const navigateToEditor = () => router.push('/editor')
    const navigateToPreview = () => router.push('/preview')

    /**
     * Transfers preview content back to editor for modifications
     */
    const editPreview = () => {
        const [formattedText, reference] = previewContent.value.content
        editorContent.value = formattedText + '<h2>References</h2>' + reference
        navigateToEditor()
    }

    /**
     * Generates citations based on selected form and style
     * @param {string} selectedForm - The selected citation form
     * @param {string} citationStyle - The desired citation style
     */
    async function generateCitations(selectedForm, citationStyle) {
        // Validation
        if (!documentTitle.value.trim()) {
            toast.error("Document title is required")
            return
        }

        const isAutoForm = String(selectedForm).toLowerCase() === 'citationautoform'
        let storedFormData = isAutoForm ? { formType: 'auto' } : localStorage.getItem(selectedForm)

        if (!isAutoForm) {
            let strippedContent = stripHTML(editorContent.value)
            if (!strippedContent.trim()) {
                toast.error('Please add some content to cite')
                return
            }

            if (!storedFormData) {
                toast.error('Please select a citation source')
                return
            }
        }

        try {
            isCitationLoading.value = true
            disableCiteMeBtn.value = true

            const formData = typeof storedFormData === 'string'
                ? JSON.parse(storedFormData)
                : storedFormData

            const requestData = cleanCitationData({
                ...formData,
                title: previewContent.value.title,
                content: editorContent.value,
                citationStyle
            })

            const { data } = await axios.post(API_ENDPOINTS.GENERATE_CITATION, requestData)

            previewContent.value.content = [
                data.result.formatted_text,
                data.result.references
            ]
            credibilityScore.value = data.overall_score
            sources.value = data.sources
            navigateToPreview()
        } catch (error) {
            console.error('Error generating citations:', error)
            toast.error('Error generating citations. Please try again.')
        } finally {
            isCitationLoading.value = false
            disableCiteMeBtn.value = false
        }
    }

    function stripHTML(htmlString) {
        // Create a temporary DOM element
        const tempElement = document.createElement('div');
        tempElement.innerHTML = htmlString;

        // Extract and return the inner text
        return tempElement.textContent || tempElement.innerText || '';
    }


    return {
        // UI State
        isLeftSidebarOpen,
        isRightSidebarOpen,
        isCitationLoading,
        disableCiteMeBtn,

        // Document State
        documentTitle,
        editorContent,
        credibilityScore,
        sources,
        wordCount,
        charCount,

        // Preview State
        previewContent,
        isPreviewMode,

        // Actions
        toggleLeftSidebar,
        toggleRightSidebar,
        navigateToEditor,
        navigateToPreview,
        editPreview,
        generateCitations
    }
})
