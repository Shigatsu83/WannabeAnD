import React, { useEffect, useState } from "react";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://192.168.100.7:8080";

function Scoreboard() {
  const [scores, setScores] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchScores = () => {
      axios.get(`${API_URL}/scoreboard`)
        .then(response => {
          setScores(response.data);
          setLoading(false);
        })
        .catch(error => {
          console.error("Error fetching scoreboard:", error);
        });
    };

    fetchScores();
    const interval = setInterval(fetchScores, 5000);

    return () => clearInterval(interval);
  }, []);

  const sortedScores = Object.entries(scores).sort((a, b) => b[1] - a[1]);

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold mb-6 text-blue-400">🏆 CTF Scoreboard 🏆</h1>
      {loading ? (
        <p className="text-xl">Loading scores...</p>
      ) : (
        <div className="w-full max-w-2xl">
          <table className="w-full bg-gray-800 shadow-md rounded-lg overflow-hidden">
            <thead className="bg-blue-500">
              <tr>
                <th className="px-4 py-3 text-left">Rank</th>
                <th className="px-4 py-3 text-left">Team</th>
                <th className="px-4 py-3 text-right">Points</th>
              </tr>
            </thead>
            <tbody>
              {sortedScores.map(([team, points], index) => (
                <tr key={team} className={`border-b border-gray-700 ${index === 0 ? "bg-yellow-500 text-black font-bold" : "bg-gray-700"}`}>
                  <td className="px-4 py-3">{index + 1}</td>
                  <td className="px-4 py-3">{team}</td>
                  <td className="px-4 py-3 text-right">{points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Scoreboard;
