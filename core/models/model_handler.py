import torch
import os
from typing import Optional

def save_model(model: torch.nn.Module, path: str, model_name: str):
    """
    Saves a PyTorch model to a specified path.
    """
    if not os.path.exists(path):
        os.makedirs(path)
    
    full_path = os.path.join(path, f"{model_name}.pt")
    torch.save(model.state_dict(), full_path)
    print(f"Model saved to {full_path}")

def load_model(model: torch.nn.Module, path: str, model_name: str, device: str = 'cpu') -> Optional[torch.nn.Module]:
    """
    Loads a PyTorch model from a specified path.
    """
    full_path = os.path.join(path, f"{model_name}.pt")
    if os.path.exists(full_path):
        model.load_state_dict(torch.load(full_path, map_location=device))
        model.to(device)
        model.eval() # Set model to evaluation mode
        print(f"Model loaded from {full_path}")
        return model
    else:
        print(f"No model found at {full_path}")
        return None

if __name__ == '__main__':
    # This is a module with functions, so direct execution doesn't do much.
    print("Model handler module created.")
    # Example usage would involve creating a model instance first.
    # from model_definition import SimpleLSTM
    # model = SimpleLSTM(10, 20, 1, 2)
    # save_model(model, path='../../models/saved', model_name='test_lstm')
    # loaded_model = load_model(SimpleLSTM(10, 20, 1, 2), path='../../models/saved', model_name='test_lstm')
    # print(loaded_model)
