<script setup>
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { useCitationStore } from '@/stores/citationStore'
import MainPageHeader from '@/components/MainPageHeader.vue'
import LeftSidebar from '@/components/SideBar/LeftSidebar.vue'
import RightSidebar from '@/components/SideBar/RightSidebar.vue'
import CitationSourceSelector from '@/components/CitationSourceSelector.vue'
import CitationStyleSelector from '@/components/CitationStyleSelector.vue'
import { provide, computed } from 'vue'
import CiteMeLogo from '@/components/CiteMeLogo.vue';

const store = useCitationStore()

// Provide shared state to components
provide('editorContent', store.editorContent)
provide('previewContent', store.previewContent)
provide('documentTitle', store.documentTitle)

// Provide word and character counts
provide('wordCount', computed(() => store.wordCount))
provide('charCount', computed(() => store.charCount))

const selectedForm = defineModel('selectedForm')
const citationStyle = defineModel('citationStyle')
</script>

<template>
    <div class="flex h-screen w-screen overflow-hidden">
        <Transition name="slide-left">
            <LeftSidebar
                v-if="store.isLeftSidebarOpen"
                class="fixed left-0 top-0 z-50 h-screen shadow-lg"
                @close="store.toggleLeftSidebar"
                :editor-content="{
                    title: store.previewContent.title,
                    content: store.editorContent,
                }"
            />
        </Transition>

        <div class="flex w-full flex-col">
            <!-- Header -->
            <MainPageHeader
                :disable-btn="store.disableCiteMeBtn"
                @toggle-sidebar="store.toggleLeftSidebar"
                v-model:title="store.documentTitle"
                v-model:show-preview="store.isPreviewMode"
                @generate-citations="() => store.generateCitations(selectedForm, citationStyle)"
                @navigate-to-editor="store.navigateToEditor"
                @navigate-to-preview="store.navigateToPreview"
                class="flex-shrink-0 border-b-2 border-gray-400"
            />

            <Teleport to="#citationStyleSelector" defer>
                <CitationStyleSelector v-model:citation-style="citationStyle" />
            </Teleport>
            <Teleport to="#mobileCitationStyleSelector" defer>
                <CitationStyleSelector v-model:citation-style="citationStyle" />
            </Teleport>

            <div class="flex relative">
                <!-- Main content area -->
                <div class="mx-auto flex h-[calc(100vh-76px)] w-[90%] flex-col lg:w-[800px]">
                    <!-- Citation Source Selector -->
                    <div v-if="!store.isPreviewMode" class="flex-shrink-0 py-2">
                        <CitationSourceSelector v-model:selected-form="selectedForm" />
                    </div>


                    <!-- Router view -->
                    <router-view
                        class="flex-grow overflow-hidden"
                        :key="$route.path"
                        v-model:editorContent="store.editorContent"
                        :preview-content="store.previewContent"
                        @edit="store.editPreview"
                    />
                </div>
            </div>


        </div>

        <!-- Right sidebar toggle button -->
        <button
            @click="store.toggleRightSidebar"
            class="fixed right-0 top-1/2 z-40 -translate-y-1/2 rounded-l-lg bg-white p-2 shadow-md hover:bg-gray-50"
        >
            <component
                :is="store.isRightSidebarOpen ? ChevronRight : ChevronLeft"
                class="h-5 w-5 text-gray-600"
            />
        </button>

        <!-- Right Sidebar -->
        <Transition name="slide-right">
            <RightSidebar
                :credibility-score="store.credibilityScore"
                :sources="store.sources"
                v-show="store.isRightSidebarOpen"
                @close="store.toggleRightSidebar"
                class="fixed right-0 top-0 z-50 h-screen shadow-lg lg:static lg:shadow-none"
            />
        </Transition>

        <!-- Overlay -->
        <div
            v-show="store.isLeftSidebarOpen"
            class="fixed inset-0 z-40 bg-black/50"
            @click="store.toggleLeftSidebar"
        />
    </div>
</template>
