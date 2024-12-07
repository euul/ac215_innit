import React, { useEffect, useState } from 'react';

function App() {
  const [message, setMessage] = useState("");

useEffect(() => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
    fetch(`${backendUrl}/api/hello`)
        .then((response) => response.json())
        .then((data) => setMessage(data.message))
        .catch((error) => console.error("Error:", error));
}, []);


  return (
    <div>
      <h1>Simple Website</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;
