
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
    start() {
      this.streamStore.startStream(this.streamName);
    },
    stop() {
      this.streamStore.stopStream(this.streamName);
    },
  },
};
</script>

<template>
  <div>
    <button class="btn-primary">
      <div
        v-on:click="start()"
        v-if="this.streamStore.stream.running === false"
      >
        start
      </div>
      <div v-on:click="stop()" v-if="this.streamStore.stream.running === true">
        stop
      </div>
    </button>
  </div>
</template>
