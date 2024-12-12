import axios from "axios"

const updateUserMetadata = async (username, metadata) => {
  try {
    const response = await axios.put(
      `${process.env.NEXT_PUBLIC_BASE_API_URL}/update-metadata`,
      { username, metadata }
    )
    return response.data
  } catch (error) {
    console.error("Error updating user metadata:", error)
    throw error
  }
}

export default { updateUserMetadata }
