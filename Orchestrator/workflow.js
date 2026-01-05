const { v4: uuidv4 } = require('uuid');
const axios = require('axios');
const { createClient } = require('redis');

// Configuration des services
const SERVICES = {
    DATA_PREPARER: process.env.DATA_PREPARER_URL || 'http://localhost:8000/api/v1',
    MODEL_SELECTOR: process.env.MODEL_SELECTOR_URL || 'http://localhost:8001/api/v1',
    TRAINER: process.env.TRAINER_URL || 'http://localhost:8002/api/v1',
    EVALUATOR: process.env.EVALUATOR_URL || 'http://localhost:8003/api/v1'
};

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';

// Client Redis
let redisClient;
(async () => {
    redisClient = createClient({ url: REDIS_URL });
    redisClient.on('error', (err) => console.error('Redis Client Error', err));
    await redisClient.connect();
})();

async function saveJobState(id, job) {
    if (redisClient && redisClient.isOpen) {
        await redisClient.set(`pipeline:${id}`, JSON.stringify(job), { EX: 86400 });
    }
}

async function getJobState(id) {
    if (redisClient && redisClient.isOpen) {
        const data = await redisClient.get(`pipeline:${id}`);
        return data ? JSON.parse(data) : null;
    }
    return null;
}

exports.startPipeline = async (pipelineDef, natsClient) => {
    const executionId = uuidv4();
    const job = {
        id: executionId,
        definition: pipelineDef,
        status: 'running',
        startTime: new Date(),
        steps: [],
        logs: [],
        artifacts: {}
    };

    await saveJobState(executionId, job);

    // Indexer l'ID dans un Set pour pouvoir lister l'historique
    if (redisClient && redisClient.isOpen) {
        await redisClient.sAdd('pipelines:index', executionId);
    }

    executePipeline(executionId);
    return executionId;
};

exports.listPipelines = async () => {
    if (!redisClient || !redisClient.isOpen) return [];

    try {
        const ids = await redisClient.sMembers('pipelines:index');
        const pipelines = [];

        // Récupérer les détails pour chaque ID (pourrait être optimisé avec MGET si on change la structure)
        for (const id of ids) {
            const job = await getJobState(id);
            if (job) {
                // On retourne une version allégée pour la liste
                pipelines.push({
                    id: job.id,
                    dataset_id: job.definition?.dataset_id,
                    status: job.status,
                    startTime: job.startTime,
                    endTime: job.endTime,
                    error: job.error,
                    model_count: job.definition?.models?.length || 0
                });
            }
        }

        // Trier par date décroissante
        return pipelines.sort((a, b) => new Date(b.startTime) - new Date(a.startTime));
    } catch (err) {
        console.error("Error listing pipelines:", err);
        return [];
    }
};

exports.getStatus = async (id) => {
    return await getJobState(id);
};

async function executePipeline(id) {
    let job = await getJobState(id);
    if (!job) return;

    const log = async (msg) => {
        const logMsg = `[${new Date().toISOString()}] ${msg}`;
        console.log(`[Job ${id}] ${msg}`);
        job.logs.push(logMsg);
        await saveJobState(id, job);
    };

    const recordStep = async (name, status) => {
        job.steps.push({ name, status, timestamp: new Date() });
        await saveJobState(id, job);
    };

    const def = job.definition;
    log(`Starting pipeline execution for dataset: ${def.dataset_id || 'unknown'}`);

    try {
        // 1. Data Preparation
        log('Step 1: Data Preparation starting...');
        const prepResult = await executeDataPreparation(def.dataset_path, def.config.preprocessing);

        job.artifacts.dataset_id = prepResult.dataset_id;
        job.artifacts.cleaned_dataset_path = prepResult.cleaned_dataset_path;

        await recordStep('DataPreparation', 'completed');
        log(`Data Preparation done. Cleaned path: ${prepResult.cleaned_dataset_path}`);

        // 2. Model Selection
        let selectedModels = def.models;
        if (!selectedModels || selectedModels.length === 0) {
            log('Step 2: Model Selection starting...');
            // Attention: ModelSelector attend le path local/minio
            const selectionResult = await executeModelSelection(
                job.artifacts.dataset_id,
                job.artifacts.cleaned_dataset_path,
                def.target_column,
                def.task_type
            );
            selectedModels = selectionResult.selected_models.map(m => m.name || m.model_name).slice(0, 3);
            await recordStep('ModelSelection', 'completed');
            log(`Model Selection done. Selected: ${selectedModels.join(', ')}`);
        } else {
            log(`Using user selected models: ${selectedModels.join(', ')}`);
            await recordStep('ModelSelection', 'skipped');
        }

        // 3. Training
        log('Step 3: Training starting...');
        const trainingResults = [];
        for (const modelName of selectedModels) {
            log(`Training model: ${modelName}...`);
            // Trainer attend: model_name, dataset_path, target_column, hyperparameters
            const trainResult = await executeTraining({
                model_name: modelName,
                dataset_path: job.artifacts.cleaned_dataset_path,
                target_column: def.target_column,
                hyperparameters: def.config.hyperparameters || {}
            });

            // Attendre la fin du job si asynchrone ? 
            // Trainer retourne { job_id, status: "submitted" }
            // Il faudrait faire du polling ici. Pour simplifier ce code, on suppose que le Trainer est synchrone ou on attend un peu.
            // MAIS mon implémentation Trainer lance en BackgroundTasks.
            // Donc ici il faut faire du polling sur /train/{job_id}

            const finalTrainStatus = await pollTrainingCompletion(trainResult.job_id);
            trainingResults.push({ model: modelName, job_id: trainResult.job_id, ...finalTrainStatus });
        }
        job.artifacts.training_results = trainingResults;
        await recordStep('Training', 'completed');

        // 4. Evaluation
        log('Step 4: Evaluation starting...');
        const evaluationResults = [];
        for (const trainRes of trainingResults) {
            log(`Debug check trainRes: ${JSON.stringify(trainRes)}`);
            if (trainRes.status === 'completed' && trainRes.model_path) {
                // Evaluator attend: model_path, dataset_path, target_column
                const evalResult = await executeEvaluation({
                    model_path: trainRes.model_path,
                    dataset_path: job.artifacts.cleaned_dataset_path, // Sur jeu de test idéalement
                    target_column: def.target_column
                });
                evaluationResults.push(evalResult);
            }
        }
        job.artifacts.evaluation_results = evaluationResults;
        await recordStep('Evaluation', 'completed');

        job.status = 'completed';
        job.endTime = new Date();
        log('Pipeline execution finished successfully.');
        await saveJobState(id, job);

    } catch (error) {
        console.error(`Pipeline ${id} failed:`, error.message);
        job.status = 'failed';
        job.error = error.message;
        job.endTime = new Date();
        log(`Pipeline failed: ${error.message}`);
        await saveJobState(id, job);
    }
}

// --- API Calls ---

async function executeDataPreparation(filePath, config) {
    // Si config est simplement "true" ou vide, on utilise un pipeline par défaut
    let pipelinePayload = config;

    if (config === true || !config || (typeof config === 'object' && !config.steps)) {
        pipelinePayload = {
            steps: [
                { name: "imputation", strategy: "mean" },
                { name: "scaling", method: "standard" },
                { name: "one_hot_encoding", columns: [] } // Auto-detect
            ]
        };
    }

    const res = await axios.post(`${SERVICES.DATA_PREPARER}/prepare`, {
        file_path: filePath,
        pipeline: pipelinePayload
    });
    return res.data;
}

async function executeModelSelection(datasetId, datasetPath, targetCol, taskType) {
    const res = await axios.post(`${SERVICES.MODEL_SELECTOR}/select`, {
        dataset_id: datasetId,
        dataset_path: datasetPath,
        target_column: targetCol,
        task_type: taskType
    });
    return res.data;
}

async function executeTraining(payload) {
    const res = await axios.post(`${SERVICES.TRAINER}/train`, payload);
    return res.data;
}

async function startPolling(url, checkFn, timeoutMs = 300000) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
        try {
            const res = await axios.get(url);
            if (checkFn(res.data)) return res.data;
        } catch (e) {
            console.warn(`Polling error: ${e.message}`);
        }
        await new Promise(r => setTimeout(r, 2000));
    }
    throw new Error("Polling timeout");
}

async function pollTrainingCompletion(jobId) {
    return startPolling(
        `${SERVICES.TRAINER}/train/${jobId}`,
        (data) => data.status === 'completed' || data.status === 'failed'
    );
}

async function executeEvaluation(payload) {
    const res = await axios.post(`${SERVICES.EVALUATOR}/evaluate`, payload);
    return res.data;
}
