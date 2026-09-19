import joblib, numpy as np, warnings

warnings.filterwarnings("ignore")
base = "C:/Users/HP/Downloads/SuryaDrishti/backend/output/"
for name in ["forecast_model_rf.joblib", "forecast_model_rf_fusion.joblib"]:
    m = joblib.load(base + name)
    nf = m.n_features_in_
    lo = np.full((1, nf), 0.02)
    hi = np.full((1, nf), 0.95)
    p_lo = float(m.predict_proba(lo)[0][1])
    p_hi = float(m.predict_proba(hi)[0][1])
    ok = "YES" if p_hi >= p_lo else "NO"
    print(f"{name} | features={nf} | p(low)={p_lo:.4f} p(high)={p_hi:.4f} | behaves_sensibly={ok}")
print("AI_MODEL_TEST_DONE")
