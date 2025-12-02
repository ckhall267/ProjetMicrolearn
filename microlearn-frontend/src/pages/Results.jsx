import React from 'react';

const Results = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Résultats & Visualisations</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Courbe ROC</h2>
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Graphique ROC à intégrer (Chart.js/D3.js)</p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Matrice de Confusion</h2>
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Matrice de confusion à intégrer</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Comparaison des Métriques</h2>
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Graphique de comparaison à intégrer</p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Historique d'Entraînement</h2>
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Graphique d'historique à intégrer</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Rapport Complet</h2>
          <div className="space-y-4">
            <div className="border-b pb-4">
              <h3 className="font-semibold text-gray-700 mb-2">Résumé Exécutif</h3>
              <p className="text-gray-600">
                L'expérience AutoML a testé 5 modèles différents sur le dataset Iris. Le meilleur
                modèle (XGBoost) a atteint une accuracy de 98% avec un F1-score de 0.97.
              </p>
            </div>
            <div className="border-b pb-4">
              <h3 className="font-semibold text-gray-700 mb-2">Recommandations</h3>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li>XGBoost est recommandé pour la production</li>
                <li>Le modèle peut être déployé via l'interface Deployer</li>
                <li>Considérer l'optimisation des hyperparamètres pour améliorer encore les performances</li>
              </ul>
            </div>
            <div className="flex justify-end space-x-4">
              <button className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
                Télécharger le rapport PDF
              </button>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Déployer le meilleur modèle
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Results;

