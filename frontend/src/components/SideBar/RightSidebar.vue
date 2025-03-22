<script setup>
import {
    BookOpen,
    ChevronRight,
    Shield,
} from 'lucide-vue-next';
import { computed, ref } from 'vue';
import SourceAnalysis from "@/components/SourceAnalysis/SourceAnalysis.vue";
import CitationSuggestions from "@/components/SourceAnalysis/CitationSuggestions.vue";
import SourceDetailsDrawer from '@/components/SourceAnalysis/SourceDetailsDrawer.vue';

const activeSourceType = ref(null);
const showSourceDetails = ref(false);

const openSourceDetails = (type) => {
    activeSourceType.value = type;
    showSourceDetails.value = true;
};

const closeSourceDetails = () => {
    showSourceDetails.value = false;
    activeSourceType.value = null;
};

const props = defineProps({
    credibilityScore: {
        type: Number,
        default: 0
    },
    sources: {
        type: Array,
        required: true,
        default: () => [],
    },
});

const academicSource = computed(() =>
    props.sources.filter(source =>
        ['peer reviewed', 'article'].includes(source.type?.trim().toLowerCase())
    )
);

const webSource = computed(() =>
    props.sources.filter(source =>
        ['website', 'blog'].includes(source.type?.trim().toLowerCase())
    )
);

const otherSource = computed(() =>
    props.sources.filter(source => {
        const type = source.type?.trim().toLowerCase();
        return !['peer reviewed', 'article', 'website', 'blog'].includes(type);
    })
);

const getSourcesByType = computed(() => ({
    academic: academicSource.value,
    web: webSource.value,
    other: otherSource.value
}));

const getCredibilityColor = (score) => {
    if (score >= 90) return 'text-green-500';
    if (score >= 70) return 'text-yellow-500';
    return 'text-red-500';
};

defineEmits(['close']);
</script>

<template>
    <div class="h-screen">
        <div class="h-full w-full border-r border-indigo-100 bg-white/80 backdrop-blur-sm md:w-80">
            <!-- Header -->
            <div
                class="flex items-center justify-between border-b border-indigo-100 bg-gradient-to-r from-indigo-50 to-blue-50 px-4 py-2"
            >
                <button
                    class="flex items-center space-x-2 font-medium text-indigo-900"
                >
                    <BookOpen class="h-5 w-5 text-indigo-600" />
                    <span>Citation Analysis</span>
                </button>
                <button
                    @click="$emit('close')"
                    class="rounded p-1 hover:bg-indigo-100"
                >
                    <ChevronRight class="h-5 w-5 text-indigo-600" />
                </button>
            </div>

            <!-- Content -->
            <div class="h-[calc(100%-3rem)] overflow-y-auto scrollbar-thin">
                <div class="p-4 space-y-6">
                    <!-- Source Credibility Score -->
                    <div class="p-4 rounded-xl border border-gray-200 drop-shadow-lg backdrop-blur-2xl!">
                        <div class="flex items-center justify-between mb-2">
                            <h3 class="text-lg font-semibold text-gray-900">Source Credibility Score</h3>
                            <Shield :class="['h-6 w-6', getCredibilityColor(credibilityScore)]" />
                        </div>
                        <div class="flex items-center justify-between">
                            <div class="text-3xl font-bold" :class="getCredibilityColor(credibilityScore)">
                                {{ credibilityScore < 1 ? (credibilityScore * 100).toFixed(1) : credibilityScore.toFixed(1) }}%
                            </div>
                            <span class="text-sm text-gray-600 font-medium">
                                {{ sources.length }} sources
                            </span>
                        </div>
                    </div>

                    <SourceAnalysis
                        :sources="sources"
                        :academic-sources="academicSource"
                        :web-sources="webSource"
                        :other-sources="otherSource"
                        @open-source-details="openSourceDetails"
                    />
                    <CitationSuggestions
                        :sources="sources"
                    />
                </div>
            </div>
        </div>

        <SourceDetailsDrawer
            :show="showSourceDetails"
            :active-source-type="activeSourceType"
            :sources="getSourcesByType[activeSourceType] || []"
            @close="closeSourceDetails"
        />
    </div>
</template>

<style scoped>
.source-drawer {
    position: fixed;
    top: 0;
    right: 0;
    height: 100vh;
    width: 400px;
    background: linear-gradient(to bottom, #f0f4ff, #ffffff);
    box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
    transform: translateX(100%);
    transition: transform 0.3s ease-in-out;
    z-index: 100;
    overflow-y: auto;
}

.source-drawer.open {
    transform: translateX(0);
}

.source-drawer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #e5e7eb;
}

.source-drawer-content {
    padding: 1rem;
    overflow-y: auto;
    height: calc(100% - 64px);
}

.source-item {
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    transition: all 0.2s ease;
}

.source-item:hover {
    border-color: #9ca3af;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.source-title {
    font-weight: 500;
    color: #1e40af;
    margin-bottom: 0.5rem;
}

.source-url {
    color: #3b82f6;
    text-decoration: underline;
    margin-bottom: 0.5rem;
    display: block;
}

.source-score {
    color: #4b5563;
    font-size: 0.875rem;
}

/* Update responsive styles */
@media (max-width: 768px) {
    .source-drawer {
        width: 100%;
    }
}

/* Add grid layout styles */
.grid {
    display: grid;
}

.grid-rows-[auto_1fr] {
    grid-template-rows: auto 1fr;
}

.grid-rows-[auto_1fr_auto] {
    grid-template-rows: auto 1fr auto;
}

.min-h-0 {
    min-height: 0;
}

.space-y-6 > * + * {
    margin-top: 1.5rem;
}
</style>
