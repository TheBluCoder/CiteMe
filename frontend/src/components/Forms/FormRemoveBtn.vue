<template>
  <button
      type="button"
      class="block rounded-md px-2 py-1 text-center text-sm backdrop-blur-sm"
      :disabled="disableRemoveBtn"
      @click="$emit('remove')"
  >
      <span
          :class="{
              'text-red-500': true,
              'text-red-500/60': disableRemoveBtn,
          }"
          >remove</span
      >
  </button>
</template>

<script setup>
defineProps({
  disableRemoveBtn: Boolean,
});
defineEmits(['remove']);
</script>