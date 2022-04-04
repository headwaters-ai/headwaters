<script>
import { mapStores } from "pinia";
import { useStreamStore } from "../stores/streamStore.js";
import StreamFreq from "../components/StreamFreq.vue";
import StreamStartStop from "../components/StreamStartStop.vue";

export default {
  data() {
    return {
      streamName: "fruits",
    };
  },
  computed: {
    ...mapStores(useStreamStore),
  },
  created() {
    this.streamStore.getStreamStatus(this.streamName);
  },
  components: {
    StreamFreq,
    StreamStartStop,
  },
};
</script>

<template>
  <div
    class="
      m-2
      p-2
      text-sm
      relative
      shadow-xl
      bg-gray-100
      border border-gray-300
      w-auto
      h-20
      rounded-md
      flex flex-col
      justify-center
    "
  >
    <div class="flex flex-row justify-between">
      <div><b>stream:</b> {{ this.streamName }}</div>
      <div v-if="this.streamStore.stream">
        <b>running:</b> {{ this.streamStore.stream.running }}
      </div>
      <StreamStartStop v-bind:streamName="this.streamName" />
    </div>
    <StreamFreq v-bind:streamName="this.streamName" />
  </div>
</template>



