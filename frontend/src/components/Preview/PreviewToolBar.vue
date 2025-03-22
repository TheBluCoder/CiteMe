<script setup>
import PreviewButton from '@/components/Preview/PreviewButton.vue';
import { usePreviewToolBar } from '@/stores/usePreviewToolBar.js';

const { PreviewToolBarConstants } = usePreviewToolBar();
</script>

<template>
    <div
        class="my-4 flex items-center justify-center gap-2 rounded-lg bg-transparent p-2"
    >
        <div class="flex justify-center gap-2">
            <PreviewButton
                v-for="tool in PreviewToolBarConstants"
                :key="tool.text"
                @click="tool.action"
                :icon="tool.icon"
            >
                {{ tool.text }}
            </PreviewButton>
        </div>
    </div>
</template>

<style scoped></style>
