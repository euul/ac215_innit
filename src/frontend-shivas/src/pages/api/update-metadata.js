import axios from "axios"

export async function PATCH(req) {
  console.log("Received request at /api/update-metadata")

  try {
    const { username, metadata } = await req.json()

    if (!username || !metadata) {
      console.error("Missing username or metadata in request body")
      return new Response(
        JSON.stringify({ detail: "Username and metadata are required" }),
        { status: 400 }
      )
    }

    const backendURL = `${process.env.NEXT_PUBLIC_BASE_API_URL}/update-metadata`
    console.log("Forwarding request to backend at:", backendURL)

    const response = await axios.patch(backendURL, { username, metadata })
    console.log("Backend Response:", response.data)

    return new Response(JSON.stringify(response.data), { status: 200 })
  } catch (error) {
    console.error("Error in API route:", error.response?.data || error.message)
    return new Response(
      JSON.stringify(error.response?.data || { detail: "Server error" }),
      { status: error.response?.status || 500 }
    )
  }
}
