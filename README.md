MicroLearn — Orchestrateur AutoML par microservices 
Contexte 
L'exploration de modèles d’apprentissage automatique (ML) nécessite souvent des 
compétences avancées et un processus long : nettoyage des données, sélection de modèles, 
entraînement, évaluation, déploiement. Les solutions AutoML (Automated Machine Learning) 
restent souvent monolithiques, difficiles à personnaliser et peu ouvertes à l’expérimentation 
distribuée. Dans un contexte académique ou industriel, il devient crucial de composer 
dynamiquement des pipelines ML pour tester plusieurs approches, itérer rapidement, et 
répliquer les expériences. 
Objectif 
Développer une plateforme modulaire d'AutoML distribuée basée sur des microservices, 
chacun réalisant une étape du pipeline de data mining : préparation, sélection de modèles, 
entraînement, évaluation, déploiement. L’utilisateur (développeur ou data scientist) pourra 
composer un pipeline ML sur mesure via API, lancer des entraînements parallèles sur GPU, et 
comparer les performances. Le tout est conçu pour être scalable, personnalisable, et 
réplicable, conformément aux standards SoftwareX. 
