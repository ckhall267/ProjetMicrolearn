import React, { useState } from 'react';

const Analysis = () => {
  const [selectedModel, setSelectedModel] = useState('');

  const models = [
    { id: '1', name: 'XGBoost - Iris Dataset', accuracy: 0.98, f1: 0.97, auc: 0.99 },
    { id: '2', name: 'Random Forest - House Prices', accuracy: 0.92, f1: 0.91, auc: 0.94 },
    { id: '3', name: 'SVM - Customer Churn', accuracy: 0.89, f1: 0.88, auc: 0.90 },
  ];

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
                {models.map((model) => (
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
                      {model.auc.toFixed(3)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => setSelectedModel(model.id)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Voir détails
                      </button>
                    </td>
                  </tr>
                ))}
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
                    {JSON.stringify(
                      {
                        learning_rate: 0.1,
                        max_depth: 6,
                        n_estimators: 100,
                      },
                      null,
                      2
                    )}
                  </pre>
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">Métriques détaillées</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Precision:</span>
                    <span className="font-medium">0.95</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Recall:</span>
                    <span className="font-medium">0.94</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">RMSE:</span>
                    <span className="font-medium">0.12</span>
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

