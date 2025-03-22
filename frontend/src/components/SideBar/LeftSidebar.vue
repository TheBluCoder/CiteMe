<script setup>
import {
    FileText,
    FilePlus,
    Upload,
    Download,
    Printer,
    History,
    Tags,
    ListTodo,
    Settings,
    BookOpen,
    X,
    FileJson,
    FileUp,
} from 'lucide-vue-next';

import { printContent, saveContent } from '@/stores/useDocumentActions.js';

const emit = defineEmits(['close']);
const props = defineProps({
    editorContent: {
        FormType: Object,
        required: true,
        default: () => ({
            title: '',
            content: '',
        }),
    },
});

const handleClose = () => {
    emit('close');
};

const handlePrint = () => {
    printContent(props.editorContent.title, props.editorContent.content);
};

const handleDownload = () => {
    saveContent(props.editorContent.title, props.editorContent.content);
};
</script>

<template>
    <div
        class="scrollbar-thin h-screen w-64 overflow-y-auto border-r border-indigo-100 bg-white/80 backdrop-blur-sm"
    >
        <div
            class="flex items-center justify-between border-b border-indigo-100 bg-gradient-to-r from-indigo-50 to-blue-50 px-4"
        >
            <button
                type="button"
                class="my-1 flex items-center space-x-2 font-medium text-indigo-900"
            >
                <FileText class="h-5 w-5 text-indigo-600" />
                <span>My Documents</span>
            </button>
            <button
                type="button"
                class="rounded p-1 hover:bg-indigo-100"
                @click="handleClose"
            >
                <X class="h-5 w-5 text-indigo-600" />
            </button>
        </div>

        <div class="flex flex-col gap-4">
            <div class="">
                <h2 class="m-2 text-xs font-semibold uppercase text-indigo-600">
                    DOCUMENT
                </h2>
                <div class="space-y-2">
                    <!-- New document -->
                    <button
                        type="button"
                        class="group flex w-full cursor-not-allowed items-center space-x-2 rounded-lg p-2 opacity-50"
                        title="Coming soon"
                    >
                        <FilePlus class="h-5 w-5 text-indigo-500" />
                        <span class="text-gray-700">New document</span>
                    </button>

                    <!-- Upload file -->
                    <button
                        class="group flex w-full cursor-not-allowed items-center space-x-2 rounded-lg p-2 opacity-50"
                        title="Coming soon"
                    >
                        <Upload class="h-5 w-5 text-indigo-500" />
                        <span class="text-gray-700">Upload file</span>
                        <span class="ml-auto text-xs text-indigo-400"
                            >.docx, .txt</span
                        >
                    </button>

                    <button
                        type="button"
                        class="group flex w-full items-center space-x-2 rounded-lg p-2 hover:bg-indigo-50"
                        @click="handleDownload"
                    >
                        <Download
                            class="h-5 w-5 text-indigo-500 group-hover:text-indigo-600"
                        />
                        <span class="text-gray-700 group-hover:text-indigo-900"
                            >Download</span
                        >
                        <span class="ml-auto text-xs text-indigo-400"
                            >as .docx</span
                        >
                    </button>
                    <button
                        type="button"
                        class="group flex w-full items-center space-x-2 rounded-lg p-2 hover:bg-indigo-50"
                        @click="handlePrint"
                    >
                        <Printer
                            class="h-5 w-5 text-indigo-500 group-hover:text-indigo-600"
                        />
                        <span class="text-gray-700 group-hover:text-indigo-900"
                            >Print</span
                        >
                        <span class="ml-auto text-xs text-indigo-400"
                            >Ctrl+P</span
                        >
                    </button>
                    <!-- Update version history button in document section -->
                    <button
                        type="button"
                        class="group flex w-full cursor-not-allowed items-center space-x-2 rounded-lg p-2 opacity-60 hover:bg-indigo-50"
                        title="Coming soon"
                    >
                        <History
                            class="h-5 w-5 text-indigo-500 group-hover:text-indigo-600"
                        />
                        <span class="text-gray-700 group-hover:text-indigo-900"
                            >Version history</span
                        >
                    </button>
                </div>
            </div>

            <div class="mb-6">
                <h2 class="m-2 text-xs font-semibold uppercase text-indigo-600">
                    RESEARCH TOOLS
                </h2>
                <div class="space-y-2">
                    <button
                        type="button"
                        class="group flex w-full cursor-not-allowed items-center space-x-2 rounded-lg p-2 opacity-60 hover:bg-indigo-50"
                        title="Coming soon"
                    >
                        <BookOpen
                            class="h-5 w-5 text-indigo-500 group-hover:text-indigo-600"
                        />
                        <span class="text-gray-700 group-hover:text-indigo-900"
                            >Bibliography Manager</span
                        >
                    </button>
                    <button
                        type="button"
                        class="group flex w-full cursor-not-allowed items-center space-x-2 rounded-lg p-2 opacity-60 hover:bg-indigo-50"
                        title="Coming soon"
                    >
                        <ListTodo
                            class="h-5 w-5 text-indigo-500 group-hover:text-indigo-600"
                        />
                        <span class="text-gray-700 group-hover:text-indigo-900"
                            >Research Notes</span
                        >
                    </button>
                    <button
                        type="button"
                        class="group flex w-full cursor-not-allowed items-center space-x-2 rounded-lg p-2 opacity-60 hover:bg-indigo-50"
                        title="Coming soon"
                    >
                        <Tags
                            class="h-5 w-5 text-indigo-500 group-hover:text-indigo-600"
                        />
                        <span class="text-gray-700 group-hover:text-indigo-900"
                            >Keywords Manager</span
                        >
                    </button>
                </div>
            </div>

            <div class="mb-6">
                <h2 class="m-2 text-xs font-semibold uppercase text-indigo-600">
                    SOURCES
                </h2>
                <div class="space-y-2">
                    <!-- Import source metadata -->
                    <button
                        class="group flex w-full cursor-not-allowed items-center space-x-2 rounded-lg p-2 opacity-50"
                        title="Coming soon"
                    >
                        <FileJson class="h-5 w-5 text-indigo-500" />
                        <span class="text-gray-700">Import source metadata</span>
                        <span class="ml-auto text-xs text-indigo-400">.json</span>
                    </button>

                    <!-- Upload source document -->
                    <button
                        type="button"
                        class="group flex w-full cursor-not-allowed items-center space-x-2 rounded-lg p-2 opacity-50"
                        title="Coming soon"
                    >
                        <FileUp class="h-5 w-5 text-indigo-500" />
                        <span class="whitespace-nowrap text-gray-700">Upload source document</span>
                        <span class="ml-auto text-xs text-indigo-400">.pdf, .docx</span>
                    </button>
                </div>
            </div>

            <div class="items-end">
                <!-- Editor settings -->
                <button
                    type="button"
                    class="group flex w-full cursor-not-allowed items-center space-x-2 rounded-lg p-2 opacity-50"
                    title="Coming soon"
                >
                    <Settings class="h-5 w-5 text-indigo-500" />
                    <span class="text-gray-700">Editor settings</span>
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
    transition: transform 0.3s ease-out;
}

.slide-enter-from,
.slide-leave-to {
    transform: translateX(-100%);
}
</style>
