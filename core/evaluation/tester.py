import torch
from torch.utils.data import DataLoader
from .metrics import calculate_metrics
from .confusion_matrix import plot_confusion_matrix
import numpy as np
from modules.YA_Common.utils.logger import get_logger
import torch.nn as nn

logger = get_logger("tester")

class Tester:
    def __init__(self, model, test_loader, device='cpu', loss_fn=None):
        self.model = model
        self.test_loader = test_loader
        self.device = device
        self.loss_fn = loss_fn if loss_fn else nn.BCELoss() # Default loss

    def test(self):
        """
        Performs testing on the test set, calculates metrics, and generates a confusion matrix.
        """
        logger.info("Starting model evaluation on the test set...")
        if not self.test_loader:
            logger.warning("Test loader is empty. Skipping evaluation.")
            return {}

        self.model.to(self.device)
        self.model.eval()
        all_preds = []
        all_labels = []
        total_loss = 0

        with torch.no_grad():
            for features, labels in self.test_loader:
                features, labels = features.to(self.device), labels.to(self.device)

                # The input shape should be handled by the model or preprocessor
                # No model-specific shape adjustments here to keep it generic
                outputs = self.model(features)
                
                # Calculate loss
                loss = self.loss_fn(outputs.squeeze(), labels)
                total_loss += loss.item()

                preds = (outputs.squeeze() > 0.5).cpu().numpy()
                all_preds.extend(preds)
                all_labels.extend(labels.cpu().numpy())

        if not all_labels:
            logger.warning("No data was processed during testing.")
            return {}

        y_true = np.array(all_labels)
        y_pred = np.array(all_preds)
        
        metrics = calculate_metrics(y_true, y_pred)
        metrics['test_loss'] = total_loss / len(self.test_loader)
        
        logger.info("Test Results:")
        for key, value in metrics.items():
            logger.info(f"  - Test {key.capitalize()}: {value:.4f}")
            
        # Generate and save confusion matrix
        try:
            plot_confusion_matrix(y_true, y_pred, class_names=['Not Wolf', 'Wolf'], filename='logs/test_confusion_matrix.png')
            logger.info("Confusion matrix saved to logs/test_confusion_matrix.png")
        except Exception as e:
            logger.error(f"Failed to generate confusion matrix: {e}")
        
        return metrics

if __name__ == '__main__':
    logger.info("Tester module created.")
    # Example usage requires a trained model and a test dataloader.
