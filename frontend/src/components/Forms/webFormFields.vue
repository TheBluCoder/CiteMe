<template>
  <div class="mb-4 flex flex-wrap justify-between gap-2">
      <label class="text-sm font-medium text-gray-700 lg:flex-shrink-0"
          >Authors <span class="text-red-500">*</span>

          <input
              name="authors"
              class="ml-1 rounded-md border-indigo-200 bg-white/50 py-1 pl-2 pr-8 text-sm backdrop-blur-sm focus:border-indigo-500 focus:ring-indigo-500"
              type="text"
              :value="source.authors"
              @input="$emit('update:authors', $event.target.value)"
              placeholder="John Doe, Jane Doe et al"
              required
              maxlength="30"
          />
      </label>

      <label class="text-sm font-medium text-gray-700 lg:flex-shrink-0"
          >Title <span class="text-red-500">*</span>

          <input
              name="Title"
              class="ml-1 rounded-md border-indigo-200 bg-white/50 py-1 pl-2 pr-8 text-sm backdrop-blur-sm focus:border-indigo-500 focus:ring-indigo-500"
              type="text"
              :value="source.title"
              @input="$emit('update:title', $event.target.value)"
              placeholder="Journal of Big data"
              maxlength="30"
          />
      </label>

      <label class="text-sm font-medium text-gray-700 lg:flex-shrink-0"
          >Type <span class="text-red-500">*</span>
          <input
              name="type"
              class="ml-5 rounded-md border-indigo-200 bg-white/50 py-1 pl-2 pr-8 text-sm backdrop-blur-sm focus:border-indigo-500 focus:ring-indigo-500"
              type="text"
              :value="source.sourceType"
              @input="$emit('update:type', $event.target.value)"
              placeholder="e.g. article, website "
              required
              maxlength="30"
          />
      </label>

      <label class="text-sm font-medium text-gray-700 lg:flex-shrink-0"
          >Publication Date <span class="text-red-500">*</span>

          <input
              name="dates"
              class="ml-1 w-[12rem] rounded-md border-indigo-200 bg-white/50 py-1 pl-2 pr-8 text-sm backdrop-blur-sm focus:border-indigo-500 focus:ring-indigo-500"
              type="date"
              :value="source.publishedDate"
              @input="$emit('update:publishedDate', $event.target.value)"
          />
      </label>

      <label class="text-sm font-medium text-gray-700 lg:flex-shrink-0"
          >DOI

          <input
              name="doi"
              class="ml-9 w-[12rem] rounded-md border-indigo-200 bg-white/50 py-1 pl-2 pr-8 text-sm backdrop-blur-sm focus:border-indigo-500 focus:ring-indigo-500"
              type="text"
              :value="source.doi"
              @input="$emit('update:doi', $event.target.value)"
              placeholder="10.1186/s40537-021-00553-4"
              maxlength="30"
          />
      </label>

      <label class="text-sm font-medium text-gray-700 lg:flex-shrink-0"
          >volume

          <input
              name="doi"
              class="ml-1 w-[12rem] rounded-md border-indigo-200 bg-white/50 py-1 pl-2 pr-8 text-sm backdrop-blur-sm focus:border-indigo-500 focus:ring-indigo-500"
              type="number"
              :value="source.volume"
              @input="$emit('update:volume', $event.target.value)"
              placeholder="1"
              maxlength="30"
          />
      </label>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

defineProps({
  source: Object,
});

defineEmits([
  'update:authors',
  'update:title',
  'update:type',
  'update:publishedDate',
  'update:doi',
  'update:volume',
]);
</script>

<style scoped></style>
