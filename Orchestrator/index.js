const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { connect, StringCodec } = require('nats');
const workflowEngine = require('./workflow');

const app = express();
const port = 3100;

app.use(cors());
app.use(bodyParser.json());

// Connexion NATS (simulée pour l'instant si pas de serveur)
async function startNats() {
    try {
        const nc = await connect({ servers: "localhost:4222" });
        console.log("Connected to NATS");
        return nc;
    } catch (err) {
        console.log("NATS connection failed (is NATS server running?):", err.message);
        return null; // On continue sans NATS pour le dev
    }
}

let natsClient = null;
startNats().then(nc => natsClient = nc);

app.get('/', (req, res) => {
    res.json({ service: 'Orchestrator', status: 'active' });
});

app.post('/pipeline/execute', async (req, res) => {
    const pipelineDef = req.body;

    if (!pipelineDef) {
        return res.status(400).json({ error: "Pipeline definition required" });
    }

    try {
        const executionId = await workflowEngine.startPipeline(pipelineDef, natsClient);
        res.json({
            executionId: executionId,
            status: "started",
            message: "Pipeline execution started"
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: "Failed to start pipeline", details: err.message });
    }
});

app.get('/status/:id', (req, res) => {
    const status = workflowEngine.getStatus(req.params.id);
    if (!status) return res.status(404).json({ error: "Execution ID not found" });
    res.json(status);
});

app.listen(port, () => {
    console.log(`Orchestrator running on http://localhost:${port}`);
});
