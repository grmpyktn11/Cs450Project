import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");
  const [gameInfo, setGameInfo] = useState(null);
  const [error, setError] = useState("");

  const sendMessage = async () => {
    setGameInfo(null);
    setError("");
    const res = await fetch("http://localhost:5000/api/returngame", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ search: message })
    });

    const data = await res.json();

    if (data.error) {
      setError(data.error);
    } else {
      setGameInfo(data);
    }
  };

  return (
    <div style={{ padding: "40px" }}>
      <h1>steam database</h1>

      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a game..."
        style={{ padding: "10px", width: "250px" }}
      />

      <button
        onClick={sendMessage}
        style={{ marginLeft: "10px", padding: "10px" }}
      >
        Submit
      </button>

      <div style={{ marginTop: "20px" }}>
        {error && <div style={{ color: "red" }}>{error}</div>}

        {gameInfo && (
          <div>
            <p><strong>Name:</strong> {gameInfo.gamename}</p>
            <p><strong>Steam URL:</strong> <a href={gameInfo.url} target="_blank">{gameInfo.url}</a></p>
            <p><strong>Base Price:</strong> ${gameInfo.initialPrice}</p>
            <p><strong>Current Price:</strong> ${gameInfo.currentPrice}</p>
            <p><strong>Rating:</strong> {gameInfo.rating ?? "N/A"}</p>
            <p><strong>Genre:</strong> {gameInfo.genre}</p>
            <p><strong>Release Date:</strong> {gameInfo.releaseDate}</p>
            <p><strong>Description:</strong> {gameInfo.description}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
