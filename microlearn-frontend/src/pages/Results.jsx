import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

// Enregistrement des composants Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Results = () => {
  const [pipelineData, setPipelineData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const useQuery = () => new URLSearchParams(useLocation().search);
  const query = useQuery();
  const pipelineId = query.get('id');

  const ORCHESTRATOR_API = process.env.REACT_APP_ORCHESTRATOR_API || 'http://localhost:3100';

  useEffect(() => {
    if (pipelineId) {
      fetchPipelineData(pipelineId);
    } else {
      setLoading(false);
      setError("Aucun ID d'expérience spécifié");
    }
  }, [pipelineId]);

  // Polling automatique
  useEffect(() => {
    let interval;
    if (pipelineData?.status === 'running' || pipelineData?.status === 'started') {
      interval = setInterval(() => {
        fetchPipelineData(pipelineId);
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [pipelineData, pipelineId]);

  const fetchPipelineData = async (id) => {
    try {
      const response = await fetch(`${ORCHESTRATOR_API}/status/${id}`);
      if (!response.ok) throw new Error("Expérience non trouvée");
      const data = await response.json();
      setPipelineData(data);
    } catch (err) {
      console.error("Erreur chargement résultats:", err);
      setError(err.message);
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

  if (error || !pipelineData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center flex-col">
        <h2 className="text-xl font-bold text-red-600 mb-2">Erreur</h2>
        <p className="text-gray-600">{error || "Données indisponibles"}</p>
      </div>
    );
  }

  const { artifacts, status } = pipelineData;
  const evalResults = artifacts?.evaluation_results || [];

  // Trouver le meilleur modèle
  const bestModel = evalResults.length > 0
    ? [...evalResults].sort((a, b) => b.metrics.accuracy - a.metrics.accuracy)[0]
    : null;

  // --- Préparation des Données pour le Graphique de Comparaison ---
  const modelsNames = evalResults.map(r => r.model_name);
  const accuracies = evalResults.map(r => r.metrics.accuracy);
  const f1Scores = evalResults.map(r => r.metrics.f1_score || 0);

  const chartData = {
    labels: modelsNames,
    datasets: [
      {
        label: 'Accuracy',
        data: accuracies,
        backgroundColor: 'rgba(53, 162, 235, 0.6)',
      },
      {
        label: 'F1 Score',
        data: f1Scores,
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Comparaison des Performances',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1.0,
      }
    }
  };

  // --- Rendu de la Matrice de Confusion (si dispo pour le meilleur modèle) ---
  const renderConfusionMatrix = () => {
    if (!bestModel || !bestModel.metrics.confusion_matrix) {
      return <p className="text-gray-500">Données non disponibles</p>;
    }

    const matrix = bestModel.metrics.confusion_matrix;
    // Trouver la valeur max pour la couleur
    const maxVal = Math.max(...matrix.flat());

    return (
      <div className="flex flex-col items-center">
        <p className="mb-2 text-sm text-gray-600 font-semibold">{bestModel.model_name}</p>
        <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${matrix.length}, minmax(0, 1fr))` }}>
          {matrix.map((row, i) => (
            row.map((val, j) => {
              // Calcul opacité (min 0.1 pour visibilité)
              const alpha = maxVal > 0 ? (val / maxVal * 0.8 + 0.1) : 0.1;
              return (
                <div
                  key={`${i}-${j}`}
                  className="w-16 h-16 flex items-center justify-center border border-gray-200 rounded text-sm font-bold"
                  style={{ backgroundColor: `rgba(59, 130, 246, ${alpha})` }}
                  title={`Classe ${i} vs Classe ${j}`}
                >
                  {val}
                </div>
              );
            })
          ))}
        </div>
        <div className="mt-2 text-xs text-gray-500 text-center">
          <p>Y-Axis: Vrai Label</p>
          <p>X-Axis: Prédiction</p>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Résultats & Visualisations
          <span className={`ml-4 text-sm px-3 py-1 rounded-full ${status === 'completed' ? 'bg-green-100 text-green-800' :
            status === 'failed' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
            {status ? status.toUpperCase() : "UNKNOWN"}
          </span>
        </h1>

        {/* --- Section Métriques --- */}
        {evalResults.length > 0 ? (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Performances des Modèles</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Modèle</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Accuracy</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">F1 Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Precision</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recall</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {evalResults.map((res, idx) => (
                    <tr key={idx} className={bestModel === res ? "bg-green-50" : ""}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {res.model_name} {bestModel === res && "🏆"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {(res.metrics.accuracy * 100).toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {res.metrics.f1_score?.toFixed(3) || "N/A"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {res.metrics.precision?.toFixed(3) || "N/A"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {res.metrics.recall?.toFixed(3) || "N/A"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 p-4 rounded-lg mb-6">
            <p className="text-yellow-800">Les résultats d'évaluation ne sont pas encore disponibles. L'entraînement est peut-être encore en cours.</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Comparaison des Métriques</h2>
            <div className="bg-white rounded-lg flex items-center justify-center p-2">
              {evalResults.length > 0 ? (
                <Bar options={chartOptions} data={chartData} />
              ) : (
                <p className="text-gray-500">Pas de données à comparer</p>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Matrice de Confusion (Meilleur Modèle)</h2>
            <div className="bg-white rounded-lg flex flex-col items-center justify-center p-4">
              {renderConfusionMatrix()}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Courbe ROC</h2>
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500 text-center px-4">
                Données ROC non disponibles.<br />
                <span className="text-xs">(Nécessite une mise à jour du backend Evaluator pour retourner les points FPR/TPR)</span>
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Logs d'exécution</h2>
            <div className="h-64 bg-gray-900 rounded-lg p-4 overflow-y-auto font-mono text-xs text-green-400">
              {pipelineData.logs && pipelineData.logs.map((log, i) => (
                <div key={i}>{log}</div>
              ))}
            </div>
          </div>
        </div>

        {bestModel && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Rapport Complet</h2>
            <div className="space-y-4">
              <div className="border-b pb-4">
                <h3 className="font-semibold text-gray-700 mb-2">Résumé Exécutif</h3>
                <p className="text-gray-600">
                  L'expérience a testé {evalResults.length} modèles différents. Le meilleur
                  modèle ({bestModel.model_name}) a atteint une accuracy de {(bestModel.metrics.accuracy * 100).toFixed(2)}%.
                </p>
              </div>
              <div className="border-b pb-4">
                <h3 className="font-semibold text-gray-700 mb-2">Recommandations</h3>
                <ul className="list-disc list-inside text-gray-600 space-y-1">
                  <li>{bestModel.model_name} est recommandé pour la production</li>
                  <li>Le modèle peut être déployé via l'interface Deployer (À venir)</li>
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
        )}
      </div>
    </div >
  );
};

export default Results;

