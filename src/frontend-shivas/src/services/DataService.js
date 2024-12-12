import { BASE_API_URL } from "./Common"
import axios from "axios"

// Create an axios instance
const api = axios.create({
  baseURL: BASE_API_URL,
})

// Add request interceptor to include session ID in headers
api.interceptors.request.use(
  (config) => {
    const sessionId = localStorage.getItem("userSessionId")
    if (sessionId) {
      config.headers["X-Session-ID"] = sessionId
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

const DataService = {
  // Existing methods...

  // Fetch diagnostic test questions
  GetDiagnosticTestQuestions: async function () {
    return await api.get("/diagnostic")
  },

  // Submit diagnostic test responses
  SubmitDiagnosticTestResponses: async function (responses) {
    return await api.post("/diagnostic/submit", { responses })
  },
}

export default DataService
