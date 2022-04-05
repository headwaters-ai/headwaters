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
    setBurstFreq(newBurstFreq) {
      this.streamStore.setBurstFreq(this.streamName, newBurstFreq);
    },
  },
};
</script>

<template>
  <div class="flex flex-row items-center">
    <button
      class="btn-increment"
      v-on:click="setBurstFreq(this.streamStore.stream.burst_freq - 50)"
    >
      -
    </button>
    <div class="pl-2 w-16 text-center">
      {{ this.streamStore.stream.burst_freq }}ms
    </div>
    <button
      class="btn-increment"
      v-on:click="setBurstFreq(this.streamStore.stream.burst_freq + 50)"
    >
      +
    </button>
  </div>
</template>