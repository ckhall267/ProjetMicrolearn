import React, { useState, useEffect } from 'react';

const AutoML = () => {
  const [selectedDataset, setSelectedDataset] = useState('');
  const [targetColumn, setTargetColumn] = useState('');
  const [taskType, setTaskType] = useState('');
  const [selectedModels, setSelectedModels] = useState([]);
  const [recommendedModels, setRecommendedModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modelSelectionLoading, setModelSelectionLoading] = useState(false);
  const [pipelineConfig, setPipelineConfig] = useState({
    preprocessing: true,
    hyperopt: false,
    crossValidation: true,
  });

  const MODEL_SELECTOR_API = process.env.REACT_APP_MODEL_SELECTOR_API || 'http://localhost:8001/api/v1';

  // Charger les modèles recommandés quand un dataset est sélectionné
  useEffect(() => {
    if (selectedDataset && targetColumn) {
      selectRecommendedModels();
    }
  }, [selectedDataset, targetColumn, taskType]);

  const selectRecommendedModels = async () => {
    setModelSelectionLoading(true);
    try {
      const response = await fetch(`${MODEL_SELECTOR_API}/select`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          dataset_id: selectedDataset,
          dataset_path: `microlearn-data/datasets/${selectedDataset}`,
          target_column: targetColumn || null,
          task_type: taskType || null,
          metric: 'accuracy',
          max_models: 10,
          require_gpu: false,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendedModels(data.selected_models || []);
        // Pré-sélectionner les 3 meilleurs modèles
        const topModels = data.selected_models.slice(0, 3).map((m) => m.name);
        setSelectedModels(topModels);
      }
    } catch (error) {
      console.error('Erreur lors de la sélection de modèles:', error);
    } finally {
      setModelSelectionLoading(false);
    }
  };

  const toggleModel = (modelName) => {
    setSelectedModels((prev) =>
      prev.includes(modelName)
        ? prev.filter((name) => name !== modelName)
        : [...prev, modelName]
    );
  };

  const handleExecute = () => {
    console.log('Exécution du pipeline AutoML avec:', {
      dataset: selectedDataset,
      target_column: targetColumn,
      task_type: taskType,
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
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dataset
              </label>
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
            
            {selectedDataset && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Colonne cible (Target)
                  </label>
                  <input
                    type="text"
                    value={targetColumn}
                    onChange={(e) => setTargetColumn(e.target.value)}
                    placeholder="Ex: species, price, churn"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type de tâche
                  </label>
                  <select
                    value={taskType}
                    onChange={(e) => setTaskType(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Auto-détection</option>
                    <option value="classification">Classification</option>
                    <option value="regression">Régression</option>
                  </select>
                </div>
                
                <button
                  onClick={selectRecommendedModels}
                  disabled={modelSelectionLoading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  {modelSelectionLoading ? 'Sélection en cours...' : 'Sélectionner automatiquement les modèles'}
                </button>
              </>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Sélection des Modèles</h2>
            {recommendedModels.length > 0 && (
              <span className="text-sm text-gray-600">
                {recommendedModels.length} modèles recommandés trouvés
              </span>
            )}
          </div>
          
          {modelSelectionLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Analyse du dataset et sélection des modèles...</p>
            </div>
          ) : recommendedModels.length > 0 ? (
            <div>
              <p className="text-sm text-gray-600 mb-4">
                Les modèles sont triés par score de compatibilité (du plus adapté au moins adapté)
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {recommendedModels.map((model, index) => (
                  <div
                    key={model.name}
                    onClick={() => toggleModel(model.name)}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      selectedModels.includes(model.name)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-gray-900">{model.name}</span>
                          {index < 3 && (
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                              Top {index + 1}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-1 capitalize">{model.category}</p>
                      </div>
                      {selectedModels.includes(model.name) && (
                        <svg className="h-5 w-5 text-blue-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                    </div>
                    
                    <div className="mt-2 space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600">Score de compatibilité:</span>
                        <span className="font-semibold text-blue-600">
                          {model.compatibility_score.toFixed(2)}
                        </span>
                      </div>
                      {model.requires_gpu && (
                        <span className="inline-block px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                          Requiert GPU
                        </span>
                      )}
                      {model.reason && (
                        <p className="text-xs text-gray-500 mt-2 italic">{model.reason}</p>
                      )}
                    </div>
                    
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs font-medium text-gray-700 mb-1">Types de tâches:</p>
                      <div className="flex flex-wrap gap-1">
                        {model.task_types.map((type) => (
                          <span key={type} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                            {type}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>Sélectionnez un dataset et une colonne cible pour voir les modèles recommandés</p>
              <p className="text-sm mt-2">Le service ModelSelector analysera votre dataset et proposera les meilleurs modèles</p>
            </div>
          )}
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

