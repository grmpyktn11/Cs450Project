import { useState } from "react";
import "./App.css"; // Import your stylesheet

export default function App() {
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

  const getRatingColor = (rating) => {
    if (rating === null || rating === undefined) return "rating-gray";
    if (rating > 75) return "rating-green";
    if (rating > 40) return "rating-yellow";
    return "rating-red";
  };

  return (
    <div className="app-container">
      <h1 className="title">Steam Database</h1>
      <h2 className="subtitle">By Emily Hansen and Khalid Moosa</h2>
      <p className="intro">Search for your favorite Steam games below!</p>

      <div className="input-row">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a game..."
          className="search-input"
        />
        <button onClick={sendMessage} className="submit-btn">Submit</button>
      </div>

      {error && <div className="error">{error}</div>}

      {gameInfo && (
        <div className="game-card">
          <div className="top-row">
            <img src={gameInfo.image} alt={gameInfo.gamename} className="game-img" />
            <h2 className="game-title">{gameInfo.gamename}</h2>
          </div>
          <div className="price-row">
            <div><strong>Current Price:</strong> ${gameInfo.currentPrice}</div>
            {gameInfo.currentPrice !== gameInfo.initialPrice && (
              <>
                <div><strong>Discount:</strong> {((gameInfo.initialPrice - gameInfo.currentPrice) / gameInfo.initialPrice * 100).toFixed(0)}%</div>
                <div><strong>Base Price:</strong> ${gameInfo.initialPrice}</div>
              </>
            )}
          </div>
          <div>
            <strong>Rating: </strong>
            <span className={`rating ${getRatingColor(gameInfo.rating)}`}>
              {gameInfo.rating ?? "N/A"}
            </span>
          </div>
          <div><strong>Genre:</strong> {gameInfo.genre}</div>
          <div><strong>Release Date:</strong> {gameInfo.releaseDate}</div>
          <div className="description">
            <p><strong>Description:</strong> {gameInfo.description}</p>
          </div>
        </div>
      )}
    </div>
  );
}
