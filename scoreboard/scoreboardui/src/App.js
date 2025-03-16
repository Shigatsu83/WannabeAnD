import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from "react-router-dom";
import Scoreboard from "./Scoreboard";
import ConfigPanel from "./ConfigPanel";
import Login from "./Login";

function PrivateRoute({ children }) {
  return localStorage.getItem("isAuthenticated") ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center">
        <nav className="p-4">
          <Link to="/" className="mr-4 text-blue-400 hover:underline">🏆 Scoreboard</Link>
        </nav>
        <Routes>
          {/* Public Page */}
          <Route path="/" element={<Scoreboard />} />

          {/* Protected Admin Page */}
          <Route path="/admin" element={<PrivateRoute><ConfigPanel /></PrivateRoute>} />

          {/* Login Page */}
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
