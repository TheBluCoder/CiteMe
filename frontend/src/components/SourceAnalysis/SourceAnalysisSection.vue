<script setup>
import { Shield } from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps({
    sourceType: {
        type: String,
        required: true,
    },
    sourceCredibility: {
        type: Number,
        required: true,
    },
    sourceCount: {
        type: Number,
        required: true,
    },
    status: {
        type: String,
        required: true,
    },
})

const credibilityColor = computed(() => {
    if (props.sourceCredibility >= 90) return 'text-green-500'
    if (props.sourceCredibility >= 70) return 'text-yellow-500'
    return 'text-red-500'
})

const statusColor = computed(() => {
    return props.status === 'verified'
        ? 'bg-green-100 text-green-600'
        : 'bg-yellow-100 text-yellow-600'
})
</script>

<template>
    <div
        class="rounded-lg border border-gray-300 p-3 hover:border-gray-400/80 hover:border-2 transition-colors duration-400 hover:shadow-md"
    >
        <div class="mb-2 flex items-center justify-between">
            <div class="flex items-center space-x-2">
                <Shield :class="['h-4 w-4', credibilityColor]" />
                <span class="font-medium"> {{ sourceType }} Sources </span>
            </div>
            <span :class="['rounded-full px-2 py-1 text-sm', statusColor]">
                {{ status }}
            </span>
        </div>
        <div class="flex items-center justify-between text-sm text-gray-500">
            <span>Credibility: {{ sourceCredibility }}%</span>
            <span>{{ sourceCount }} matches</span>
        </div>
    </div>
</template>
