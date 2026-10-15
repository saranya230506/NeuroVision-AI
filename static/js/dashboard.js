/**
 * NeuroVision AI - Analytics & Dashboard Charts Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  const distributionCanvas = document.getElementById('classDistributionChart');
  const confidenceCanvas = document.getElementById('confidenceBarChart');

  if (!distributionCanvas) return;

  function isDarkMode() {
    return document.documentElement.getAttribute('data-theme') === 'dark';
  }

  function getChartColors() {
    const dark = isDarkMode();
    return {
      text: dark ? '#cbd5e1' : '#475569',
      grid: dark ? '#334155' : '#e2e8f0',
      classes: {
        glioma: '#ef4444',
        meningioma: '#f59e0b',
        notumor: '#10b981',
        pituitary: '#06b6d4'
      }
    };
  }

  // Fetch live stats from API
  fetch('/api/stats')
    .then(res => res.json())
    .then(data => {
      if (!data.success) return;
      initCharts(data.stats);
    })
    .catch(err => console.error('Error fetching dashboard stats:', err));

  let distChart = null;
  let confChart = null;

  function initCharts(stats) {
    const colors = getChartColors();
    const classCounts = stats.class_counts || {
      'Glioma': 0, 'Meningioma': 0, 'No Tumor': 0, 'Pituitary': 0
    };

    // 1. Class Distribution Doughnut Chart
    if (distributionCanvas) {
      const ctx = distributionCanvas.getContext('2d');
      distChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary'],
          datasets: [{
            data: [
              classCounts['Glioma'] || 0,
              classCounts['Meningioma'] || 0,
              classCounts['No Tumor'] || 0,
              classCounts['Pituitary'] || 0
            ],
            backgroundColor: [
              colors.classes.glioma,
              colors.classes.meningioma,
              colors.classes.notumor,
              colors.classes.pituitary
            ],
            borderColor: isDarkMode() ? '#111827' : '#ffffff',
            borderWidth: 2,
            hoverOffset: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: colors.text,
                font: { family: 'Inter', size: 12, weight: 600 },
                padding: 16
              }
            },
            tooltip: {
              callbacks: {
                label: function (ctx) {
                  const val = ctx.raw || 0;
                  const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                  const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                  return ` ${ctx.label}: ${val} scans (${pct}%)`;
                }
              }
            }
          },
          cutout: '68%'
        }
      });
    }

    // 2. Class Volume Bar Chart
    if (confidenceCanvas) {
      const ctx2 = confidenceCanvas.getContext('2d');
      confChart = new Chart(ctx2, {
        type: 'bar',
        data: {
          labels: ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary'],
          datasets: [{
            label: 'Total Diagnosed Cases',
            data: [
              classCounts['Glioma'] || 0,
              classCounts['Meningioma'] || 0,
              classCounts['No Tumor'] || 0,
              classCounts['Pituitary'] || 0
            ],
            backgroundColor: [
              'rgba(239, 68, 68, 0.75)',
              'rgba(245, 158, 11, 0.75)',
              'rgba(16, 185, 129, 0.75)',
              'rgba(6, 182, 212, 0.75)'
            ],
            borderRadius: 8,
            borderWidth: 1,
            borderColor: [
              colors.classes.glioma,
              colors.classes.meningioma,
              colors.classes.notumor,
              colors.classes.pituitary
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: { color: colors.text, precision: 0 },
              grid: { color: colors.grid }
            },
            x: {
              ticks: { color: colors.text, font: { weight: 600 } },
              grid: { display: false }
            }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }
  }

  // Handle Theme Change updates for Chart.js
  window.addEventListener('neurovision-theme-changed', () => {
    const colors = getChartColors();
    if (distChart) {
      distChart.options.plugins.legend.labels.color = colors.text;
      distChart.data.datasets[0].borderColor = isDarkMode() ? '#111827' : '#ffffff';
      distChart.update();
    }
    if (confChart) {
      confChart.options.scales.x.ticks.color = colors.text;
      confChart.options.scales.y.ticks.color = colors.text;
      confChart.options.scales.y.grid.color = colors.grid;
      confChart.update();
    }
  });

});
