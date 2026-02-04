from typing import Dict, Any

def get_default_lstm_config() -> Dict[str, Any]:
    """
    Returns the default configuration for the LSTM model.
    """
    return {
        'model_type': 'lstm',
        'input_dim': 128,
        'hidden_dim': 256,
        'output_dim': 1,
        'n_layers': 2,
        'dropout': 0.5,
        'lr': 0.001,
        'optimizer': 'adam',
        'loss_function': 'bce',
        'batch_size': 32,
        'epochs': 50,
    }

def get_default_gnn_config() -> Dict[str, Any]:
    """
    Returns the default configuration for the GNN model.
    """
    return {
        'model_type': 'gnn',
        'input_dim': 64,
        'hidden_dim': 128,
        'output_dim': 2, # e.g., wolf or not wolf
        'lr': 0.01,
        'optimizer': 'adam',
        'loss_function': 'cross_entropy',
        'batch_size': 1, # Often 1 for graph-level predictions
        'epochs': 100,
    }

def load_config(model_type: str) -> Dict[str, Any]:
    """
    Loads a configuration based on model type.
    """
    if model_type == 'lstm':
        return get_default_lstm_config()
    elif model_type == 'gnn':
        return get_default_gnn_config()
    else:
        raise ValueError(f"Unknown model type: {model_type}")

if __name__ == '__main__':
    lstm_config = load_config('lstm')
    print("Default LSTM Config:")
    print(lstm_config)
    
    gnn_config = load_config('gnn')
    print("\nDefault GNN Config:")
    print(gnn_config)

    print("\nModel config module created.")
