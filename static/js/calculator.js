document.addEventListener('DOMContentLoaded', () => {
    // Current calculator values cache for audit history saves
    let lastCalculation = { total: 0, energy: 0, transport: 0, diet: 0, waste: 0 };

    // --- SLIDER VALUE UPDATERS ---
    const sliders = document.querySelectorAll('.range-slider');
    sliders.forEach(slider => {
        const valSpan = document.getElementById(`${slider.id}-val`);
        if (valSpan) {
            slider.addEventListener('input', () => {
                valSpan.textContent = slider.value;
                calculateFootprint();
            });
        }
    });

    // Handle select drop-downs triggers
    const selectElements = document.querySelectorAll('.form-input');
    selectElements.forEach(select => {
        select.addEventListener('change', calculateFootprint);
    });

    // --- CHART.JS INITIALIZATION ---
    let breakdownChart = null;
    const ctx = document.getElementById('breakdown-chart');

    function renderBreakdownChart(energy, transport, diet, waste) {
        const data = {
            labels: ['Home Energy', 'Transport', 'Diet', 'Waste & Lifestyle'],
            datasets: [{
                data: [energy, transport, diet, waste],
                backgroundColor: [
                    '#059669', // Emerald
                    '#10b981', // Mint
                    '#d97706', // Terracotta
                    '#6366f1'  // Indigo
                ],
                borderWidth: 1,
                borderColor: '#ffffff',
                hoverOffset: 6
            }]
        };

        const config = {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#1c2d24',
                            font: {
                                family: 'Inter',
                                size: 11
                            },
                            padding: 10
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed !== undefined) {
                                    label += context.parsed.toFixed(2) + ' Tons CO2e';
                                }
                                return label;
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        };

        if (breakdownChart) {
            breakdownChart.destroy();
        }
        
        if (ctx) {
            breakdownChart = new Chart(ctx, config);
        }
    }

    // --- CALCULATOR CALCULATION ---
    const calcForm = document.getElementById('carbon-calculator-form');
    if (calcForm) {
        calcForm.addEventListener('submit', (e) => {
            e.preventDefault();
            calculateFootprint();
        });
    }

    // Initialize global metrics variables
    let currentMetrics = {
        elec: 280,
        gas: 600,
        lpg: 0,
        carDist: 8000,
        carType: 'hybrid',
        transit: 4,
        flights: 10,
        dietType: 'average',
        trash: 15,
        recycling: 40
    };

    function calculateFootprint() {
        // Read inputs
        currentMetrics.elec = parseFloat(document.getElementById('energy-elec').value) || 0;
        currentMetrics.gas = parseFloat(document.getElementById('energy-gas').value) || 0;
        currentMetrics.lpg = parseFloat(document.getElementById('energy-lpg').value) || 0;
        currentMetrics.carDist = parseFloat(document.getElementById('trans-car').value) || 0;
        currentMetrics.carType = document.getElementById('trans-car-type').value;
        currentMetrics.transit = parseFloat(document.getElementById('trans-public').value) || 0;
        currentMetrics.flights = parseFloat(document.getElementById('trans-flights').value) || 0;
        currentMetrics.dietType = document.getElementById('diet-type').value;
        currentMetrics.trash = parseFloat(document.getElementById('waste-trash').value) || 0;
        currentMetrics.recycling = parseFloat(document.getElementById('waste-recycling').value) || 0;

        // Calculations (Annual tons CO2e)
        const energyTons = ((currentMetrics.elec * 12 * 0.207) + (currentMetrics.gas * 12 * 0.183) + (currentMetrics.lpg * 12 * 1.55)) / 1000;

        let carFactor = 0.17;
        if (currentMetrics.carType === 'diesel') carFactor = 0.16;
        else if (currentMetrics.carType === 'hybrid') carFactor = 0.10;
        else if (currentMetrics.carType === 'ev') carFactor = 0.04;
        
        const carTons = (currentMetrics.carDist * carFactor) / 1000;
        const transitTons = (currentMetrics.transit * 52 * 0.05) / 1000;
        const flightsTons = (currentMetrics.flights * 150) / 1000;
        const transportTons = carTons + transitTons + flightsTons;

        let dietTons = 2.1;
        if (currentMetrics.dietType === 'vegan') dietTons = 1.1;
        else if (currentMetrics.dietType === 'vegetarian') dietTons = 1.5;
        else if (currentMetrics.dietType === 'meat') dietTons = 3.3;

        const wasteTons = ((currentMetrics.trash * 52 * 0.5) * (1 - (currentMetrics.recycling / 100))) / 1000;

        const totalTons = energyTons + transportTons + dietTons + wasteTons;

        // Update UI footprint label
        const totalValEl = document.getElementById('result-total-val');
        if (totalValEl) {
            totalValEl.textContent = totalTons.toFixed(2);
        }

        // Save footprint state for cross-page weather simulation consistency
        localStorage.setItem('userCarbonFootprint', totalTons);
        if (window.rainSimulator) {
            window.rainSimulator.setIntensity(totalTons);
        }

        // Fill Progress Bar
        const comparisonFill = document.getElementById('comparison-fill');
        if (comparisonFill) {
            const percentage = Math.min((totalTons / 10.0) * 100, 100);
            comparisonFill.style.width = `${percentage}%`;
            
            const labelEl = document.getElementById('comparison-label');
            if (labelEl) {
                if (totalTons <= 2.0) {
                    labelEl.innerHTML = '<span style="color: var(--index-low);">Target Achieved! Net-Zero Compliant (&lt; 2T)</span>';
                } else if (totalTons <= 4.5) {
                    labelEl.innerHTML = '<span style="color: var(--index-moderate);">Moderate Footprint (Below Global Average)</span>';
                } else {
                    labelEl.innerHTML = '<span style="color: var(--index-high);">High Footprint (Above Global Average)</span>';
                }
            }
        }

        // Render Breakdown Chart
        renderBreakdownChart(energyTons, transportTons, dietTons, wasteTons);

        // Highlight Highest Category
        updateDynamicRecommendations(energyTons, transportTons, dietTons, wasteTons);

        // Recalculate and update the solutions sub-label math formulas live
        updateSolutionsSublabels();

        // Save variables for history logs
        lastCalculation = {
            total: totalTons,
            energy: energyTons,
            transport: transportTons,
            diet: dietTons,
            waste: wasteTons
        };

        // Spawn a puff of floating leaves
        spawnPuff();
    }

    function updateDynamicRecommendations(energy, transport, diet, waste) {
        const recoBox = document.getElementById('dynamic-reco-box');
        if (!recoBox) return;

        const categories = [
            { name: 'Home Energy', value: energy, icon: '⚡', tips: [
                'Switch to LED lightbulbs to cut lighting energy usage by 75%.',
                'Unplug background appliances (phantom loads) when not in use.',
                'Improve home insulation and seal gaps around doors and windows.'
            ] },
            { name: 'Transport', value: transport, icon: '🚗', tips: [
                'Car pool or switch to walking/cycling for short trips under 3km.',
                'Maintain proper tire pressure to improve vehicle fuel efficiency by 3%.',
                'Limit short-haul flights and consider train options where available.'
            ] },
            { name: 'Diet', value: diet, icon: '🥗', tips: [
                'Adopt a meat-free day (e.g., Meatless Monday) to cut dietary emissions by 15%.',
                'Reduce food waste by planning meals and freezing leftovers.',
                'Source local and seasonal foods to minimize transportation footprint.'
            ] },
            { name: 'Waste & Lifestyle', value: waste, icon: '♻️', tips: [
                'Compost organic waste to prevent methane generation in landfills.',
                'Purchase secondhand items and avoid single-use plastics.',
                'Setup a dedicated waste separation system to maximize recycling.'
            ] }
        ];

        categories.sort((a, b) => b.value - a.value);
        const highest = categories[0];

        let html = `
            <div style="margin-top: 0.5rem;">
                <h4 style="font-size: 1.05rem; color: var(--accent); display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.6rem;">
                    <span>${highest.icon}</span> High Impact Area: Reduce ${highest.name}
                </h4>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">
                    Based on your inputs, <strong>${highest.name}</strong> is your leading source of emissions. Try implementing these targeted steps:
                </p>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.5rem;">
        `;

        highest.tips.forEach(tip => {
            html += `
                <li style="display: flex; gap: 0.5rem; font-size: 0.85rem; color: var(--text-primary); line-height: 1.4;">
                    <span style="color: var(--accent);">✔</span>
                    <span>${tip}</span>
                </li>
            `;
        });

        html += `
                </ul>
            </div>
        `;

        recoBox.innerHTML = html;
    }

    // --- MATHEMATICAL SAVINGS ENGINE FOR SOLUTIONS CHECKLIST ---
    function getFormulaSavings(actionId) {
        let savingVal = 0;
        let formulaStr = '';

        let carFactor = 0.17;
        if (currentMetrics.carType === 'diesel') carFactor = 0.16;
        else if (currentMetrics.carType === 'hybrid') carFactor = 0.10;
        else if (currentMetrics.carType === 'ev') carFactor = 0.04;

        switch (actionId) {
            case 'led':
                savingVal = (currentMetrics.elec * 12 * 0.08 * 0.207) / 1000;
                formulaStr = `(${currentMetrics.elec} kWh × 12 × 0.08 × 0.207) / 1000`;
                break;
            case 'thermostat':
                savingVal = (currentMetrics.gas * 12 * 0.10 * 0.183) / 1000;
                formulaStr = `(${currentMetrics.gas} kWh × 12 × 0.10 × 0.183) / 1000`;
                break;
            case 'heatpump':
                const gasBase = (currentMetrics.gas * 12 * 0.183) / 1000;
                const hpElectric = ((currentMetrics.gas * 12) / 3.0 * 0.207) / 1000;
                savingVal = Math.max(0, gasBase - hpElectric);
                formulaStr = `(${currentMetrics.gas} × 12 × 0.183) / 1000 - ((${currentMetrics.gas} × 12) / 3.0 × 0.207) / 1000`;
                break;
            case 'windows':
                savingVal = (currentMetrics.gas * 12 * 0.12 * 0.183) / 1000;
                formulaStr = `(${currentMetrics.gas} kWh × 12 × 0.12 × 0.183) / 1000`;
                break;
            case 'bike':
                savingVal = (currentMetrics.carDist * 0.20 * carFactor) / 1000;
                formulaStr = `(${currentMetrics.carDist} km × 0.20 × ${carFactor.toFixed(2)}) / 1000`;
                break;
            case 'ev':
                savingVal = Math.max(0, (currentMetrics.carDist * (carFactor - 0.04)) / 1000);
                formulaStr = `(${currentMetrics.carDist} km × (${carFactor.toFixed(2)} - 0.04)) / 1000`;
                break;
            case 'flight':
                savingVal = 0.25;
                formulaStr = `0.25 Tons (Static Estimate)`;
                break;
            case 'tires':
                savingVal = (currentMetrics.carDist * 0.03 * carFactor) / 1000;
                formulaStr = `(${currentMetrics.carDist} km × 0.03 × ${carFactor.toFixed(2)}) / 1000`;
                break;
            case 'plantdiet':
                let currentDietVal = 2.1;
                if (currentMetrics.dietType === 'vegan') currentDietVal = 1.1;
                else if (currentMetrics.dietType === 'vegetarian') currentDietVal = 1.5;
                else if (currentMetrics.dietType === 'meat') currentDietVal = 3.3;
                savingVal = Math.max(0, currentDietVal - 1.1);
                formulaStr = `${currentDietVal.toFixed(1)} T (Current) - 1.1 T (Vegan Target)`;
                break;
            case 'meatfree':
                let dietBase = 2.1;
                if (currentMetrics.dietType === 'vegan') dietBase = 1.1;
                else if (currentMetrics.dietType === 'vegetarian') dietBase = 1.5;
                else if (currentMetrics.dietType === 'meat') dietBase = 3.3;
                savingVal = Math.max(0, (dietBase - 1.5) * (1 / 7));
                formulaStr = `(${dietBase.toFixed(1)} T - 1.5 T) × 1/7 Week`;
                break;
            case 'foodwaste':
                savingVal = 0.15;
                formulaStr = `0.15 Tons (Static Estimate)`;
                break;
            case 'localfood':
                savingVal = 0.10;
                formulaStr = `0.10 Tons (Static Estimate)`;
                break;
            case 'compost':
                savingVal = (currentMetrics.trash * 52 * 0.5 * 0.30) / 1000;
                formulaStr = `(${currentMetrics.trash} kg × 52 × 0.5 × 0.30) / 1000`;
                break;
            case 'plastics':
                savingVal = 0.08;
                formulaStr = `0.08 Tons (Static Estimate)`;
                break;
            case 'sorting':
                savingVal = (currentMetrics.trash * 52 * 0.5 * 0.20) / 1000;
                formulaStr = `(${currentMetrics.trash} kg × 52 × 0.5 × 0.20) / 1000`;
                break;
            case 'secondhand':
                savingVal = 0.18;
                formulaStr = `0.18 Tons (Static Estimate)`;
                break;
        }

        return { val: savingVal, formula: formulaStr };
    }

    // Map checkboxes to formula actions
    const checkboxMap = {
        0: 'led',
        1: 'thermostat',
        2: 'heatpump',
        3: 'windows',
        4: 'bike',
        5: 'ev',
        6: 'flight',
        7: 'tires',
        8: 'plantdiet',
        9: 'meatfree',
        10: 'foodwaste',
        11: 'localfood',
        12: 'compost',
        13: 'plastics',
        14: 'sorting',
        15: 'secondhand'
    };

    function updateSolutionsSublabels() {
        const checkboxes = document.querySelectorAll('.sol-checkbox');
        checkboxes.forEach((cb, index) => {
            const actionId = checkboxMap[index];
            if (actionId) {
                const calcResult = getFormulaSavings(actionId);
                cb.dataset.savings = calcResult.val;
                
                let labelContainer = cb.parentNode.querySelector('.sol-savings');
                if (labelContainer) {
                    labelContainer.innerHTML = `
                        Saves ${calcResult.val.toFixed(2)} Tons CO₂e
                        <div style="font-family: monospace; font-size: 0.65rem; color: var(--text-muted); margin-top: 0.15rem; font-weight: normal;">
                            Math: ${calcResult.formula}
                        </div>
                    `;
                }
            }
        });
        updateSavingsCounter();
    }

    // --- CHECKLIST CARBON SAVINGS TRACKER ---
    const savingsValEl = document.getElementById('savings-total-val');
    const checkboxes = document.querySelectorAll('.sol-checkbox');
    
    if (checkboxes.length > 0 && savingsValEl) {
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateSavingsCounter);
        });
    }

    function updateSavingsCounter() {
        let totalSavings = 0;
        const activeCheckboxes = document.querySelectorAll('.sol-checkbox:checked');
        activeCheckboxes.forEach(cb => {
            totalSavings += parseFloat(cb.dataset.savings) || 0;
        });
        
        if (savingsValEl) {
            savingsValEl.textContent = totalSavings.toFixed(2);
        }
    }

    // --- LEAF SMOKE PARTICLE SPARKER ---
    function spawnLeafSmoke() {
        const container = document.getElementById('gauge-container');
        if (!container) return;

        // Check if gauge container is visible in viewport
        const rect = container.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;

        const leaf = document.createElement('span');
        leaf.className = 'leaf-smoke';
        
        const leaves = ['🍃', '🌱', '🌿', '☘️'];
        leaf.textContent = leaves[Math.floor(Math.random() * leaves.length)];

        // Random offset and rotation properties
        const randomX = Math.floor(Math.random() * 80) - 40;
        const randomRot = Math.floor(Math.random() * 180) + 90;
        
        leaf.style.setProperty('--random-x', `${randomX}px`);
        leaf.style.setProperty('--random-rot', `${randomRot}deg`);

        // Spawn position (approx bottom center of gauge circle)
        leaf.style.left = `calc(50% - 10px)`;
        
        container.appendChild(leaf);

        // Remove element after animation
        setTimeout(() => {
            leaf.remove();
        }, 2800);
    }

    // Spawn a leaf every 1.5 seconds automatically
    setInterval(spawnLeafSmoke, 1500);

    // Spawn a small puff of leaves on recalculation
    function spawnPuff() {
        for (let i = 0; i < 3; i++) {
            setTimeout(spawnLeafSmoke, i * 250);
        }
    }

    // --- CARBON AUDIT HISTORY TRACKING ---
    let historyChart = null;

    function renderHistoryTrendChart(audits) {
        const ctxHist = document.getElementById('history-trend-chart');
        if (!ctxHist) return;
        
        // Sort chronologically by date
        const sorted = [...audits].sort((a, b) => new Date(a.date) - new Date(b.date));
        const labels = sorted.map(a => {
            const d = new Date(a.date);
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
        });
        const dataValues = sorted.map(a => a.total);
        
        if (historyChart) {
            historyChart.destroy();
        }
        
        historyChart = new Chart(ctxHist, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Carbon Footprint',
                    data: dataValues,
                    borderColor: '#059669',
                    backgroundColor: 'rgba(5, 150, 105, 0.06)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    pointRadius: 4.5,
                    pointBackgroundColor: '#059669',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 1.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#3d4f45', font: { family: 'Inter', size: 9 } }
                    },
                    y: {
                        min: 0,
                        grid: { color: 'rgba(5, 150, 105, 0.05)' },
                        ticks: { color: '#3d4f45', font: { family: 'Inter', size: 9 } }
                    }
                }
            }
        });
    }

    function loadAuditHistory() {
        const auditsList = document.getElementById('saved-audits-list');
        const historyPanel = document.getElementById('history-panel');
        if (!auditsList) return;
        
        const stored = localStorage.getItem('atmosync_audits');
        const audits = stored ? JSON.parse(stored) : [];
        
        if (audits.length === 0) {
            if (historyPanel) historyPanel.style.display = 'none';
            auditsList.innerHTML = '<div style="color: var(--text-muted); font-size: 0.8rem; text-align: center; margin: auto; padding: 1rem;">No saved entries yet. Click "Save Progress" to log your current audit.</div>';
            return;
        }
        
        if (historyPanel) historyPanel.style.display = 'block';
        
        // Sort newest first
        const listAudits = [...audits].sort((a, b) => new Date(b.date) - new Date(a.date));
        
        auditsList.innerHTML = '';
        listAudits.forEach(a => {
            const dateStr = new Date(a.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
            auditsList.innerHTML += `
                <div style="background: #ffffff; border: 1px solid rgba(5,150,105,0.08); padding: 0.65rem 0.8rem; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; box-shadow: var(--shadow-sm); margin-bottom: 0.25rem;">
                    <div>
                        <div style="font-weight: 700; color: var(--text-primary);">${a.total.toFixed(2)} Tons CO₂e</div>
                        <div style="font-size: 0.7rem; color: var(--text-muted);">${dateStr}</div>
                    </div>
                    <div style="display: flex; gap: 0.4rem; font-size: 0.65rem; color: var(--text-secondary); background: var(--accent-sage); padding: 0.15rem 0.4rem; border-radius: 4px; font-weight: 600;">
                        <span>E: ${a.breakdown.energy.toFixed(1)}</span>
                        <span>T: ${a.breakdown.transport.toFixed(1)}</span>
                        <span>D: ${a.breakdown.diet.toFixed(1)}</span>
                    </div>
                </div>
            `;
        });
        
        // Re-draw chart (wrapping in a short timeout to let tab transition render correctly)
        setTimeout(() => {
            renderHistoryTrendChart(audits);
        }, 100);
    }

    // Save current calculations to history
    const saveBtn = document.getElementById('save-audit-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            const stored = localStorage.getItem('atmosync_audits');
            const audits = stored ? JSON.parse(stored) : [];
            
            const newAudit = {
                id: Date.now(),
                date: new Date().toISOString(),
                total: lastCalculation.total,
                breakdown: {
                    energy: lastCalculation.energy,
                    transport: lastCalculation.transport,
                    diet: lastCalculation.diet,
                    waste: lastCalculation.waste
                }
            };
            
            audits.push(newAudit);
            localStorage.setItem('atmosync_audits', JSON.stringify(audits));
            loadAuditHistory();
            
            // Visual feedback on save button
            const originalHTML = saveBtn.innerHTML;
            saveBtn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Saved!';
            saveBtn.style.background = 'var(--accent-mint)';
            setTimeout(() => {
                saveBtn.innerHTML = originalHTML;
                saveBtn.style.background = '';
            }, 1200);
        });
    }

    // Clear history logs
    const clearBtn = document.getElementById('clear-history-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (confirm("Are you sure you want to delete all saved carbon audits?")) {
                localStorage.removeItem('atmosync_audits');
                loadAuditHistory();
            }
        });
    }

    // Export report printable page
    const printBtn = document.getElementById('print-report-btn');
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            const printWindow = window.open('', '_blank');
            const dateStr = new Date().toLocaleDateString('en-US', { 
                year: 'numeric', month: 'long', day: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
            
            const html = `
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Atmo Sync - Carbon Audit Certificate</title>
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Plus+Jakarta+Sans:wght@700;800&display=swap');
                        body {
                            font-family: 'Inter', sans-serif;
                            background: #ffffff;
                            color: #1c2d24;
                            padding: 3rem;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 80vh;
                        }
                        .certificate {
                            border: 8px double #059669;
                            border-radius: 12px;
                            padding: 3rem;
                            max-width: 650px;
                            width: 100%;
                            text-align: center;
                            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
                            position: relative;
                        }
                        .certificate::before {
                            content: '🌱';
                            font-size: 3rem;
                            display: block;
                            margin-bottom: 1rem;
                        }
                        h1 {
                            font-family: 'Plus Jakarta Sans', sans-serif;
                            font-size: 2.2rem;
                            color: #059669;
                            margin: 0.5rem 0 1.5rem 0;
                            text-transform: uppercase;
                            letter-spacing: 1px;
                        }
                        .subtitle {
                            font-size: 1rem;
                            color: #3d4f45;
                            margin-bottom: 2rem;
                            line-height: 1.5;
                        }
                        .score-box {
                            background: #f0fdf4;
                            border: 1px solid rgba(5,150,105,0.2);
                            border-radius: 12px;
                            padding: 1.5rem;
                            margin: 2rem 0;
                            display: inline-block;
                        }
                        .score {
                            font-family: 'Plus Jakarta Sans', sans-serif;
                            font-size: 3.5rem;
                            font-weight: 800;
                            color: #059669;
                            line-height: 1;
                        }
                        .unit {
                            font-size: 0.85rem;
                            color: #3d4f45;
                            font-weight: 700;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;
                            margin-top: 0.5rem;
                        }
                        .breakdown-table {
                            width: 100%;
                            margin-top: 1.5rem;
                            border-collapse: collapse;
                            font-size: 0.9rem;
                        }
                        .breakdown-table th {
                            border-bottom: 2px solid #059669;
                            padding: 0.5rem;
                            color: #3d4f45;
                            font-weight: 700;
                        }
                        .breakdown-table td {
                            border-bottom: 1px solid #e2e8f0;
                            padding: 0.75rem 0.5rem;
                            color: #1c2d24;
                        }
                        .footer {
                            margin-top: 3rem;
                            font-size: 0.8rem;
                            color: #73857b;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            border-top: 1px dashed #e2e8f0;
                            padding-top: 1.5rem;
                        }
                        @media print {
                            body { padding: 0; }
                            .certificate { border-color: #059669 !important; box-shadow: none !important; }
                        }
                    </style>
                </head>
                <body>
                    <div class="certificate">
                        <h1>Carbon Footprint Audit</h1>
                        <p class="subtitle">This official statement verifies the calculated annual greenhouse gas emissions for the audited household, measured in metric tons of carbon dioxide equivalent (Tons CO₂e).</p>
                        
                        <div class="score-box">
                            <div class="score">${lastCalculation.total.toFixed(2)}</div>
                            <div class="unit">Tons CO₂e / Year</div>
                        </div>
                        
                        <table class="breakdown-table">
                            <thead>
                                <tr>
                                    <th align="left">Emission Source</th>
                                    <th align="right">Carbon Footprint</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td align="left">🏠 Home Energy</td>
                                    <td align="right">${lastCalculation.energy.toFixed(2)} Tons</td>
                                </tr>
                                <tr>
                                    <td align="left">🚗 Transport & Commuting</td>
                                    <td align="right">${lastCalculation.transport.toFixed(2)} Tons</td>
                                </tr>
                                <tr>
                                    <td align="left">🥗 Diet & Agriculture</td>
                                    <td align="right">${lastCalculation.diet.toFixed(2)} Tons</td>
                                </tr>
                                <tr>
                                    <td align="left">♻️ Waste & Disposal</td>
                                    <td align="right">${lastCalculation.waste.toFixed(2)} Tons</td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <div class="footer">
                            <div>Audit Date: ${dateStr}</div>
                            <div>Verified by Atmo Sync</div>
                        </div>
                    </div>
                    <script>
                        window.onload = function() {
                            window.print();
                        };
                    </script>
                </body>
                </html>
            `;
            printWindow.document.open();
            printWindow.document.write(html);
            printWindow.document.close();
        });
    }

    // Trigger initial calculation & history loads
    calculateFootprint();
    loadAuditHistory();

    // Redraw history trend chart if the tab is loaded or switched to
    document.addEventListener('tabChanged', () => {
        const stored = localStorage.getItem('atmosync_audits');
        const audits = stored ? JSON.parse(stored) : [];
        if (audits.length > 0) {
            setTimeout(() => {
                renderHistoryTrendChart(audits);
            }, 150);
        }
    });
});
