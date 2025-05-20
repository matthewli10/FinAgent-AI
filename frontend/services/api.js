export async function summarizeTranscript(ticker, transcript_text) {
    try {
      const res = await fetch("http://192.168.86.34:8000/summarize/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker, transcript_text }),
      });
  
      console.log("Status:", res.status);
  
      if (!res.ok) {
        const errorText = await res.text();
        console.error("API Error Response:", errorText);
        throw new Error("API call failed");
      }
  
      return await res.json();
    } catch (err) {
      console.error("Error:", err.message);
      return null;
    }
  }
  