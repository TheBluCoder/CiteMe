<script setup>
defineProps({
    disableAddBtn: Boolean,
});
defineEmits(['add']);
</script>

<template>
    <button
        type="button"
        class="block rounded-md px-2 py-1 text-center text-sm backdrop-blur-sm"
        :disabled="disableAddBtn"
        @click="$emit('add')"
    >
        <span
            :class="{
                'text-green-600': true,
                'text-green-500/60': disableAddBtn,
            }"
            >add</span
        >
    </button>
</template>

<style scoped></style>