import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT_DIR = r"D:/PS15_SolarFlare/backend/Solar Low Energy X-ray Spectrometer/output"
os.makedirs(OUT_DIR, exist_ok=True)

# Styling settings
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

def plot_activation_functions():
    x = np.linspace(-6, 6, 200)
    
    # Activation equations
    sigmoid = 1 / (1 + np.exp(-x))
    tanh = np.tanh(x)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. Sigmoid Plot
    axes[0].plot(x, sigmoid, color='#16a34a', lw=3, label=r'$\sigma(x) = \frac{1}{1 + e^{-x}}$')
    axes[0].axhline(0, color='gray', linestyle='--', lw=1)
    axes[0].axhline(1, color='gray', linestyle='--', lw=1)
    axes[0].axvline(0, color='gray', linestyle=':', lw=1)
    axes[0].set_ylim([-0.1, 1.1])
    axes[0].set_xlabel('Input Value (x)', fontsize=11)
    axes[0].set_ylabel('Activation Output (y)', fontsize=11)
    axes[0].set_title('Sigmoid Activation Function\n(Probability Mapping: Range [0, 1])', fontsize=12, fontweight='bold')
    axes[0].legend(fontsize=12, loc='upper left')
    axes[0].grid(True, alpha=0.3)
    
    # Add application annotation
    axes[0].text(0.5, 0.2, "APPLICATION: Used in the final layer\nof the flare warning model to predict the\nprobability of precursor emergence.", 
                 transform=axes[0].transAxes, fontsize=9.5, ha="center", bbox=dict(boxstyle="round", fc="white", alpha=0.8, ec="green"))
    
    # 2. Tanh Plot
    axes[1].plot(x, tanh, color='#e11d48', lw=3, label=r'$\tanh(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}}$')
    axes[1].axhline(-1, color='gray', linestyle='--', lw=1)
    axes[1].axhline(0, color='gray', linestyle='--', lw=1)
    axes[1].axhline(1, color='gray', linestyle='--', lw=1)
    axes[1].axvline(0, color='gray', linestyle=':', lw=1)
    axes[1].set_ylim([-1.1, 1.1])
    axes[1].set_xlabel('Input Value (x)', fontsize=11)
    axes[1].set_ylabel('Activation Output (y)', fontsize=11)
    axes[1].set_title('Hyperbolic Tangent (Tanh) Activation Function\n(Zero-Centered Activation: Range [-1, 1])', fontsize=12, fontweight='bold')
    axes[1].legend(fontsize=12, loc='upper left')
    axes[1].grid(True, alpha=0.3)
    
    # Add application annotation
    axes[1].text(0.5, 0.2, "APPLICATION: Used in hidden layers of\nthe PINN induction model to represent symmetric\nmagnetic field polarity changes.", 
                 transform=axes[1].transAxes, fontsize=9.5, ha="center", bbox=dict(boxstyle="round", fc="white", alpha=0.8, ec="red"))
    
    plt.suptitle("Activation Functions in Aditya-L1 Neural Predictive Models", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "ml_activation_functions.png"), dpi=200)
    plt.close()
    print("Saved activation functions plot.")

if __name__ == '__main__':
    plot_activation_functions()
