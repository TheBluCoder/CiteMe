<script setup>
import { Shield } from 'lucide-vue-next';
import { computed } from 'vue';

const props = defineProps({
    sources: {
        type: Array,
        required: true,
        default: () => [],
    },
    academicSources: {
        type: Array,
        required: true,
        default: () => [],
    },
    webSources: {
        type: Array,
        required: true,
        default: () => [],
    },
    otherSources: {
        type: Array,
        required: true,
        default: () => [],
    }
});

const academicSourceCredibility = computed(() => {
    if (!props.academicSources.length) return 0;
    return props.academicSources.reduce((acc, source) => acc + (source.credibility_score || 0), 0) / props.academicSources.length;
});

const webSourceCredibility = computed(() => {
    if (!props.webSources.length) return 0;
    return props.webSources.reduce((acc, source) => acc + (source.credibility_score || 0), 0) / props.webSources.length;
});

const otherSourceCredibility = computed(() => {
    if (!props.otherSources.length) return 0;
    return props.otherSources.reduce((acc, source) => acc + (source.credibility_score || 0), 0) / props.otherSources.length;
});

const getCredibilityColor = (score) => {
    if (score >= 90) return 'text-green-500';
    if (score >= 70) return 'text-yellow-500';
    return 'text-red-500';
};

const emit = defineEmits(['openSourceDetails']);

const categoryStyles = {
    academic: {
        border: 'border-purple-200',
        background: 'bg-indigo-50/50',
        text: 'text-indigo-900',
        hover: 'hover:border-indigo-400 hover:bg-indigo-50'
    },
    web: {
        border: 'border-green-200',
        background: 'bg-green-50/50',
        text: 'text-green-900',
        hover: 'hover:border-green-400 hover:bg-green-50'
    },
    other: {
        border: 'border-blue-200',
        background: 'bg-blue-50/50',
        text: 'text-blue-900',
        hover: 'hover:border-blue-400 hover:bg-blue-50'
    }
};
</script>

<template>
    <div class="mb-6">
        <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-semibold text-gray-900">Source Analysis</h2>
            <span class="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-sm text-blue-600 font-medium">
                {{ sources.length }}
            </span>
        </div>

        <div class="space-y-6">
            <!-- Academic Sources -->
            <div
                class="source-card"
                :class="[
                    categoryStyles.academic.border,
                    categoryStyles.academic.background,
                    categoryStyles.academic.hover
                ]"
                @click="emit('openSourceDetails', 'academic')"
            >
                <div class="mb-3 flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                        <Shield
                            :class="['h-5 w-5', getCredibilityColor(academicSourceCredibility)]"
                        />
                        <span class="font-semibold" :class="categoryStyles.academic.text">
                            Academic Sources
                        </span>
                    </div>
                    <span
                        :class="[
                            'status-badge',
                            academicSources.length > 0
                                ? 'bg-indigo-100 text-indigo-700'
                                : 'bg-yellow-100 text-yellow-700',
                        ]"
                    >
                        {{ academicSources.length > 0 ? 'verified' : 'unverified' }}
                    </span>
                </div>
                <div class="flex items-center justify-between text-sm">
                    <span :class="categoryStyles.academic.text">
                        Credibility: {{ academicSourceCredibility.toFixed(1) }}%
                    </span>
                    <span class="font-medium text-indigo-600">
                        {{ academicSources.length }} matches
                    </span>
                </div>
            </div>

            <!-- Web Sources -->
            <div
                class="source-card"
                :class="[
                    categoryStyles.web.border,
                    categoryStyles.web.background,
                    categoryStyles.web.hover
                ]"
                @click="emit('openSourceDetails', 'web')"
            >
                <div class="mb-3 flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                        <Shield
                            :class="['h-5 w-5', getCredibilityColor(webSourceCredibility)]"
                        />
                        <span class="font-semibold" :class="categoryStyles.web.text">
                            Web Sources
                        </span>
                    </div>
                    <span
                        :class="[
                            'status-badge',
                            webSources.length > 0
                                ? 'bg-blue-100 text-blue-700'
                                : 'bg-yellow-100 text-yellow-700',
                        ]"
                    >
                        {{ webSources.length > 0 ? 'verified' : 'unverified' }}
                    </span>
                </div>
                <div class="flex items-center justify-between text-sm">
                    <span :class="categoryStyles.web.text">
                        Credibility: {{ webSourceCredibility.toFixed(1) }}%
                    </span>
                    <span class="font-medium text-green-600">
                        {{ webSources.length }} matches
                    </span>
                </div>
            </div>

            <!-- Other Sources -->
            <div
                class="source-card"
                :class="[
                    categoryStyles.other.border,
                    categoryStyles.other.background,
                    categoryStyles.other.hover
                ]"
                @click="emit('openSourceDetails', 'others')"
            >
                <div class="mb-3 flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                        <Shield
                            :class="['h-5 w-5', getCredibilityColor(otherSourceCredibility)]"
                        />
                        <span class="font-semibold" :class="categoryStyles.other.text">
                            Other Sources
                        </span>
                    </div>
                    <span
                        :class="[
                            'status-badge',
                            otherSources.length > 0
                                ? 'bg-emerald-100 text-emerald-700'
                                : 'bg-yellow-100 text-yellow-700',
                        ]"
                    >
                        {{ otherSources.length > 0 ? 'verified' : 'unverified' }}
                    </span>
                </div>
                <div class="flex items-center justify-between text-sm">
                    <span :class="categoryStyles.other.text">
                        Credibility: {{ otherSourceCredibility.toFixed(1) }}%
                    </span>
                    <span class="font-medium text-blue-600">
                        {{ otherSources.length }} matches
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
@reference "@/assets/main.css";
.source-card {
    @apply rounded-xl p-4 transition-all duration-300 cursor-pointer border shadow-sm;
    backdrop-filter: blur(8px);
}

.source-card:hover {
    @apply transform -translate-y-0.5 shadow-md;
}

.status-badge {
    @apply rounded-full px-3 py-1 text-sm font-medium;
}
</style>
