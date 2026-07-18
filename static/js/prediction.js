(function () {

    const { api, formatApiError } = window.ReAdmitIQ;

    const ARC_LENGTH = 314.16;

    const colors = {
        Low: "#3FBFAD",
        Medium: "#F2B138",
        High: "#F2545B"
    };

    const advice = {
        Low: "Standard discharge follow-up is likely sufficient.",
        Medium: "Consider a follow-up call within 7 days.",
        High: "Recommend care-coordinator outreach before discharge and a follow-up visit within 72 hours."
    };

    document
        .getElementById("predictForm")
        .addEventListener("submit", submitPrediction);


    async function submitPrediction(e) {

        e.preventDefault();

        const errorEl = document.getElementById("predictError");

        errorEl.classList.remove("show");

        const btn = document.getElementById("predictBtn");

        btn.disabled = true;

        btn.innerHTML =
            '<span class="spinner"></span> Scoring...';

        clearExplainability();

        const payload = {

            patient_id:
                document.getElementById("p_patient_id").value
                    ? Number(document.getElementById("p_patient_id").value)
                    : null,

            age:
                Number(document.getElementById("p_age").value),

            gender:
                document.getElementById("p_gender").value,

            blood_pressure:
                document.getElementById("p_bp").value,

            cholesterol:
                Number(document.getElementById("p_cholesterol").value),

            bmi:
                Number(document.getElementById("p_bmi").value),

            diabetes:
                document.getElementById("p_diabetes").value,

            hypertension:
                document.getElementById("p_hypertension").value,

            medication_count:
                Number(document.getElementById("p_meds").value),

            length_of_stay:
                Number(document.getElementById("p_los").value),

            discharge_destination:
                document.getElementById("p_destination").value
        };

        try {

            const response = await api(
                "/api/prediction/predict",
                {
                    method: "POST",
                    body: JSON.stringify(payload)
                }
            );

            if (!response)
                return;

            if (!response.ok) {

                const err =
                    await response.json().catch(() => ({}));

                throw new Error(
                    formatApiError(err.detail)
                );
            }

            const result =
                await response.json();

            renderGauge(result);

            if (result.explanation) {
                renderExplanation(result.explanation);
            }

            if (result.feature_importance) {
                renderFeatureImportance(
                    result.feature_importance,
                    result.explanation
                );
            }

        }

        catch (err) {

            errorEl.textContent = err.message;

            errorEl.classList.add("show");
        }

        finally {

            btn.disabled = false;

            btn.textContent =
                "Calculate risk score";
        }
    }


    function renderGauge(result) {

        const arc =
            document.getElementById("gaugeArc");

        const score =
            document.getElementById("gaugeScore");

        const label =
            document.getElementById("gaugeLabel");

        const hint =
            document.getElementById("gaugeHint");

        const color =
            colors[result.risk_label] || "#3FBFAD";

        const dash =
            (result.risk_percent / 100) * ARC_LENGTH;

        arc.setAttribute(
            "stroke",
            color
        );

        arc.style.transition =
            "stroke-dasharray 0.6s ease";

        arc.setAttribute(
            "stroke-dasharray",
            `${dash} ${ARC_LENGTH}`
        );

        score.textContent =
            `${result.risk_percent}%`;

        score.style.color = color;

        label.textContent =
            `${result.risk_label} risk of 30-day readmission`;

        hint.textContent =
            advice[result.risk_label] || "";
    }
        function renderExplanation(explanation) {

        const panel =
            document.getElementById("explanationPanel");

        if (!panel || !explanation)
            return;

        panel.style.display = "block";

        const summary =
            document.getElementById("explanationSummary");

        summary.textContent =
            explanation.summary || "";

        const factors =
            document.getElementById("topFactors");

        factors.innerHTML = "";

        (explanation.top_factors || []).forEach(factor => {

            const card =
                document.createElement("div");

            card.className =
                "factor-card";

            const increasing =
                factor.direction === "increases_risk";

            card.innerHTML = `

                <div class="factor-icon ${increasing ? "risk-up" : "risk-down"}">

                    ${increasing ? "▲" : "▼"}

                </div>

                <div class="factor-body">

                    <div class="factor-title">

                        ${factor.label}

                    </div>

                    <div class="factor-value">

                        ${factor.value}

                    </div>

                </div>

                <div class="factor-impact">

                    ${(factor.impact * 100).toFixed(1)}%

                </div>

            `;

            factors.appendChild(card);

        });

    }



    function renderFeatureImportance(importances, explanation) {

        const container =
            document.getElementById("featureImportance");

        if (!container || !importances)
            return;

        container.innerHTML = "";

        const directions = {};

        if (explanation && explanation.top_factors) {

            explanation.top_factors.forEach(f => {

                directions[f.label] = f.direction;

            });

        }

        const entries =
            Object.entries(importances);

        const max =
            Math.max(...entries.map(e => e[1]));

        entries
            .slice(0, 8)
            .forEach(([feature, value]) => {

                const label =
                    formatLabel(feature);

                const direction =
                    directions[label];

                let color =
                    "#3FBFAD";

                if (direction === "increases_risk")
                    color = "#F2545B";

                if (direction === "decreases_risk")
                    color = "#47C97A";

                const row =
                    document.createElement("div");

                row.className =
                    "importance-row";

                row.innerHTML = `

                    <div class="importance-label">

                        ${label}

                    </div>

                    <div class="importance-bar-track">

                        <div
                            class="importance-bar-fill"

                            style="
                                width:${(value/max)*100}%;
                                background:${color};
                            ">

                        </div>

                    </div>

                    <div class="importance-value">

                        ${value.toFixed(3)}

                    </div>

                `;

                container.appendChild(row);

            });

    }

        function clearExplainability() {

        const panel =
            document.getElementById("explanationPanel");

        if (panel) {
            panel.style.display = "none";
        }

        const summary =
            document.getElementById("explanationSummary");

        if (summary) {
            summary.textContent = "";
        }

        const factors =
            document.getElementById("topFactors");

        if (factors) {
            factors.innerHTML = "";
        }

        const importance =
            document.getElementById("featureImportance");

        if (importance) {
            importance.innerHTML = "";
        }

    }



    function formatLabel(feature) {

        const labels = {

            age: "Age",

            gender_enc: "Gender",

            systolic_bp: "Systolic BP",

            diastolic_bp: "Diastolic BP",

            cholesterol: "Cholesterol",

            bmi: "BMI",

            diabetes_enc: "Diabetes",

            hypertension_enc: "Hypertension",

            medication_count: "Medication Count",

            length_of_stay: "Length of Stay",

            discharge_enc: "Discharge Destination"

        };

        return labels[feature] || feature;

    }

})();