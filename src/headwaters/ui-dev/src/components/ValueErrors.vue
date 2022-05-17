<script>
import { mapStores } from "pinia";
import { useSourceStore } from "../stores/sourceStore.js";

export default {
  props: {
    streamName: String,
  },
  computed: {
    ...mapStores(useSourceStore),
  },
  created() {
    this.sourceStore.getSingleSourceStatus(this.streamName);
  },
  methods: {
    setValueErrorsToggle(streamName, ValueErrorBool) {
      this.sourceStore.setValueErrorsToggle(streamName, ValueErrorBool);
    },
  },
};
</script>

<template>
  <div class="flex flex-row items-center">
    <div>{{this.sourceStore.source.error_mode.value_error_prob}}</div>
    <div>Off</div>
    <button
      class="btn-increment"
      v-on:click="setValueErrorsToggle(this.streamName, true)"
    >
      on
    </button>
    <button
      class="btn-increment"
      v-on:click="setValueErrorsToggle(this.streamName, false)"
    >
      off
    </button>
  </div>
</template>