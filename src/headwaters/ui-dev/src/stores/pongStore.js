import { defineStore } from 'pinia'
import requests from '../services/requests.js'

export const usePongStore = defineStore({
  id: 'pong',
  state: () => ({
    pong: null
  }),
  getters: {
    doublePong: (state) => state.pong * 2
  },
  actions: {
    incrementPong() {
      this.pong++
    },
    getPong() {
      return requests.getPong()
      .then(response => {
          console.log('pong rcvd' , response.data)
          this.pong = response.data.pong
      })
      .catch(error => {
          console.log("issue gettign a pong", error)
          throw error
      })
    }
  }
})
