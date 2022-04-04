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
    setFreq(newFreq) {
      this.streamStore.setStreamFreq(this.streamName, newFreq);
    },
  },
};
</script>

<template>
  <div class="flex flex-row items-center">
    <button
      class="btn-increment"
      v-on:click="setFreq(this.streamStore.stream.stream_freq - 100)"
    >
      -
    </button>
    <div class="pl-2 w-16 text-center">
      {{ this.streamStore.stream.stream_freq }}ms
    </div>
    <button
      class="btn-increment"
      v-on:click="setFreq(this.streamStore.stream.stream_freq + 100)"
    >
      +
    </button>
  </div>
</template>


