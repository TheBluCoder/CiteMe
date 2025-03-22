<script setup>
import { X } from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps({
    show: {
        type: Boolean,
        required: true,
    },
    activeSourceType: {
        type: String,
        required: false,
        default: null,
    },
    sources: {
        type: Array,
        required: true,
        default: () => [],
    },
})

const getSourceTypeTitle = computed(() => {
    switch (props.activeSourceType) {
        case 'academic':
            return 'Academic'
        case 'web':
            return 'Web'
        case 'others':
            return 'Others'
        default:
            return ''
    }
})

defineEmits(['close'])

function getCredibilityClass(score) {
    if (!score) return 'neutral'
    if (score >= 90) return 'excellent'
    if (score >= 70) return 'good'
    if (score >= 50) return 'fair'
    return 'poor'
}
</script>

<template>
    <div class="fixed top-0 right-0 h-screen w-[450px] bg-gradient-to-br from-[#f8faff] to-white shadow-[-8px_0_20px_rgba(0,0,0,0.1)] transform transition-all duration-400 ease-in-out z-50 border-l border-indigo-100/10 [-ms-overflow-style:none] [scrollbar-width:none]" :class="{ 'translate-x-0': show, 'translate-x-full': !show }">
        <div class="flex justify-between items-center p-4 bg-white/90 backdrop-blur border-b border-indigo-100/10 sticky top-0 z-10">
            <h3
                class="text-lg font-semibold"
                :class="{
                    'text-green-600': activeSourceType === 'web',
                    'text-blue-600': activeSourceType === 'others',
                    'text-purple-600': activeSourceType === 'academic',
                }"
            >
                {{ getSourceTypeTitle }} Sources
            </h3>
            <button @click="$emit('close')" class="p-2 rounded-lg transition-all duration-200 bg-white border border-indigo-100/10 hover:bg-gray-50 hover:scale-105">
                <X class="h-5 w-5 text-gray-500" />
            </button>
        </div>

        <div class="p-4 h-[calc(100vh-4rem)] overflow-y-auto [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            <div v-if="sources.length === 0" class="flex justify-center items-center h-48 bg-white/50 rounded-2xl border-2 border-dashed border-indigo-100/20">
                <p class="text-gray-500">No sources available</p>
            </div>
            <div v-else class="space-y-3">
                <div v-for="source in sources" :key="source.url" class="p-4 bg-white border border-indigo-100/10 rounded-2xl transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-indigo-100/30 hover:border-indigo-300/30">
                    <div class="font-semibold mb-2 break-words" :class="{
                        'text-green-900': activeSourceType === 'web',
                        'text-blue-900': activeSourceType === 'others',
                        'text-purple-900': activeSourceType === 'academic'
                    }">{{ source.title }}</div>
                    <a :href="source.url" target="_blank" class="block text-sm p-2 rounded-lg mb-3 break-all transition-colors duration-200" :class="{
                        'text-green-500 bg-green-50/50 hover:bg-green-50': activeSourceType === 'web',
                        'text-blue-500 bg-blue-50/50 hover:bg-blue-50': activeSourceType === 'others',
                        'text-purple-500 bg-purple-50/50 hover:bg-purple-50': activeSourceType === 'academic'
                    }">
                        {{ source.url }}
                    </a>
                    <div class="flex items-center gap-3">
                        <div
                            class="text-sm px-3 py-1 rounded-full font-medium"
                            :class="{
                                'bg-green-100/80 text-green-700': getCredibilityClass(source.credibility_score) === 'excellent',
                                'bg-yellow-100/80 text-yellow-700': getCredibilityClass(source.credibility_score) === 'good',
                                'bg-orange-100/80 text-orange-700': getCredibilityClass(source.credibility_score) === 'fair',
                                'bg-red-100/80 text-red-700': getCredibilityClass(source.credibility_score) === 'poor',
                                'bg-gray-100/80 text-gray-700': getCredibilityClass(source.credibility_score) === 'neutral'
                            }"
                        >
                            Score: {{ source.credibility_score || 'N/A' }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style>
@layer utilities {
    .scrollbar-hide {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
    .scrollbar-hide::-webkit-scrollbar {
        display: none;
    }
}
</style>
