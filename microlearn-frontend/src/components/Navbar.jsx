import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

const Navbar = () => {
  const location = useLocation();
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const isActive = (path) => {
    return location.pathname === path ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-blue-600';
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
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
              {isAuthenticated && (
                <>
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
                    to="/model-selector"
                    className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/model-selector')}`}
                  >
                    ModelSelector
                  </Link>
                  <Link
                    to="/analysis"
                    className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/analysis')}`}
                  >
                    Analyse
                  </Link>
                  <Link
                    to="/results"
                    className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/results')}`}
                  >
                    Résultats
                  </Link>
                </>
              )}
            </div>
          </div>
          <div className="flex items-center">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <span className="text-gray-700 font-medium">
                  {user?.username || 'Utilisateur'}
                </span>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-md text-sm font-medium transition-colors"
                >
                  Déconnexion
                </button>
              </div>
            ) : (
              <div className="flex space-x-4">
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Connexion
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  Inscription
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

