<template>
  <div
      class="fixed left-0 top-0 z-50 h-screen w-screen place-content-center rounded-md py-2 bg-gray-600/50 backdrop-blur-[2px]"
  >
      <form
          class="scrollbar-thin mx-auto max-h-[80%] min-h-[200px] max-w-[90%] overflow-y-auto rounded-lg border bg-indigo-50 px-4 py-2 opacity-100 shadow-lg lg:max-w-[650px]"
          v-bind="$attrs"
      >
          <slot></slot>
      </form>
      <div class="my-4 flex justify-center gap-4">
          <button
              type="button"
              class="w-30 mb-2 block rounded-md border-indigo-200 bg-green-400 p-1 px-4 text-center backdrop-blur-sm focus:border-indigo-500 focus:ring-indigo-500"
              @click="$emit('save')"
          >
              Save
          </button>
          <button
              type="button"
              class="w-30 mb-2 block rounded-md border-indigo-200 bg-red-400 p-1 px-4 text-center backdrop-blur-sm focus:border-indigo-500 focus:ring-indigo-500"
              @click="$emit('discard')"
          >
              Discard
          </button>
      </div>
  </div>
</template>

<script setup>
defineOptions({ inheritAttrs: false });
defineEmits(['save', 'discard']);
</script>

<style scoped>
.bg-opacity {
  background-color: transparent;
}
</style>
