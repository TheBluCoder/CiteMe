<script setup>
import { ref } from 'vue';
import { ChevronDown } from 'lucide-vue-next';

const citationStyle = defineModel('citationStyle', {
    required: true,
    default: 'APA',
});

const isOpen = ref(false);
const citationFormats = [
    {
        id: 'apa',
        name: 'APA',
        description: 'American Psychological Association',
    },
    { id: 'mla', name: 'MLA', description: 'Modern Language Association' },
    {
        id: 'ieee',
        name: 'IEEE',
        description: 'Institute of Electrical and Electronics Engineers',
    },
    { id: 'chicago', name: 'Chicago', description: 'Chicago Manual of Style' },
];

const selectFormat = (format) => {
    citationStyle.value = format;
    isOpen.value = false;
};
</script>

<template>
    <div class="relative">
        <button
            @click="isOpen = !isOpen"
            class="flex items-center gap-2 rounded-lg border border-gray-200 px-4 py-2 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
            :class="{
                'bg-blue-500 text-sm font-semibold text-white/80 hover:bg-blue-600':
                    !isOpen,
                'border-2 border-blue-500 text-gray-400 hover:bg-gray-100':
                    isOpen,
            }"
        >
            <span class="hidden md:block">Citation Format</span>
            <span> {{ citationStyle }}</span>
            <ChevronDown class="h-4 w-4 text-white/80" />
        </button>

        <Transition name="fade">
            <div
                v-if="isOpen"
                class="absolute bottom-full right-0 z-10 mt-2 w-60 rounded-lg border border-gray-200 bg-white shadow-lg md:bottom-auto md:mt-2"
            >
                <button
                    v-for="format in citationFormats"
                    :key="format.id"
                    @click="selectFormat(format.name)"
                    class="group w-full px-4 py-3 text-left transition-colors duration-300 first:rounded-t-lg last:rounded-b-lg hover:bg-blue-200 focus:bg-gray-50 focus:outline-none"
                >
                    <span class="block text-sm font-medium text-gray-800">{{
                        format.name
                    }}</span>
                    <span
                        class="text-xs text-gray-500 group-hover:text-green-600"
                        >{{ format.description }}</span
                    >
                </button>
            </div>
        </Transition>
    </div>
</template>

<style scoped></style>