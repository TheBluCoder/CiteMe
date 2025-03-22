<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed, defineOptions } from 'vue'
import { EditorContent } from '@tiptap/vue-3';
import EditorToolbar from '@/components/Editor/EditorToolbar.vue';
import WordAndCharacterCount from '@/components/Editor/WordAndCharacterCount.vue';
import { useEditorConfig } from '../components/Editor/EditorConfig.js';
defineOptions({ name: 'editorComponent' });
const selectedHeading = ref('paragraph');

const content = defineModel('editorContent');
const { wordCount, characterCount, editor, characterLimit } = useEditorConfig();
onMounted(() => {
    const savedContent = localStorage.getItem('editorContent');
    if (savedContent) {
        editor.value?.commands.setContent(savedContent);
    }
    editor.value?.commands.focus();
});

onBeforeUnmount(() => {
    const currentContent = editor.value?.getHTML();
    if (currentContent) {
        localStorage.setItem('editorContent', currentContent);
    }
    editor.value?.destroy();
});

watch(
    () => editor.value?.getHTML(),
    (newContent) => {
        if (newContent) {
            content.value = newContent;
        }
    },
);
watch(content, (newContent) => {
    console.log('content_', newContent);
    if (!newContent) {
        localStorage.removeItem('editorContent');
    }
    if (editor.value?.getHTML() !== newContent) {
        editor.value?.commands.setContent(newContent);
    }
});
console.log("within the editor component")
let get_content_v= computed(() => content).value;
console.log("get_content_v", get_content_v);
</script>

<template>
    <!-- Editor with fixed toolbar and counter, scrollable content -->
    <div class="flex h-full flex-col">
        <!-- Fixed toolbar -->
        <div class="mb-2 flex-shrink-0">
            <div class="flex items-center justify-between gap-x-4">
                <EditorToolbar
                    v-if="editor"
                    v-model="selectedHeading"
                    :editor="editor"
                    class="flex-grow"
                />
            </div>
        </div>

        <!-- Scrollable editor content -->
      <keep-alive>
        <div
            class="scrollbar-thin flex-grow overflow-y-auto rounded-lg bg-white/80 shadow-lg backdrop-blur-sm"
        >
            <editor-content
                :editor="editor"
                class="h-full p-4 focus:outline-none"
            />
        </div>
      </keep-alive>

        <!-- Fixed word/character counter -->
        <div class="mt-2 flex-shrink-0">
            <WordAndCharacterCount
                :word-count="wordCount"
                :character-count="characterCount"
                :character-limit="characterLimit"
            />
        </div>
    </div>
</template>

<style >
@reference "@/assets/main.css";

.ProseMirror {
    @apply min-h-full;
}

.ProseMirror p.is-editor-empty:first-child::before {
    content: attr(data-placeholder);
    float: left;
    color: #64748b;
    pointer-events: none;
    height: 0;
}

/* Custom styling for the editor content */
.ProseMirror {
    @apply text-gray-800;
    outline: none !important;
}

.ProseMirror p {
    @apply mb-4 leading-relaxed;
}

/* Heading styles */
.ProseMirror h1 {
    @apply text-3xl font-bold mb-4 text-gray-900;
}

.ProseMirror h2 {
    @apply text-2xl font-bold mb-3 text-gray-900;
}
</style>
