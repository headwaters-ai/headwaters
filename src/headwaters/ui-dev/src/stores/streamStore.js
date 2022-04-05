import { defineStore } from 'pinia'
import requests from '../services/requests.js'

export const useStreamStore = defineStore({
  id: 'stream',
  state: () => ({
    stream: '',
    messages: []
  }),
  actions: {
    getStreamStatus(streamName) {
      return requests.getStreamStatus(streamName)
        .then(response => {
          this.stream = response.data
          console.log('stream state:', this.stream)
        })
        .catch(error => {
          this.messages.push(error.response.data.msg)
          setTimeout(() => this.messages.shift(), 5000)
          console.log("issue getting stream status", error.response.data)
        })
    },
    startStream(streamName) {
      return requests.startStream(streamName)
        .then(response => {
          this.stream = response.data
        })
        .catch(error => {
          this.getStreamStatus(streamName)
          this.messages.push(error.response.data.msg)
          setTimeout(() => this.messages.shift(), 5000)
          console.log("error issuing start command", error.response.data)
        })
    },
    stopStream(streamName) {
      return requests.stopStream(streamName)
        .then(response => {
          this.stream = response.data
        })
        .catch(error => {
          this.getStreamStatus(streamName)
          this.messages.push(error.response.data.msg)
          setTimeout(() => this.messages.shift(), 5000)
          console.log("error issuing stop command", error.response.data)
        })
    },
    setStreamFreq(streamName, newFreq) {
      return requests.setStreamFreq(streamName, newFreq)
        .then(response => {
          this.stream = response.data
        })
        .catch(error => {
          this.messages.push(error.response.data.msg)
          setTimeout(() => this.messages.shift(), 5000)
          console.log("error setting stream frequency", error.response.data)
        })
    },
    setBurstFreq(streamName, burstFreq) {
      return requests.setBurstFreq(streamName, burstFreq)
        .then(response => {
          this.stream = response.data
        })
        .catch(error => {
          this.messages.push(error.response.data.msg)
          setTimeout(() => this.messages.shift(), 5000)
          console.log("error setting burst frequency", error.response.data)
        })
    },
    setBurstVol(streamName, burstVol) {
      return requests.setBurstVol(streamName, burstVol)
        .then(response => {
          this.stream = response.data
        })
        .catch(error => {
          this.messages.push('the burst volume setting cannot be lower than that')
          setTimeout(() => this.messages.shift(), 5000)
          console.log("error setting burst volume", error.response.data)
        })
    },
    startBurst(streamName) {
      return requests.startBurst(streamName)
        .then(response => {
          this.stream = response.data
        })
        .catch(error => {
          this.messages.push(error.response.data.msg)
          setTimeout(() => this.messages.shift(), 5000)
          console.log("error starting burst", error.response.data)
        })
    }
  }
})
