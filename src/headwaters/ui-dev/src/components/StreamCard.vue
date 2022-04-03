<script>
import { mapStores } from "pinia";
import { useEngineStore } from "../stores/streamStore.js";

export default {
  data() {
    return {
      streamName: "fruits",
    };
  },
  methods: {
    start() {
      console.log("start button pressed");
      this.streamStore.startStream(this.streamName);
    },
    stop() {
      console.log("stop button pressed");
      this.streamStore.stopStream(this.streamName);
    },
  },
  computed: {
    ...mapStores(useEngineStore),
  },
  created() {
    this.streamStore.getStreamStatus(this.streamName);
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
      <button
        class="
          pt-1
          pb-1
          pl-2
          pr-2
          rounded-md
          h-8
          w-24
          sm:w-12
          ml-2
          text-sm
          transition
          duration-75
          ease-in-out
          border border-gray-500
        "
      >
        <div
          v-on:click="start()"
          v-if="this.streamStore.stream.running === false"
        >
          start
        </div>
        <div
          v-on:click="stop()"
          v-if="this.streamStore.stream.running === true"
        >
          stop
        </div>
      </button>
    </div>
  </div>
</template>



