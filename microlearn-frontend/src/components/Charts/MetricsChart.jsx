import React from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const MetricsChart = ({ models, metrics = ['accuracy', 'f1', 'precision'] }) => {
    if (!models || models.length === 0) return null;

    const data = {
        labels: models.map(m => m.name),
        datasets: metrics.map((metric, index) => ({
            label: metric.charAt(0).toUpperCase() + metric.slice(1),
            data: models.map(m => m.metrics ? m.metrics[metric] : 0),
            backgroundColor: `rgba(${50 + index * 60}, ${99 + index * 30}, ${132 + index * 20}, 0.7)`,
            borderColor: `rgba(${50 + index * 60}, ${99 + index * 30}, ${132 + index * 20}, 1)`,
            borderWidth: 1,
        })),
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Comparaison des Performances des Modèles',
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += new Intl.NumberFormat('en-US', { style: 'percent', minimumFractionDigits: 2 }).format(context.parsed.y);
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 1
            }
        }
    };

    return <Bar options={options} data={data} />;
};

export default MetricsChart;
