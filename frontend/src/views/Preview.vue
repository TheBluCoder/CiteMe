<script setup>
import {defineOptions, provide, computed} from 'vue';
import WordAndCharacterCount from '@/components/Editor/WordAndCharacterCount.vue';
import PreviewToolBar from '@/components/Preview/PreviewToolBar.vue';
import { useCitationStore } from '@/stores/citationStore';

defineOptions({ name: 'previewComponent' });
const store = useCitationStore();

const props = defineProps({
  previewContent: {
    type: Object,
    required: true,
    default: () => ({
      title: '',
      content: [],
    }),
  },
});

const emits = defineEmits(['edit']);
provide('emits', emits);

// Create a reactive previewContent object with the correct structure
const previewContentRef = computed(() => ({
  title: props.previewContent.title || '',
  content: props.previewContent.content || []
}));

// Provide the previewContent to child components
provide('previewContent', previewContentRef);
</script>

<template>
    <div class="flex h-full flex-col">
        <!-- Fixed toolbar -->
        <div class="mb-2 flex-shrink-0">
            <PreviewToolBar />
        </div>

        <!-- Scrollable preview content -->
        <div class="flex-grow overflow-hidden rounded-lg bg-gray-50 shadow-lg">
            <div class="relative h-full">
                <h1
                    class="absolute left-2 top-1 text-[16px] font-bold italic text-gray-400"
                >
                    Preview
                </h1>
                <!-- Preview content -->
                <div class="h-full overflow-y-auto scrollbar-thin p-8 pt-10">
                    <div v-if="previewContentRef.content[0]" class="prose max-w-none" v-html="previewContentRef.content[0]"></div>
                    <div v-if="previewContentRef.content[1]" class="mt-8">
                        <h2 class="text-xl font-bold mb-4">References</h2>
                        <div class="prose max-w-none" v-html="previewContentRef.content[1]"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Fixed word/character counter -->
        <div class="mt-2 flex-shrink-0">
            <WordAndCharacterCount
                :character-limit="12000"
                :character-count="store.charCount"
                :word-count="store.wordCount"
                :hide-bar="true"
                :hide-character-count="true"
            />
        </div>
    </div>
</template>

<style scoped>
.prose {
    font-size: 1rem;
    line-height: 1.75;
}
</style>
