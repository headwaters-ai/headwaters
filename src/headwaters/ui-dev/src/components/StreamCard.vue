<script>
import { mapStores } from "pinia";
import { useEngineStore } from "../stores/engineStore.js";

export default {
  data() {
    return {
      streamName: "fruits",
    };
  },
  methods: {
    start() {
      console.log("start button pressed");
      this.engineStore.startStream(this.streamName);
    },
    stop() {
      console.log("stop button pressed");
      this.engineStore.stopStream(this.streamName);
    },
  },
  computed: {
    ...mapStores(useEngineStore),
  },
  created() {
    this.engineStore.getStreamStatus(this.streamName);
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
      <div v-if="this.engineStore.stream">
        <b>running:</b> {{ this.engineStore.stream.running }}
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
          v-if="this.engineStore.stream.running === false"
        >
          start
        </div>
        <div
          v-on:click="stop()"
          v-if="this.engineStore.stream.running === true"
        >
          stop
        </div>
      </button>
    </div>
  </div>
</template>



