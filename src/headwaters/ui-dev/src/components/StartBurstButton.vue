<script>
import { mapStores } from "pinia";
import { useStreamStore } from "../stores/streamStore.js";

export default {
  props: {
    streamName: String,
  },
  computed: {
    ...mapStores(useStreamStore),
  },
  methods: {
    startBurst() {
      this.streamStore.startBurst(this.streamName);
    },
  },
};
</script>

<template>
  <div class="flex flex-row items-center">
    <button
      class="btn-primary"
      v-on:click="startBurst()"
    >
      burst
    </button>
    
  </div>
</template>