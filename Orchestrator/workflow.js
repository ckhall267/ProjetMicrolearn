const { v4: uuidv4 } = require('uuid');

// Stockage en mémoire pour le prototype
const executions = {};

exports.startPipeline = async (pipelineDef, natsClient) => {
    const executionId = uuidv4();

    executions[executionId] = {
        id: executionId,
        definition: pipelineDef,
        status: 'running',
        startTime: new Date(),
        steps: [],
        logs: []
    };

    // Simulation d'exécution asynchrone
    simulateExecution(executionId);

    return executionId;
};

exports.getStatus = (id) => {
    return executions[id];
};

async function simulateExecution(id) {
    const job = executions[id];
    console.log(`[Job ${id}] Starting simulation...`);

    // Exemple d'étapes simulées
    const steps = ['DataPreparation', 'ModelSelection', 'Training', 'Evaluation'];

    for (const step of steps) {
        await new Promise(r => setTimeout(r, 2000)); // Wait 2s
        job.steps.push({ name: step, status: 'completed', timestamp: new Date() });
        job.logs.push(`Step ${step} completed successfully.`);
    }

    job.status = 'completed';
    job.endTime = new Date();
    console.log(`[Job ${id}] Completed.`);
}
