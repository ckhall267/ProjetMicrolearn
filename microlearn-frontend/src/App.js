import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import UploadDataset from './pages/UploadDataset';
import Dashboard from './pages/Dashboard';
import AutoML from './pages/AutoML';
import Analysis from './pages/Analysis';
import Results from './pages/Results';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<UploadDataset />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/automl" element={<AutoML />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
