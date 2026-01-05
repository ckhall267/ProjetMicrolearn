import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [stats, setStats] = useState({
    datasets: 0,
    models: 0,
    activeExperiments: 0
  });
  const [recentExperiments, setRecentExperiments] = useState([]);
  const [loading, setLoading] = useState(true);

  const ORCHESTRATOR_API = process.env.REACT_APP_ORCHESTRATOR_API || 'http://localhost:3100';
  const DATAPREPARER_API = process.env.REACT_APP_DATAPREPARER_API || 'http://localhost:8000/api/v1';

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // 1. Récupérer les datasets
      const datasetsRes = await fetch(`${DATAPREPARER_API}/datasets`);
      const datasetsData = await datasetsRes.json();
      const datasetCount = datasetsData.datasets ? datasetsData.datasets.length : 0;

      // 2. Récupérer l'historique des pipelines
      const historyRes = await fetch(`${ORCHESTRATOR_API}/history`);
      const historyData = await historyRes.json();
      const history = historyData.history || [];

      // Calculer les stats
      const active = history.filter(h => h.status === 'running' || h.status === 'started').length;
      // On estime le nombre de modèles entraînés (somme des modèles par pipeline terminé)
      const modelsCount = history
        .filter(h => h.status === 'completed')
        .reduce((acc, curr) => acc + (curr.model_count || 0), 0);

      setStats({
        datasets: datasetCount,
        models: modelsCount,
        activeExperiments: active
      });

      setRecentExperiments(history.slice(0, 5)); // Prendre les 5 derniers
    } catch (error) {
      console.error("Erreur chargement dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard Utilisateur</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Datasets</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.datasets}</p>
            <p className="text-sm text-gray-500 mt-2">Total uploadés</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Modèles entraînés</h3>
            <p className="text-3xl font-bold text-green-600">{stats.models}</p>
            <p className="text-sm text-gray-500 mt-2">Total en production</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Expériences actives</h3>
            <p className="text-3xl font-bold text-purple-600">{stats.activeExperiments}</p>
            <p className="text-sm text-gray-500 mt-2">En cours</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Expériences récentes</h2>

          {recentExperiments.length === 0 ? (
            <p className="text-gray-500 text-center py-4">Aucune expérience récente.</p>
          ) : (
            <div className="space-y-4">
              {recentExperiments.map((exp) => (
                <div key={exp.id} className="border-b pb-4 last:border-0 last:pb-0">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900">
                        {exp.dataset_id} <span className="text-xs text-gray-400">({exp.id.substring(0, 8)}...)</span>
                      </p>
                      <p className="text-sm text-gray-500">
                        Démarré le {new Date(exp.startTime).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${exp.status === 'completed' ? 'bg-green-100 text-green-800' :
                          exp.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                        }`}>
                        {exp.status === 'completed' ? 'Terminé' :
                          exp.status === 'failed' ? 'Échoué' : 'En cours'}
                      </span>
                      <Link
                        to={`/results?id=${exp.id}`}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        Voir résultats →
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

