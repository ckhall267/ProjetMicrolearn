import React from 'react';

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard Utilisateur</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Datasets</h3>
            <p className="text-3xl font-bold text-blue-600">12</p>
            <p className="text-sm text-gray-500 mt-2">Total uploadés</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Modèles entraînés</h3>
            <p className="text-3xl font-bold text-green-600">45</p>
            <p className="text-sm text-gray-500 mt-2">En production</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Expériences actives</h3>
            <p className="text-3xl font-bold text-purple-600">8</p>
            <p className="text-sm text-gray-500 mt-2">En cours</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Expériences récentes</h2>
          <div className="space-y-4">
            <div className="border-b pb-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium text-gray-900">Classification Iris Dataset</p>
                  <p className="text-sm text-gray-500">Démarré il y a 2 heures</p>
                </div>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  Terminé
                </span>
              </div>
            </div>
            <div className="border-b pb-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium text-gray-900">Régression House Prices</p>
                  <p className="text-sm text-gray-500">Démarré il y a 5 heures</p>
                </div>
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                  En cours
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

