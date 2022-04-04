import { defineStore } from 'pinia'
import requests from '../services/requests.js'

export const useStreamStore = defineStore({
  id: 'stream',
  state: () => ({
    stream: ''
  }),
  actions: {
    getStreamStatus(streamName) {
      return requests.getStreamStatus(streamName)
        .then(response => {
          this.stream = response.data
          console.log('stream state:', this.stream)
        })
        .catch(error => {
          console.log("issue getting stream status", error.response.data)
        })
    },
    startStream(streamName) {
      return requests.startStream(streamName)
        .then(response => {
          this.stream = response.data
        })
        .catch(error => {
          console.log("error issuing start command", error.response.data)
        })
    },
    stopStream(streamName) {
      return requests.stopStream(streamName)
        .then(response => {
          this.stream = response.data
        })
        .catch(error => {
          console.log("error issuing stop command", error.response.data)
        })
    },
    setStreamFreq(streamName, newFreq) {
      if (this.stream.stream_freq >= 100) {
        return requests.setStreamFreq(streamName, newFreq)
          .then(response => {
            this.stream = response.data
          })
          .catch(error => {
            console.log("error setting stream freq", error.response.data)
          })
      } else {
        console.log("minimum stream freq is 100ms")
      }
    } 
  }
})
