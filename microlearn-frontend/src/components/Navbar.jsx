import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-blue-600';
  };

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="text-2xl font-bold text-blue-600">
                MicroLearn
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link
                to="/"
                className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/')}`}
              >
                Accueil
              </Link>
              <Link
                to="/upload"
                className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/upload')}`}
              >
                Upload Dataset
              </Link>
              <Link
                to="/dashboard"
                className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/dashboard')}`}
              >
                Dashboard
              </Link>
              <Link
                to="/automl"
                className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/automl')}`}
              >
                AutoML
              </Link>
              <Link
                to="/analysis"
                className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/analysis')}`}
              >
                Analyse des modèles
              </Link>
              <Link
                to="/results"
                className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/results')}`}
              >
                Résultats
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

