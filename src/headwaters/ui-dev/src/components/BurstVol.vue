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
    setBurstVol(newBurstVol) {
      this.streamStore.setBurstVol(this.streamName, newBurstVol);
    },
  },
};
</script>

<template>
  <div class="flex flex-row items-center">
    <button
      class="btn-increment"
      v-on:click="setBurstVol(this.streamStore.stream.burst_vol - 10)"
    >
      -
    </button>
    <div class="pl-2 w-16 text-center">
      {{ this.streamStore.stream.burst_vol }}
      <span class="text-xs">events</span>
    </div>
    <button
      class="btn-increment"
      v-on:click="setBurstVol(this.streamStore.stream.burst_vol + 10)"
    >
      +
    </button>
  </div>
</template>