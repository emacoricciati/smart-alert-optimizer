import os
import matplotlib.pyplot as plt
from get_aws_data import get_aws_data

def analyze_patterns(df):
    window = 12 # data every 5 minutes
    
    # Rolling Mean
    df['rolling_mean'] = df['value'].rolling(window=window).mean()
    
    # Rolling Std
    df['rolling_std'] = df['value'].rolling(window=window).std()
    
    # Calculate dynamic threshold for anomaly detection
    # This is the base of statistics for finding anomalies (Z-Score)
    df['dynamic_threshold'] = df['rolling_mean'] + (1 * df['rolling_std'])
    
    return df

def run_simulation(df, static_threshold_value=30.0):
    """
    Compare static thresholding with dynamic thresholding to evaluate the reduction in false positives.
    """
    # 1. Identification Static Alerts
    df['static_alert'] = df['value'] > static_threshold_value
    
    # 2. Identification Dynamic Alerts
    df['dynamic_alert'] = (df['value'] > df['dynamic_threshold']) & (df['dynamic_threshold'].notna())
    
    # 3. Count Alerts
    total_static = df['static_alert'].sum()
    total_dynamic = df['dynamic_alert'].sum()
    
    # 4. Calculate Reduction
    if total_static > 0:
        reduction = ((total_static - total_dynamic) / total_static) * 100
    else:
        reduction = 0
        
    return total_static, total_dynamic, reduction

def save_business_report(df, s_alerts, d_alerts, reduction):
    """
    Generate and save a business impact report based on the simulation results.
    """
    # Create reports directory if it doesn't exist
    if not os.path.exists('../reports'):
        os.makedirs('../reports')

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(14, 7))

    # 1. Plot raw data
    ax.plot(df['timestamp'], df['value'], color='#bdc3c7', alpha=0.4, label='Real CPU Usage (Raw)')
    
    # 2. Plot dynamic threshold
    ax.plot(df['timestamp'], df['dynamic_threshold'], color='#e67e22', linewidth=1.5, label='SmartAlert Adaptive Threshold')

    # 3. Highlight detected anomalies
    dynamic_points = df[df['dynamic_alert']]
    ax.scatter(dynamic_points['timestamp'], dynamic_points['value'], color='#e74c3c', s=15, label='Actual Anomalies Detected', zorder=5)

    # 4. Add business impact text box
    stats_text = (
        f"BUSINESS IMPACT REPORT\n"
        f"--------------------------\n"
        f"Legacy Alerts (Static): {s_alerts}\n"
        f"Optimized Alerts (Smart): {d_alerts}\n"
        f"Alert Noise Reduction: {reduction:.1f}%\n"
        f"Estimated Time Saved: ~{int((s_alerts-d_alerts)*5/60)} hours/week"
    )
    
    # Text box styling
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='#34495e')
    ax.text(0.02, 0.95, stats_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props, family='monospace')

    # Final touches
    ax.set_title("SRE Decision Support: Threshold Optimization Analysis", fontsize=16, pad=20, fontweight='bold')
    ax.set_ylabel("Utilization %", fontsize=12)
    ax.set_xlabel("Time Observation Period", fontsize=12)
    ax.legend(loc='upper right', frameon=True)

    # Automatic layout adjustment and save
    report_path = '../reports/optimization_impact.png'
    plt.tight_layout()
    plt.savefig(report_path, dpi=300)
    print(f"✅ Report saved to: {report_path}")
    plt.show()

if __name__ == "__main__":
    # Load data
    data = get_aws_data()
    
    # 2. Analyze patterns
    analyzed_data = analyze_patterns(data)
    

    # 3. Simulation
    s_alerts, d_alerts, red = run_simulation(data, static_threshold_value=40.0)

    # 4. Save Business Report
    save_business_report(analyzed_data, s_alerts, d_alerts, red)

