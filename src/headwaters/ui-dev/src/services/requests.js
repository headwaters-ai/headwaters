import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://127.0.0.1:5555",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

export default {
  getPong() {
    return apiClient.get("/ping");
  },
  getStreamStatus(streamName) {
    return apiClient.get("/stream_status", { params: { 'stream_name': streamName } });
  },
  startStream(streamName) {
    return apiClient.get("/start", { params: { 'stream_name': streamName } });
  },
  stopStream(streamName) {
    return apiClient.get("/stop", { params: { 'stream_name': streamName } });
  },
  setStreamFreq(streamName, newFreq) {
    return apiClient.patch("/freq", {
      'stream_name': streamName,
      'new_freq': newFreq,
    });
  }
};