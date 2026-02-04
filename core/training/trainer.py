import torch
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.tensorboard import SummaryWriter
from typing import Dict, Any
import time
import os

# Assuming other necessary modules are in the parent directory or installed
from ..models.model_definition import SimpleLSTM # Example model
from ..training.losses import get_loss_function
from ..training.optimizers import get_optimizer
from ..training.schedulers import get_scheduler
from ..training.callbacks import EarlyStopping

class Trainer:
    def __init__(self, model_config: Dict[str, Any], train_data, val_data):
        self.config = model_config
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Instantiate model
        # This part needs to be more robust to handle different model types
        if self.config['model_type'] == 'lstm':
            self.model = SimpleLSTM(
                input_dim=self.config['input_dim'],
                hidden_dim=self.config['hidden_dim'],
                output_dim=self.config['output_dim'],
                n_layers=self.config['n_layers']
            ).to(self.device)
        else:
            raise NotImplementedError(f"Model type {self.config['model_type']} not implemented in Trainer.")

        self.train_loader = self._create_dataloader(train_data)
        self.val_loader = self._create_dataloader(val_data)

        self.loss_fn = get_loss_function(self.config['loss_function'])
        self.optimizer = get_optimizer(self.model.parameters(), self.config['optimizer'], self.config['lr'])
        self.scheduler = get_scheduler(self.optimizer)
        self.early_stopping = EarlyStopping(patience=10, verbose=True)
        
        log_dir = os.path.join('..', '..', 'logs', 'tensorboard', str(int(time.time())))
        self.writer = SummaryWriter(log_dir=log_dir)

    def _create_dataloader(self, data, shuffle=True):
        if data is None:
            return None
        features, labels = data
        # Note: This assumes features and labels are already tensors.
        # In a real scenario, you'd convert numpy arrays from pandas to tensors here.
        tensor_features = torch.Tensor(features.values if hasattr(features, 'values') else features)
        tensor_labels = torch.Tensor(labels.values if hasattr(labels, 'values') else labels)
        dataset = TensorDataset(tensor_features, tensor_labels)
        return DataLoader(dataset, batch_size=self.config['batch_size'], shuffle=shuffle)

    def train_epoch(self, epoch_num):
        self.model.train()
        total_loss = 0
        for features, labels in self.train_loader:
            features, labels = features.to(self.device), labels.to(self.device)
            
            # LSTM expects 3D input
            if self.config['model_type'] == 'lstm' and len(features.shape) == 2:
                features = features.unsqueeze(1)

            self.optimizer.zero_grad()
            outputs = self.model(features)
            loss = self.loss_fn(outputs.squeeze(), labels)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        
        avg_loss = total_loss / len(self.train_loader)
        self.writer.add_scalar('Loss/train', avg_loss, epoch_num)
        return avg_loss

    def validate_epoch(self, epoch_num):
        self.model.eval()
        total_loss = 0
        with torch.no_grad():
            for features, labels in self.val_loader:
                features, labels = features.to(self.device), labels.to(self.device)
                
                if self.config['model_type'] == 'lstm' and len(features.shape) == 2:
                    features = features.unsqueeze(1)

                outputs = self.model(features)
                loss = self.loss_fn(outputs.squeeze(), labels)
                total_loss += loss.item()
        
        avg_loss = total_loss / len(self.val_loader)
        self.writer.add_scalar('Loss/validation', avg_loss, epoch_num)
        return avg_loss

    def run(self):
        print(f"Starting training on {self.device}...")
        for epoch in range(self.config['epochs']):
            train_loss = self.train_epoch(epoch)
            val_loss = self.validate_epoch(epoch)
            
            print(f"Epoch {epoch+1}/{self.config['epochs']} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
            
            if self.scheduler:
                self.scheduler.step(val_loss)
            
            self.early_stopping(val_loss, self.model)
            if self.early_stopping.early_stop:
                print("Early stopping triggered.")
                break
        
        self.writer.close()
        print("Training finished.")
        # Load best model state
        self.model.load_state_dict(torch.load('checkpoint.pt'))
        return self.model

if __name__ == '__main__':
    print("Trainer module created.")
    # Example usage requires data and config
    # from ..models.model_config import get_default_lstm_config
    # config = get_default_lstm_config()
    # ... create dummy data ...
    # trainer = Trainer(config, train_data, val_data)
    # trainer.run()
