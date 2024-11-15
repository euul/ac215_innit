import { TextField, Button } from "@mui/material"

function DiagnosticTest() {
  return (
    <div style={{ textAlign: "center", marginTop: "2rem" }}>
      <h2>Diagnostic Test</h2>
      <p>Take this test to determine your language level.</p>
      <form
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <TextField
          label="Question 1"
          variant="outlined"
          style={{ marginBottom: "1rem", width: "300px" }}
        />
        <Button variant="contained" color="primary">
          Submit
        </Button>
      </form>
    </div>
  )
}

export default DiagnosticTest
