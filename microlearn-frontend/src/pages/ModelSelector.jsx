import React, { useState, useEffect } from 'react';

const ModelSelector = () => {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('');
  const [targetColumn, setTargetColumn] = useState('');
  const [taskType, setTaskType] = useState('');
  const [selectedModels, setSelectedModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [allModels, setAllModels] = useState([]);
  const [showAllModels, setShowAllModels] = useState(false);

  const MODEL_SELECTOR_API = process.env.REACT_APP_MODEL_SELECTOR_API || 'http://localhost:8001/api/v1';

  useEffect(() => {
    fetchAllModels();
  }, []);

  const fetchAllModels = async () => {
    try {
      const response = await fetch(`${MODEL_SELECTOR_API}/models`);
      if (response.ok) {
        const data = await response.json();
        setAllModels(data.models || []);
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des modèles:', error);
    }
  };

  const handleSelectModels = async () => {
    if (!selectedDataset) {
      alert('Veuillez sélectionner un dataset');
      return;
    }

    setLoading(true);
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
        setSelectedModels(data.selected_models || []);
      } else {
        alert('Erreur lors de la sélection de modèles');
      }
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors de la sélection de modèles');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">ModelSelector</h1>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-blue-900 mb-2">
            Sélection automatique de modèles
          </h2>
          <p className="text-blue-800">
            Le service ModelSelector analyse votre dataset et recommande automatiquement 
            les modèles d'apprentissage automatique les plus adaptés en fonction de :
          </p>
          <ul className="list-disc list-inside mt-2 text-blue-700 space-y-1">
            <li>Type de tâche (classification, régression)</li>
            <li>Caractéristiques du dataset (taille, nombre de features, type de données)</li>
            <li>Compatibilité modèle/données</li>
            <li>Performances attendues</li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Configuration</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Colonne cible
              </label>
              <input
                type="text"
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
                placeholder="Ex: species, price"
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
            
            <div className="flex items-end">
              <button
                onClick={handleSelectModels}
                disabled={loading || !selectedDataset}
                className="w-full bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {loading ? 'Sélection en cours...' : 'Sélectionner les modèles'}
              </button>
            </div>
          </div>
        </div>

        {selectedModels.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Modèles recommandés ({selectedModels.length})
            </h2>
            <div className="space-y-4">
              {selectedModels.map((model, index) => (
                <div
                  key={model.name}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="text-lg font-semibold text-gray-900">
                          {index + 1}. {model.name}
                        </span>
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                          Score: {model.compatibility_score.toFixed(2)}
                        </span>
                        <span className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full capitalize">
                          {model.category}
                        </span>
                      </div>
                      
                      {model.reason && (
                        <p className="text-sm text-gray-600 mb-3 italic">
                          {model.reason}
                        </p>
                      )}
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                        <div>
                          <p className="text-xs text-gray-500">Types de tâches</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {model.task_types.map((type) => (
                              <span key={type} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                                {type}
                              </span>
                            ))}
                          </div>
                        </div>
                        
                        <div>
                          <p className="text-xs text-gray-500">Caractéristiques</p>
                          <div className="mt-1 space-y-1">
                            {model.requires_gpu && (
                              <span className="block px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                                GPU requis
                              </span>
                            )}
                            {model.supports_sparse && (
                              <span className="block px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                                Support sparse
                              </span>
                            )}
                          </div>
                        </div>
                        
                        <div>
                          <p className="text-xs text-gray-500">Min. échantillons</p>
                          <p className="text-sm font-medium">{model.min_samples}</p>
                        </div>
                        
                        <div>
                          <p className="text-xs text-gray-500">Max. features</p>
                          <p className="text-sm font-medium">
                            {model.max_features || 'Illimité'}
                          </p>
                        </div>
                      </div>
                      
                      {model.hyperparameters && Object.keys(model.hyperparameters).length > 0 && (
                        <details className="mt-3">
                          <summary className="cursor-pointer text-sm font-medium text-blue-600 hover:text-blue-800">
                            Voir les hyperparamètres par défaut
                          </summary>
                          <div className="mt-2 bg-gray-50 p-3 rounded">
                            <pre className="text-xs text-gray-700 overflow-x-auto">
                              {JSON.stringify(model.hyperparameters, null, 2)}
                            </pre>
                          </div>
                        </details>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Tous les modèles disponibles ({allModels.length})
            </h2>
            <button
              onClick={() => setShowAllModels(!showAllModels)}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              {showAllModels ? 'Masquer' : 'Afficher'}
            </button>
          </div>
          
          {showAllModels && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {allModels.map((model) => (
                <div
                  key={model.name}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <h3 className="font-semibold text-gray-900 mb-2">{model.name}</h3>
                  <p className="text-xs text-gray-500 mb-2 capitalize">{model.category}</p>
                  <div className="flex flex-wrap gap-1">
                    {model.task_types.map((type) => (
                      <span key={type} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                        {type}
                      </span>
                    ))}
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

export default ModelSelector;

