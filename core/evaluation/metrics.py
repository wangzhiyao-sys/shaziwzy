from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np

def calculate_metrics(y_true, y_pred, y_prob=None):
    """
    Calculates a dictionary of classification metrics.
    
    Args:
        y_true (np.array): True labels.
        y_pred (np.array): Predicted labels (0 or 1).
        y_prob (np.array, optional): Predicted probabilities. Defaults to None.

    Returns:
        dict: A dictionary containing accuracy, precision, recall, and F1-score.
    """
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1_score': f1_score(y_true, y_pred, zero_division=0)
    }
    return metrics

if __name__ == '__main__':
    print("Metrics module created.")
    # Example usage:
    # y_true = np.array([0, 1, 1, 0, 1, 0])
    # y_pred = np.array([0, 1, 0, 0, 1, 1])
    # metrics = calculate_metrics(y_true, y_pred)
    # print(metrics)
