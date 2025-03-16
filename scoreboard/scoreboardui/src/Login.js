import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const ADMIN_SECRET = process.env.REACT_APP_ADMIN_PASSWORD || "default_secret";

function Login() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = () => {
    if (password === ADMIN_SECRET) {
      localStorage.setItem("isAuthenticated", ADMIN_SECRET); // Store the secret
      console.log("Stored Secret:", localStorage.getItem("isAuthenticated")); // Debugging
      navigate("/admin");
    } else {
      setError("Invalid password.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
      <div className="bg-gray-800 p-6 rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold mb-4 text-blue-400">🔒 Admin Login</h2>
        {error && <p className="text-red-400">{error}</p>}
        <input
          type="password"
          placeholder="Enter Admin Password"
          className="w-full p-2 mb-3 rounded bg-gray-700 text-white"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          onClick={handleLogin}
          className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Login
        </button>
      </div>
    </div>
  );
}

export default Login;
