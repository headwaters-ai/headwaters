<script>
import { mapStores } from "pinia";
import { useStreamStore } from "../stores/streamStore.js";
import StreamFreq from "../components/StreamFreq.vue";
import BurstFreq from "../components/BurstFreq.vue";
import BurstVol from "../components/BurstVol.vue";
import StartBurstButton from "../components/StartBurstButton.vue";
import FlashMsgBar from "../components/FlashMsgBar.vue";
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
    BurstFreq,
    BurstVol,
    StartBurstButton,
    FlashMsgBar,
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
      h-auto
      rounded-md
      flex flex-col
      justify-center
    "
  >
    <div class="flex flex-row justify-between">
      <div><b>stream:</b> {{ this.streamName }}</div>
      <div v-if="this.streamStore.stream">
        <div v-if="this.streamStore.stream.running">
          <div class="text-green-500 font-bold">running</div>
        </div>
        <div v-else>
          <div class="text-orange-500 font-bold">not running</div>
        </div>
      </div>

      <StreamStartStop v-bind:streamName="this.streamName" />
    </div>
    <div class="flex flex-row m-1 items-center">
      <span class="font-bold w-11">Freq:</span>
      <StreamFreq v-bind:streamName="this.streamName" />
    </div>
    <div class="flex flex-row m-1 items-center">
      <span class="font-bold w-11">Burst:</span>
      <BurstFreq v-bind:streamName="this.streamName" />
      <BurstVol v-bind:streamName="this.streamName" />
      <StartBurstButton :streamName="this.streamName" />
    </div>

    <div class="absolute top-0 left-0 w-full">
      <div
        v-if="this.streamStore.messages"
        class="flex flex-col items-start transition duration-500 ease-in-out"
      >
        <FlashMsgBar
          v-for="message in this.streamStore.messages"
          :key="message"
          :message="message"
          class="transition duration-500 ease-in-out"
        />
      </div>
    </div>
  </div>
</template>



