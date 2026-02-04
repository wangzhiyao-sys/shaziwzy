import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np

def plot_confusion_matrix(y_true, y_pred, class_names, filename='confusion_matrix.png'):
    """
    Generates and saves a confusion matrix plot.
    """
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    
    # Save the figure
    plt.savefig(filename)
    print(f"Confusion matrix saved to {filename}")
    plt.close()

if __name__ == '__main__':
    print("Confusion matrix module created.")
    # Example usage:
    # y_true = np.array([0, 1, 1, 0, 1, 0])
    # y_pred = np.array([0, 1, 0, 0, 1, 1])
    # class_names = ['Class 0', 'Class 1']
    # plot_confusion_matrix(y_true, y_pred, class_names)
