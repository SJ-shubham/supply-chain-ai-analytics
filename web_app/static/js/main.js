// Supply Chain AI Platform JavaScript Engine

document.addEventListener('DOMContentLoaded', () => {

    // 1. Single Order Late Delivery Risk Prediction Form
    const lateRiskForm = document.getElementById('lateRiskForm');
    if (lateRiskForm) {
        lateRiskForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = lateRiskForm.querySelector('button[type="submit"]');
            btn.innerText = "Analyzing Risk...";
            btn.disabled = true;

            const payload = {
                scheduled_days: parseFloat(document.getElementById('scheduled_days').value),
                product_price: parseFloat(document.getElementById('product_price').value),
                discount_rate: parseFloat(document.getElementById('discount_rate').value),
                shipping_mode: document.getElementById('shipping_mode').value,
                market: document.getElementById('market').value,
                order_region: document.getElementById('order_region').value
            };

            try {
                const response = await fetch('/api/predict/late-risk', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();

                const resultBox = document.getElementById('resultBox');
                const riskBadge = document.getElementById('riskBadge');
                const probText = document.getElementById('probText');
                const shapContainer = document.getElementById('shapContainer');

                resultBox.classList.add('active');
                probText.innerText = (data.late_probability * 100).toFixed(1) + '%';

                if (data.risk_level === 'HIGH RISK') {
                    riskBadge.className = 'badge-high-risk';
                    riskBadge.innerText = 'HIGH RISK DETECTED';
                } else {
                    riskBadge.className = 'badge-low-risk';
                    riskBadge.innerText = 'LOW RISK (ON-TIME)';
                }

                // Render SHAP XAI Breakdown
                if (data.shap_factors) {
                    shapContainer.innerHTML = '<strong>Top Factor Risk Impact Drivers (SHAP XAI):</strong>';
                    data.shap_factors.forEach(factor => {
                        const widthPct = Math.min(100, Math.max(10, factor.impact * 100));
                        shapContainer.innerHTML += `
                            <div class="shap-row" style="margin-top:10px;">
                                <span>${factor.name}</span>
                                <span>+${(factor.impact * 100).toFixed(1)}%</span>
                            </div>
                            <div class="shap-progress-bg">
                                <div class="shap-progress-fill" style="width: ${widthPct}%;"></div>
                            </div>
                        `;
                    });
                }

            } catch (err) {
                console.error(err);
                alert("Error processing prediction API.");
            } finally {
                btn.innerText = "Predict Late Delivery Risk";
                btn.disabled = false;
            }
        });
    }

    // 2. Shipping Duration Prediction Form
    const durationForm = document.getElementById('durationForm');
    if (durationForm) {
        durationForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = durationForm.querySelector('button[type="submit"]');
            btn.innerText = "Estimating Duration...";
            btn.disabled = true;

            const payload = {
                scheduled_days: parseFloat(document.getElementById('scheduled_days').value),
                shipping_mode: document.getElementById('shipping_mode').value
            };

            try {
                const response = await fetch('/api/predict/duration', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();

                const resultBox = document.getElementById('resultBox');
                const predDays = document.getElementById('predDays');
                const delayVariance = document.getElementById('delayVariance');

                resultBox.classList.add('active');
                predDays.innerText = data.predicted_shipping_days.toFixed(2) + ' Days';
                delayVariance.innerText = (data.delay_expected_days > 0 ? '+' : '') + data.delay_expected_days.toFixed(2) + ' Days';
                delayVariance.style.color = data.delay_expected_days > 0 ? '#EF4444' : '#10B981';

            } catch (err) {
                console.error(err);
                alert("Error calling Shipping Duration API.");
            } finally {
                btn.innerText = "Estimate Duration";
                btn.disabled = false;
            }
        });
    }

    // 3. Customer Segment Prediction Form
    const segmentForm = document.getElementById('segmentForm');
    if (segmentForm) {
        segmentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = segmentForm.querySelector('button[type="submit"]');
            btn.innerText = "Classifying Persona...";
            btn.disabled = true;

            const payload = {
                recency: parseFloat(document.getElementById('recency').value),
                frequency: parseFloat(document.getElementById('frequency').value),
                monetary: parseFloat(document.getElementById('monetary').value),
                profit: parseFloat(document.getElementById('profit').value)
            };

            try {
                const response = await fetch('/api/predict/customer-segment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();

                const resultBox = document.getElementById('resultBox');
                const personaLabel = document.getElementById('personaLabel');
                const directiveText = document.getElementById('directiveText');

                resultBox.classList.add('active');
                personaLabel.innerText = data.persona_label;
                directiveText.innerText = data.marketing_directive;

            } catch (err) {
                console.error(err);
                alert("Error calling Customer Segment API.");
            } finally {
                btn.innerText = "Classify Customer Segment";
                btn.disabled = false;
            }
        });
    }

    // 4. Batch CSV Form Submission
    const batchForm = document.getElementById('batchForm');
    if (batchForm) {
        batchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('csvFile');
            if (!fileInput.files[0]) {
                alert("Please select a CSV file first.");
                return;
            }

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const btn = batchForm.querySelector('button[type="submit"]');
            btn.innerText = "Processing Batch CSV...";
            btn.disabled = true;

            try {
                const response = await fetch('/api/predict/batch', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                const resultBox = document.getElementById('resultBox');
                const totalBatch = document.getElementById('totalBatch');
                const highRiskCount = document.getElementById('highRiskCount');
                const lowRiskCount = document.getElementById('lowRiskCount');

                resultBox.classList.add('active');
                totalBatch.innerText = data.total_orders;
                highRiskCount.innerText = data.high_risk_count;
                lowRiskCount.innerText = data.low_risk_count;

            } catch (err) {
                console.error(err);
                alert("Error processing batch CSV.");
            } finally {
                btn.innerText = "Run Batch Inference";
                btn.disabled = false;
            }
        });
    }

});
