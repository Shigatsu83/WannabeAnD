import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8080";
const ADMIN_KEY = process.env.REACT_APP_ADMIN_KEY || "default_admin_key";
const ADMIN_SECRET = process.env.REACT_APP_ADMIN_PASSWORD;

function ConfigPanel() {
  const [config, setConfig] = useState({ num_teams: 0, teams: {} });
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const storedSecret = localStorage.getItem("isAuthenticated");
    if (storedSecret !== ADMIN_SECRET) {
        navigate("/login");
    }

    axios.get(`${API_URL}/config`, {
        headers: { Authorization: ADMIN_KEY }
      })
      .then(response => {
        setConfig(response.data);
        setLoading(false);
      })
      .catch(error => console.error("Error fetching config:", error));
  }, [navigate]);

  const handleNumTeamsChange = (event) => {
    const newNumTeams = parseInt(event.target.value, 10);
    setConfig(prevConfig => ({
      ...prevConfig,
      num_teams: newNumTeams,
      teams: Object.fromEntries(
        Array.from({ length: newNumTeams }, (_, i) => [`team${i + 1}`, { api_key: "" }])
      )
    }));
  };

  const handleApiKeyChange = (team, event) => {
    const newApiKey = event.target.value;
    setConfig(prevConfig => ({
      ...prevConfig,
      teams: { ...prevConfig.teams, [team]: { api_key: newApiKey } }
    }));
  };

  const handleSubmit = () => {
    axios.post(`${API_URL}/update_config`, config, {
      headers: { Authorization: ADMIN_KEY }
    })
    .then(response => setMessage(response.data.message))
    .catch(error => setMessage("Failed to update configuration"));
  };

  const handleLogout = () => {
    localStorage.removeItem("isAuthenticated");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold mb-4 text-blue-400">⚙️ Admin Panel ⚙️</h1>
      <button
        onClick={handleLogout}
        className="absolute top-4 right-4 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
      >
        Logout
      </button>
      {loading ? (
        <p>Loading configuration...</p>
      ) : (
        <div className="w-full max-w-lg bg-gray-800 p-6 rounded-lg shadow-md">
          <label className="block mb-2">Number of Teams:</label>
          <input
            type="number"
            value={config.num_teams}
            onChange={handleNumTeamsChange}
            className="w-full p-2 mb-4 rounded bg-gray-700 text-white"
          />
          {Object.keys(config.teams).map(team => (
            <div key={team} className="mb-3">
              <label className="block">{team} API Key:</label>
              <input
                type="text"
                value={config.teams[team].api_key}
                onChange={(e) => handleApiKeyChange(team, e)}
                className="w-full p-2 rounded bg-gray-700 text-white"
              />
            </div>
          ))}
          <button
            onClick={handleSubmit}
            className="w-full mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Save Configuration
          </button>
          {message && <p className="mt-4 text-green-400">{message}</p>}
        </div>
      )}
    </div>
  );
}

export default ConfigPanel;