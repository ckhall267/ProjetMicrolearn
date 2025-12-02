import React, { useState } from 'react';

const AutoML = () => {
  const [selectedDataset, setSelectedDataset] = useState('');
  const [selectedModels, setSelectedModels] = useState([]);
  const [pipelineConfig, setPipelineConfig] = useState({
    preprocessing: true,
    hyperopt: false,
    crossValidation: true,
  });

  const availableModels = [
    { id: 'xgboost', name: 'XGBoost', type: 'ensemble' },
    { id: 'svm', name: 'SVM', type: 'classical' },
    { id: 'randomforest', name: 'Random Forest', type: 'ensemble' },
    { id: 'cnn', name: 'CNN', type: 'deep_learning' },
    { id: 'logistic', name: 'Logistic Regression', type: 'classical' },
  ];

  const toggleModel = (modelId) => {
    setSelectedModels((prev) =>
      prev.includes(modelId)
        ? prev.filter((id) => id !== modelId)
        : [...prev, modelId]
    );
  };

  const handleExecute = () => {
    console.log('Exécution du pipeline AutoML avec:', {
      dataset: selectedDataset,
      models: selectedModels,
      config: pipelineConfig,
    });
    // Ici, vous appelleriez l'API de l'Orchestrator
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Interface AutoML</h1>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Sélection du Dataset</h2>
          <select
            value={selectedDataset}
            onChange={(e) => setSelectedDataset(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Sélectionner un dataset</option>
            <option value="dataset1">Iris Dataset</option>
            <option value="dataset2">House Prices</option>
            <option value="dataset3">Customer Churn</option>
          </select>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Sélection des Modèles</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {availableModels.map((model) => (
              <div
                key={model.id}
                onClick={() => toggleModel(model.id)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  selectedModels.includes(model.id)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">{model.name}</span>
                  {selectedModels.includes(model.id) && (
                    <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-1">{model.type}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Configuration du Pipeline</h2>
          <div className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={pipelineConfig.preprocessing}
                onChange={(e) =>
                  setPipelineConfig({ ...pipelineConfig, preprocessing: e.target.checked })
                }
                className="mr-3 h-4 w-4 text-blue-600"
              />
              <span className="text-gray-700">Prétraitement automatique (DataPreparer)</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={pipelineConfig.hyperopt}
                onChange={(e) =>
                  setPipelineConfig({ ...pipelineConfig, hyperopt: e.target.checked })
                }
                className="mr-3 h-4 w-4 text-blue-600"
              />
              <span className="text-gray-700">Optimisation des hyperparamètres (HyperOpt)</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={pipelineConfig.crossValidation}
                onChange={(e) =>
                  setPipelineConfig({ ...pipelineConfig, crossValidation: e.target.checked })
                }
                className="mr-3 h-4 w-4 text-blue-600"
              />
              <span className="text-gray-700">Validation croisée</span>
            </label>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            onClick={handleExecute}
            disabled={!selectedDataset || selectedModels.length === 0}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Exécuter le Pipeline AutoML
          </button>
        </div>
      </div>
    </div>
  );
};

export default AutoML;

