import torch
from torch.utils.data import DataLoader
from .metrics import calculate_metrics
import numpy as np

class Validator:
    def __init__(self, model, val_loader, loss_fn, device='cpu'):
        self.model = model
        self.val_loader = val_loader
        self.loss_fn = loss_fn
        self.device = device

    def validate(self):
        """
        Performs validation on the validation set.
        """
        self.model.eval()
        total_loss = 0
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for features, labels in self.val_loader:
                features, labels = features.to(self.device), labels.to(self.device)
                
                # Handle input shape for LSTM if necessary
                if len(features.shape) == 2 and isinstance(self.model, torch.nn.LSTM):
                     features = features.unsqueeze(1)

                outputs = self.model(features)
                loss = self.loss_fn(outputs.squeeze(), labels)
                total_loss += loss.item()

                preds = (outputs.squeeze() > 0.5).cpu().numpy()
                all_preds.extend(preds)
                all_labels.extend(labels.cpu().numpy())

        avg_loss = total_loss / len(self.val_loader)
        metrics = calculate_metrics(np.array(all_labels), np.array(all_preds))
        
        print(f"Validation Loss: {avg_loss:.4f}")
        for key, value in metrics.items():
            print(f"Validation {key.capitalize()}: {value:.4f}")
            
        return avg_loss, metrics

if __name__ == '__main__':
    print("Validator module created.")
    # Example usage requires a trained model, dataloader, and loss function.
