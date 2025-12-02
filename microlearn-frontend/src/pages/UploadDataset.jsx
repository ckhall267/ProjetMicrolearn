import React, { useState } from 'react';
import FileUpload from '../components/FileUpload';

const UploadDataset = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleFileSelect = (file) => {
    console.log('Fichier sélectionné:', file);
    // Ici, vous pouvez ajouter la logique pour traiter le fichier
  };

  const handleUploadComplete = (file) => {
    setUploadedFiles((prev) => [...prev, file]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Upload Dataset
          </h1>
          <p className="text-gray-600 mb-8">
            Téléversez votre dataset pour commencer le processus AutoML. Les formats CSV et JSON sont supportés.
          </p>

          <FileUpload
            onFileSelect={handleFileSelect}
            acceptedTypes=".csv,.json"
            maxSizeMB={100}
          />

          {/* Informations sur le préprocessing */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-blue-900 mb-3">
              Pipeline de préparation des données
            </h2>
            <p className="text-blue-800 mb-4">
              Une fois votre dataset uploadé, le service DataPreparer effectuera automatiquement :
            </p>
            <ul className="list-disc list-inside space-y-2 text-blue-700">
              <li>Nettoyage des données (suppression des doublons, outliers)</li>
              <li>Gestion des valeurs manquantes (imputation)</li>
              <li>Encodage des variables catégorielles (one-hot encoding, label encoding)</li>
              <li>Normalisation et standardisation des features</li>
              <li>Détection automatique du type de problème (classification/régression)</li>
            </ul>
          </div>

          {/* Historique des fichiers uploadés */}
          {uploadedFiles.length > 0 && (
            <div className="mt-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Fichiers uploadés récemment
              </h2>
              <div className="space-y-2">
                {uploadedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="bg-gray-50 p-4 rounded-lg flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-3">
                      <svg
                        className="h-6 w-6 text-green-500"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <div>
                        <p className="font-medium text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-500">
                          {(file.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <button className="text-blue-600 hover:text-blue-800 font-medium">
                      Voir les détails
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadDataset;

