import torch
from torch.utils.data import DataLoader
from .metrics import calculate_metrics
from .confusion_matrix import plot_confusion_matrix
import numpy as np

class Tester:
    def __init__(self, model, test_loader, device='cpu'):
        self.model = model
        self.test_loader = test_loader
        self.device = device

    def test(self):
        """
        Performs testing on the test set and generates a confusion matrix.
        """
        self.model.eval()
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for features, labels in self.test_loader:
                features, labels = features.to(self.device), labels.to(self.device)

                # Handle input shape for LSTM if necessary
                if len(features.shape) == 2 and isinstance(self.model, torch.nn.LSTM):
                     features = features.unsqueeze(1)

                outputs = self.model(features)
                preds = (outputs.squeeze() > 0.5).cpu().numpy()
                all_preds.extend(preds)
                all_labels.extend(labels.cpu().numpy())

        y_true = np.array(all_labels)
        y_pred = np.array(all_preds)
        
        metrics = calculate_metrics(y_true, y_pred)
        
        print("Test Results:")
        for key, value in metrics.items():
            print(f"Test {key.capitalize()}: {value:.4f}")
            
        # Generate and save confusion matrix
        plot_confusion_matrix(y_true, y_pred, class_names=['Not Wolf', 'Wolf'], filename='test_confusion_matrix.png')
        
        return metrics

if __name__ == '__main__':
    print("Tester module created.")
    # Example usage requires a trained model and a test dataloader.
