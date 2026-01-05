import React, { useState, useEffect } from 'react';

const Analysis = () => {
  const [selectedModel, setSelectedModel] = useState(null);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);

  const ORCHESTRATOR_API = process.env.REACT_APP_ORCHESTRATOR_API || 'http://localhost:3100';

  useEffect(() => {
    fetchAnalysisData();
  }, []);

  const fetchAnalysisData = async () => {
    try {
      // 1. Récupérer l'historique pour trouver le dernier pipeline terminé
      const historyRes = await fetch(`${ORCHESTRATOR_API}/history`);
      const historyData = await historyRes.json();
      const history = historyData.history || [];

      const lastCompleted = history.find(h => h.status === 'completed');

      if (lastCompleted) {
        // 2. Récupérer les détails de ce pipeline
        const statusRes = await fetch(`${ORCHESTRATOR_API}/status/${lastCompleted.id}`);
        const statusData = await statusRes.json();

        const evalResults = statusData.artifacts?.evaluation_results || [];

        // Transformer pour l'affichage
        const formattedModels = evalResults.map((res, index) => ({
          id: res.model_name, // Ou index si pas d'ID unique
          name: res.model_name,
          accuracy: res.metrics.accuracy,
          f1: res.metrics.f1_score,
          auc: 0.0, // Pas toujours dispo, à adapter
          precision: res.metrics.precision,
          recall: res.metrics.recall,
          hyperparameters: res.hyperparameters || {} // Il faudra s'assurer que le backend renvoie ça
        }));
        setModels(formattedModels);
      }
    } catch (error) {
      console.error("Erreur chargement analyse:", error);
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
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Analyse des Modèles</h1>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Comparaison des Modèles</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Modèle
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Accuracy
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    F1 Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    AUC
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {models.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                      Aucune donnée d'analyse disponible. Lancez un pipeline AutoML d'abord.
                    </td>
                  </tr>
                ) : (
                  models.map((model) => (
                    <tr key={model.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {model.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {(model.accuracy * 100).toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {model.f1.toFixed(3)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        -
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => setSelectedModel(model)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Voir détails
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {selectedModel && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Détails du Modèle</h2>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">Hyperparamètres</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <pre className="text-sm text-gray-600">
                    {JSON.stringify(selectedModel.hyperparameters || {}, null, 2)}
                  </pre>
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">Métriques détaillées</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Precision:</span>
                    <span className="font-medium">{selectedModel.precision?.toFixed(3) || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Recall:</span>
                    <span className="font-medium">{selectedModel.recall?.toFixed(3) || 'N/A'}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analysis;

