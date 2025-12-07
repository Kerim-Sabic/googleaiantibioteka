// BAA-2025 Frontend JavaScript (Netlify Static Site)

// API base URL - for Netlify, functions are at /.netlify/functions
const API_BASE = '/.netlify/functions';

document.addEventListener('DOMContentLoaded', function() {
    // Test API button
    const testApiBtn = document.getElementById('test-api-btn');
    const apiResponse = document.getElementById('api-response');

    if (testApiBtn) {
        testApiBtn.addEventListener('click', async function() {
            apiResponse.classList.add('show');
            apiResponse.innerHTML = '<p>Loading...</p>';

            try {
                const response = await fetch(`${API_BASE}/health`);
                const data = await response.json();

                apiResponse.innerHTML = `
                    <h4>✅ API Response (Success):</h4>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            } catch (error) {
                apiResponse.innerHTML = `
                    <h4>❌ Error:</h4>
                    <p style="color: red;">${error.message}</p>
                    <p style="font-size: 0.9rem; color: #666;">
                        Note: If running locally without Netlify CLI, functions won't work.
                        Deploy to Netlify or run with <code>netlify dev</code>
                    </p>
                `;
            }
        });
    }

    // Example recommendation form (if it exists)
    const recommendForm = document.getElementById('recommend-form');
    const recommendResult = document.getElementById('recommend-result');

    if (recommendForm) {
        recommendForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            recommendResult.classList.add('show');
            recommendResult.innerHTML = '<p>Generating recommendation...</p>';

            // Get form data
            const formData = new FormData(recommendForm);

            const payload = {
                patient: {
                    demographics: {
                        age_years: parseInt(formData.get('age') || 35),
                        gender: formData.get('gender') || 'male',
                        weight_kg: parseFloat(formData.get('weight') || 75)
                    },
                    physiology: {
                        serum_creatinine_mg_dl: parseFloat(formData.get('creatinine') || 1.0)
                    },
                    allergies: []
                },
                infection: {
                    site: formData.get('infection_site') || 'community_acquired_pneumonia',
                    acquisition: 'community_acquired',
                    severity: formData.get('severity') || 'moderate'
                }
            };

            try {
                const response = await fetch(`${API_BASE}/recommend`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (data.status === 'success') {
                    const rec = data.recommendation.primary_recommendation;

                    recommendResult.innerHTML = `
                        <h4>✅ Recommendation Generated:</h4>
                        <div class="recommendation-card">
                            <h5>Diagnosis: ${data.recommendation.diagnosis}</h5>
                            <p><strong>Assessment:</strong> ${data.recommendation.severity_assessment}</p>

                            <div class="drug-info">
                                <h6>Primary Recommendation:</h6>
                                <p><strong>Drug:</strong> ${rec.generic_name}</p>
                                <p><strong>Brands (BiH):</strong> ${rec.trade_names.join(', ')}</p>
                                <p><strong>Formulation:</strong> ${rec.formulation}</p>
                                <p><strong>Route:</strong> ${rec.route}</p>
                                <p><strong>Dose:</strong> ${rec.dose_calculation.dose_amount} ${rec.dose_calculation.dose_unit} ${rec.dose_calculation.frequency}</p>
                                <p><strong>Duration:</strong> ${rec.dose_calculation.duration_days} days</p>
                                <p><strong>Status:</strong> ${rec.regulatory_status}</p>
                            </div>

                            <div class="prescription-instructions">
                                <h6>Prescription:</h6>
                                <pre>${rec.prescription_instructions}</pre>
                            </div>

                            <div class="patient-instructions">
                                <h6>Patient Counseling:</h6>
                                <p>${rec.patient_instructions}</p>
                            </div>
                        </div>
                    `;
                } else {
                    recommendResult.innerHTML = `
                        <h4>❌ Error:</h4>
                        <p style="color: red;">${data.message}</p>
                    `;
                }

            } catch (error) {
                recommendResult.innerHTML = `
                    <h4>❌ Error:</h4>
                    <p style="color: red;">${error.message}</p>
                `;
            }
        });
    }

    // Drug search functionality
    const searchForm = document.getElementById('drug-search-form');
    const searchResults = document.getElementById('search-results');

    if (searchForm) {
        searchForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const genericName = document.getElementById('generic-name').value.trim();

            if (!genericName) {
                alert('Please enter a drug name');
                return;
            }

            searchResults.classList.add('show');
            searchResults.innerHTML = '<p>Searching...</p>';

            try {
                const response = await fetch(`${API_BASE}/search?generic=${encodeURIComponent(genericName)}`);
                const data = await response.json();

                if (data.status === 'success' && data.drugs.length > 0) {
                    let html = `<h4>Found ${data.count} brand(s) for "${genericName}":</h4>`;

                    data.drugs.forEach(drug => {
                        html += `
                            <div class="drug-card">
                                <h5>${drug.trade_name}</h5>
                                <p><strong>Manufacturer:</strong> ${drug.manufacturer}</p>
                                <p><strong>Status:</strong> ${drug.regulatory_status}</p>
                                <p><strong>ATC:</strong> ${drug.atc_code}</p>
                                ${drug.formulations ? `<p><strong>Formulations:</strong> ${drug.formulations.length}</p>` : ''}
                            </div>
                        `;
                    });

                    searchResults.innerHTML = html;
                } else {
                    searchResults.innerHTML = `
                        <p>No drugs found for "${genericName}" in BiH registry.</p>
                        <p style="color: #666; font-size: 0.9rem;">This drug may not be registered in Bosnia & Herzegovina.</p>
                    `;
                }

            } catch (error) {
                searchResults.innerHTML = `
                    <p style="color: red;">Error: ${error.message}</p>
                `;
            }
        });
    }
});

// Add styles for new elements
const additionalStyles = `
<style>
.recommendation-card, .drug-card {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    margin: 15px 0;
    border-left: 4px solid #667eea;
}

.drug-info, .prescription-instructions, .patient-instructions {
    margin: 15px 0;
    padding: 15px;
    background: white;
    border-radius: 5px;
}

.show {
    display: block !important;
}

.hidden {
    display: none;
}
</style>
`;

// Inject additional styles
document.head.insertAdjacentHTML('beforeend', additionalStyles);
