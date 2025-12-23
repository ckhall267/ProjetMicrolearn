import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import UploadDataset from './pages/UploadDataset';
import Dashboard from './pages/Dashboard';
import AutoML from './pages/AutoML';
import Analysis from './pages/Analysis';
import Results from './pages/Results';
import ModelSelector from './pages/ModelSelector';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/upload" element={<UploadDataset />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/automl" element={<AutoML />} />
              <Route path="/model-selector" element={<ModelSelector />} />
              <Route path="/analysis" element={<Analysis />} />
              <Route path="/results" element={<Results />} />
            </Route>
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
