import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, LogisticRegression

OUT_DIR = r"D:/PS15_SolarFlare/backend/Solar Low Energy X-ray Spectrometer/output"
MODELS_DIR = r"D:/PS15_SolarFlare/backend/output"

# Load windows predictions
fusion_res = pd.read_csv(os.path.join(MODELS_DIR, "forecast_results_rf_fusion.csv"))

# Ensure output directory exists
os.makedirs(OUT_DIR, exist_ok=True)

# Styling settings
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

def plot_feature_pie_chart():
    labels = ['Soft X-ray (SoLEXS)', 'Hard X-ray (HEL1OS)', 'Novel Fusion Precursors (Hardness Ratio & Z-Scores)']
    sizes = [5, 5, 7] # 5 SoLEXS, 5 HEL1OS, 7 Fusion
    colors = ['#3b82f6', '#f97316', '#22c55e']
    explode = (0, 0, 0.1) # explode the novel ones
    
    plt.figure(figsize=(8, 7))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140, textprops={'fontsize': 11, 'weight': 'bold'})
    plt.title('Distribution of Feature Categories in the Unified Classifier', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "stat_feature_pie_chart.png"), dpi=200)
    plt.close()
    print("Saved feature pie chart.")

def plot_feature_scatterplot():
    plt.figure(figsize=(9, 7))
    
    no_flare = fusion_res[fusion_res['y_true'] == 0]
    precursor = fusion_res[fusion_res['y_true'] == 1]
    
    plt.scatter(no_flare['mean_s'], no_flare['mean_ratio'], color='#3b82f6', alpha=0.5, label='No Flare (Quiet Sun)', s=25)
    plt.scatter(precursor['mean_s'], precursor['mean_ratio'], color='#ef4444', alpha=0.8, label='Precursor (Flare Impending)', s=40, edgecolors='black')
    
    plt.yscale('log')
    plt.xlabel('Average Soft X-ray Count Rate (mean_s)', fontsize=11)
    plt.ylabel('Spectral Hardness Ratio (mean_ratio - Log Scale)', fontsize=11)
    plt.title('Feature Scatterplot: Separating Quiet Sun from Flare Precursors', fontsize=12, fontweight='bold')
    
    plt.text(0.05, 0.05, "RESEARCH GAP: Standard models only look at counts (X-axis),\ncreating overlap. Our novel Hardness Ratio (Y-axis) separates\nthe classes clearly before the flare peak occurs.", 
             transform=plt.gca().transAxes, color='black', fontsize=9.5, bbox=dict(boxstyle="round", fc="yellow", alpha=0.2))
             
    plt.legend(loc='upper right')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.savefig(os.path.join(OUT_DIR, "stat_feature_scatterplot.png"), dpi=200)
    plt.close()
    print("Saved feature scatterplot.")

def plot_linear_regression():
    plt.figure(figsize=(9, 7))
    
    X = fusion_res[['mean_s']].values
    y = fusion_res['mean_h'].values
    
    lr = LinearRegression()
    lr.fit(X, y)
    y_pred = lr.predict(X)
    
    plt.scatter(X, y, color='purple', alpha=0.4, s=20, label='Telemetry Windows')
    plt.plot(X, y_pred, color='red', lw=2.5, label=f'Linear Regression (R² = {lr.score(X, y):.3f})')
    
    plt.xlabel('SoLEXS SXR Mean Count Rate', fontsize=11)
    plt.ylabel('HEL1OS HXR Mean Count Rate', fontsize=11)
    plt.title('Linear Regression: Soft vs. Hard X-ray Cross-Correlation', fontsize=12, fontweight='bold')
    
    plt.text(0.05, 0.9, f"Equation: HXR = {lr.coef_[0]:.3f} * SXR + {lr.intercept_:.2f}",
             transform=plt.gca().transAxes, color='darkred', weight='bold', bbox=dict(boxstyle="round", fc="white", alpha=0.8))
             
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(OUT_DIR, "stat_linear_regression.png"), dpi=200)
    plt.close()
    print("Saved linear regression plot.")

def plot_logistic_regression():
    plt.figure(figsize=(9, 7))
    
    X = fusion_res[['z_max_h']].values
    y = fusion_res['y_true'].values
    
    log_reg = LogisticRegression(class_weight='balanced')
    log_reg.fit(X, y)
    
    X_curve = np.linspace(X.min() - 1, X.max() + 1, 300).reshape(-1, 1)
    y_prob = log_reg.predict_proba(X_curve)[:, 1]
    
    plt.scatter(X[y==0], y[y==0], color='blue', alpha=0.4, label='Class 0: Quiet Sun', s=20)
    plt.scatter(X[y==1], y[y==1], color='red', alpha=0.8, label='Class 1: Flare Precursor', s=30)
    
    plt.plot(X_curve, y_prob, color='green', lw=3, label='Logistic Regression Sigmoid Curve')
    
    plt.xlabel('Maximum Hard X-ray Z-Score (z_max_h)', fontsize=11)
    plt.ylabel('Predicted Precursor Probability P(Y=1)', fontsize=11)
    plt.title('Logistic Regression: Probability Mapping for Flare Trigger Alerts', fontsize=12, fontweight='bold')
    
    w = log_reg.coef_[0][0]
    b = log_reg.intercept_[0]
    decision_boundary = -b / w
    plt.axvline(x=decision_boundary, color='gray', linestyle='--', label=f'Decision Boundary (z={decision_boundary:.2f})')
    
    plt.legend(loc='center right')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(OUT_DIR, "stat_logistic_regression.png"), dpi=200)
    plt.close()
    print("Saved logistic regression plot.")

if __name__ == '__main__':
    plot_feature_pie_chart()
    plot_feature_scatterplot()
    plot_linear_regression()
    plot_logistic_regression()
    print("All statistical and ML regression/scatterplot graphs generated successfully!")
