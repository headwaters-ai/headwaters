import { defineStore } from 'pinia'
import requests from '../services/requests.js'

export const useSourceStore = defineStore({
  id: 'source',
  state: () => ({
    source: '',
    messages: []
  }),
  actions: {
    getSingleSourceStatus(sourceName) {
      return requests.getSingleSourceStatus(sourceName)
        .then(response => {
          this.source = response.data
          console.log('source state:', this.source)
        })
        .catch(error => {
          this.messages.push(error.response.data.msg)
          setTimeout(() => this.messages.shift(), 5000)
          console.log("issue getting source status", error.response.data)
        })
    },
    setValueErrorsToggle(sourceName, ValueErrorBool) {
        return requests.setValueErrorsToggle(sourceName, ValueErrorBool)
          .then(response => {
            this.source = response.data
            console.log('source state:', this.source)
          })
          .catch(error => {
            this.messages.push(error.response.data.msg)
            setTimeout(() => this.messages.shift(), 5000)
            console.log("issue getting source status in val error toggle", error.response.data)
          })
      },
  }
})
