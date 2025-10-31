// Chart.js configuration and utilities for MGNREGA Dashboard
class MGNREGACharts {
    constructor() {
        this.colors = {
            primary: '#2c5aa0',
            secondary: '#34a853',
            accent: '#fbbc05',
            danger: '#ea4335',
            info: '#4285f4',
            warning: '#f9ab00',
            sc: '#4caf50',
            st: '#2196f3',
            women: '#ff9800'
        };
        
        this.init();
    }

    init() {
        // Set global Chart.js configuration
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
    }

    createEmploymentChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [
                    'Households Employed - परिवारों को रोजगार - રોજગારી મળેલા ઘરગથ્થુઓ',
                    'Persons Worked - काम किए व्यक्ति - કામ કરનાર વ્યક્તિઓ', 
                    'Total Person Days - कुल व्यक्ति दिवस - કુલ વ્યક્તિ દિવસ'
                ],
                datasets: [
                    {
                        label: 'Your District - आपका जिला - તમારો જિલ્લો',
                        data: [
                            data.district.households_provided_employment,
                            data.district.persons_worked,
                            data.district.total_person_days
                        ],
                        backgroundColor: this.colors.primary,
                        borderColor: this.colors.primary,
                        borderWidth: 1
                    },
                    {
                        label: 'State Average - राज्य औसत - રાજ્ય સરેરાશ',
                        data: [
                            data.state_avg.households_provided_employment,
                            data.state_avg.persons_worked,
                            data.state_avg.total_person_days
                        ],
                        backgroundColor: this.colors.secondary,
                        borderColor: this.colors.secondary,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            padding: 20,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                if (value >= 1000000) {
                                    return `${context.dataset.label}: ${(value / 1000000).toFixed(2)}M`;
                                } else if (value >= 1000) {
                                    return `${context.dataset.label}: ${(value / 1000).toFixed(1)}K`;
                                }
                                return `${context.dataset.label}: ${value}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                if (value >= 1000000) {
                                    return (value / 1000000).toFixed(1) + 'M';
                                } else if (value >= 1000) {
                                    return (value / 1000).toFixed(0) + 'K';
                                }
                                return value;
                            }
                        }
                    }
                }
            }
        });
    }

    createSocialCategoryChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const totalDays = data.total_person_days;
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [
                    'SC - अनुसूचित जाति - અનુસૂચિત જાતિ',
                    'ST - अनुसूचित जनजाति - અનુસૂચિત જનજાતિ', 
                    'Women - महिला - મહિલા',
                    'Others - अन्य - અન્ય'
                ],
                datasets: [{
                    data: [
                        data.sc_person_days,
                        data.st_person_days,
                        data.women_person_days,
                        totalDays - (data.sc_person_days + data.st_person_days + data.women_person_days)
                    ],
                    backgroundColor: [
                        this.colors.sc,
                        this.colors.st,
                        this.colors.women,
                        this.colors.info
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                const percentage = ((value / totalDays) * 100).toFixed(1);
                                return `${context.label}: ${value.toLocaleString()} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '50%'
            }
        });
    }

    createExpenditureChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Total Expenditure - कुल व्यय - કુલ ખર્ચ'],
                datasets: [
                    {
                        label: 'Your District - आपका जिला - તમારો જિલ્લો',
                        data: [data.district.total_expenditure],
                        backgroundColor: this.colors.primary
                    },
                    {
                        label: 'State Average - राज्य औसत - રાજ્ય સરેરાશ',
                        data: [data.state_avg.expenditure_per_person * data.district.persons_worked],
                        backgroundColor: this.colors.secondary
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                if (value >= 10000000) {
                                    return `${context.dataset.label}: ₹${(value / 10000000).toFixed(2)} Cr`;
                                } else if (value >= 100000) {
                                    return `${context.dataset.label}: ₹${(value / 100000).toFixed(2)} L`;
                                }
                                return `${context.dataset.label}: ₹${value.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                if (value >= 10000000) {
                                    return '₹' + (value / 10000000).toFixed(1) + 'Cr';
                                } else if (value >= 100000) {
                                    return '₹' + (value / 100000).toFixed(0) + 'L';
                                }
                                return '₹' + value;
                            }
                        }
                    }
                }
            }
        });
    }

    createWorksCompletionChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const completionRate = (data.works_completed / data.works_taken_up) * 100;
        const pendingRate = 100 - completionRate;
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [
                    'Completed - पूर्ण - પૂર્ણ',
                    'Pending - लंबित - બાકી'
                ],
                datasets: [{
                    data: [completionRate, pendingRate],
                    backgroundColor: [this.colors.success, this.colors.warning],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.raw.toFixed(1)}%`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    createMonthlyTrendChart(canvasId, monthlyData) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: monthlyData.months,
                datasets: [{
                    label: 'Person Days - व्यक्ति दिवस - વ્યક્તિ દિવસ',
                    data: monthlyData.personDays,
                    borderColor: this.colors.primary,
                    backgroundColor: this.hexToRgba(this.colors.primary, 0.1),
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                if (value >= 1000000) {
                                    return (value / 1000000).toFixed(1) + 'M';
                                } else if (value >= 1000) {
                                    return (value / 1000).toFixed(0) + 'K';
                                }
                                return value;
                            }
                        }
                    }
                }
            }
        });
    }

    createPerformanceRadarChart(canvasId, metrics) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'radar',
            data: {
                labels: [
                    'Employment - रोजगार - રોજગાર',
                    'Women Participation - महिला भागीदारी - મહિલા ભાગીદારી',
                    'Works Completion - कार्य पूर्णता - કામ પૂર્ણતા',
                    'Expenditure Efficiency - व्यय दक्षता - ખર્ચ કાર્યક્ષમતા',
                    'SC/ST Participation - अनुसूचित जाति/जनजाति भागीदारी - અનુસૂચિત જાતિ/જનજાતિ ભાગીદારી'
                ],
                datasets: [
                    {
                        label: 'Your District - आपका जिला - તમારો જિલ્લો',
                        data: metrics.district,
                        backgroundColor: this.hexToRgba(this.colors.primary, 0.2),
                        borderColor: this.colors.primary,
                        pointBackgroundColor: this.colors.primary
                    },
                    {
                        label: 'State Average - राज्य औसत - રાજ્ય સરેરાશ',
                        data: metrics.stateAvg,
                        backgroundColor: this.hexToRgba(this.colors.secondary, 0.2),
                        borderColor: this.colors.secondary,
                        pointBackgroundColor: this.colors.secondary
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Utility function to convert hex to rgba
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // Method to destroy charts when needed
    destroyChart(chart) {
        if (chart) {
            chart.destroy();
        }
    }

    // Method to update chart data
    updateChart(chart, newData) {
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.mgnregaCharts = new MGNREGACharts();
    
    // Auto-initialize charts if data attributes are present
    const chartElements = document.querySelectorAll('[data-chart-type]');
    chartElements.forEach(element => {
        const chartType = element.getAttribute('data-chart-type');
        const chartData = element.getAttribute('data-chart-data');
        
        if (chartData) {
            try {
                const data = JSON.parse(chartData);
                switch(chartType) {
                    case 'employment':
                        window.mgnregaCharts.createEmploymentChart(element.id, data);
                        break;
                    case 'social-category':
                        window.mgnregaCharts.createSocialCategoryChart(element.id, data);
                        break;
                    case 'expenditure':
                        window.mgnregaCharts.createExpenditureChart(element.id, data);
                        break;
                    case 'works-completion':
                        window.mgnregaCharts.createWorksCompletionChart(element.id, data);
                        break;
                }
            } catch (error) {
                console.error('Error initializing chart:', error);
            }
        }
    });
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MGNREGACharts;
}