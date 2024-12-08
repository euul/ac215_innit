import axios from "axios";

export default async function handler(req, res) {
    console.log("Received request at /login"); // Log the request

    if (req.method === "POST") {
        const { username, password } = req.body;
        console.log("Request Body:", { username, password }); // Log the incoming request body

        try {
            const backendURL = `${process.env.NEXT_PUBLIC_BASE_API_URL}/login`;
            console.log("Forwarding request to:", backendURL); // Log where the request is going

            const response = await axios.post(backendURL, { username, password });
            console.log("Backend Response:", response.data); // Log the backend response

            res.status(200).json(response.data);
        } catch (error) {
            console.error("Error in API route:", error.response?.data || error.message);
            res.status(error.response?.status || 500).json(
                error.response?.data || { detail: "Server error" }
            );
        }
    } else {
        console.log(`Unsupported method: ${req.method}`); // Log unsupported HTTP methods
        res.setHeader("Allow", ["POST"]);
        res.status(405).end(`Method ${req.method} Not Allowed`);
    }
}
