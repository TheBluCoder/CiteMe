<script setup>
import { Search, AlertTriangle, Clock } from 'lucide-vue-next';

defineProps({
    sources: {
        type: Array,
        required: true,
        default: () => [],
    }
});
</script>

<template>
    <div class="relative rounded-lg border border-gray-300 p-4 hover:border-gray-400/80 hover:border-2 transition-colors duration-300 hover:shadow-md">
        <!-- Coming Soon Overlay -->
        <div class="absolute inset-0 z-10 backdrop-blur-[2px] bg-white/30 rounded-lg flex items-center justify-center group cursor-not-allowed">
            <div class="flex items-center gap-2 px-3 py-2 bg-gray-900/80 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <Clock class="h-4 w-4" />
                <span class="text-sm font-medium">Coming Soon</span>
            </div>
        </div>

        <div class="mb-4 flex items-center justify-between">
            <div class="flex items-center space-x-2">
                <Search class="h-5 w-5 text-blue-500" />
                <h3 class="font-medium">Citation Suggestions</h3>
            </div>
            <button class="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-600">
                Analyze
            </button>
        </div>

        <div class="space-y-3">
            <div class="flex items-start space-x-3 rounded-lg bg-yellow-50 p-3">
                <AlertTriangle class="h-5 w-5 text-yellow-500" />
                <div>
                    <p class="text-sm text-yellow-700">
                        This paragraph may need citation. We found {{ sources.length }} potential sources.
                    </p>
                    <button class="mt-2 text-sm font-medium text-blue-600">
                        View suggestions
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
