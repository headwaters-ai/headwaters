import { defineStore } from 'pinia'
import requests from '../services/requests.js'

export const useEngineStore = defineStore({
  id: 'engine',
  state: () => ({
    stream: ''
  }),
  actions: {
    getStreamStatus(streamName) {
      return requests.getStreamStatus(streamName)
      .then(response => {
          console.log('stream status rcvd' , response.data)
          this.stream = response.data
          console.log('stream state:', this.stream)
      })
      .catch(error => {
          console.log("issue getting stream status", error)
          throw error
      })
    },
    startStream(streamName) {
      return requests.startStream(streamName)
      .then(response => {
          this.stream = response.data
          console.log('stream state:', this.stream)
      })
      .catch(error => {
          console.log("error issuing start command", error)
          throw error
      })
    },
    stopStream(streamName) {
      return requests.stopStream(streamName)
      .then(response => {
          this.stream = response.data
          console.log('stream state:', this.stream)
      })
      .catch(error => {
          console.log("error issuing stop command", error)
          throw error
      })
    }
  }
})
