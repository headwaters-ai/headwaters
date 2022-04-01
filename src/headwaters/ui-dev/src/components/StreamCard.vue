<template>
  <div
    class="
      mx-auto
      m-2
      p-2
      relative
      shadow-xl
      cursor-pointer
      bg-gray-100
      border border-red-500
      w-11/12
      h-40
      rounded-md
    "
  >
    <div class="text-2xl font-bold text-sky-300">
      stream "{{ this.engineStore.stream.stream_name }}"
    </div>
    <button
      class="
        pt-1
        pb-1
        pl-2
        pr-2
        rounded-md
        h-12
        w-24
        sm:w-12
        ml-2
        text-sm
        transition
        duration-75
        ease-in-out
        border
        border-blue-100
      "
      v-on:click="ping()"
    >
      ping!
    </button>
    <button
      class="
        pt-1
        pb-1
        pl-2
        pr-2
        rounded-md
        h-12
        w-24
        sm:w-12
        ml-2
        text-sm
        transition
        duration-75
        ease-in-out
        border
        border-blue-100
      "
      v-on:click="start()"
      v-if="this.engineStore.stream.running === false"
    >
      start
    </button>
    <button
      class="
        pt-1
        pb-1
        pl-2
        pr-2
        rounded-md
        h-12
        w-24
        sm:w-12
        ml-2
        text-sm
        transition
        duration-75
        ease-in-out
        border
        border-blue-100
      "
      v-on:click="stop()"
      v-if="this.engineStore.stream.running === true"
    >
      stop
    </button>
    <div v-if="this.pongStore.pong"> {{this.pongStore.pong}} </div>
    <div v-if="this.engineStore.stream"> {{this.engineStore.stream}} </div>
  </div>
</template>

<script>
import { mapStores } from 'pinia'
import { usePongStore } from "../stores/pongStore.js"
import { useEngineStore } from "../stores/engineStore.js"


export default {
  data() {
    return {
      streamName: "fruits",
    };
  },
  methods: {
    ping() {
      console.log("ping button pressed")
      this.pongStore.getPong()
    },
    start() {
      console.log("start button pressed")
      this.engineStore.startStream(this.streamName)
    },
    stop() {
      console.log("stop button pressed")
      this.engineStore.stopStream(this.streamName)
    }
  },
  computed: {
    ...mapStores(usePongStore, useEngineStore)
  },
  created() {
    this.engineStore.getStreamStatus(this.streamName)
    this.pongStore.getPong()
    console.log(this.streamName)
  }
};
</script>

