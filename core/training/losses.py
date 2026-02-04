import torch.nn as nn

def get_loss_function(loss_name: str):
    """
    Returns a loss function instance based on its name.
    """
    if loss_name.lower() == 'bce':
        return nn.BCELoss()
    elif loss_name.lower() == 'cross_entropy':
        return nn.CrossEntropyLoss()
    elif loss_name.lower() == 'mse':
        return nn.MSELoss()
    else:
        raise ValueError(f"Unknown loss function: {loss_name}")

if __name__ == '__main__':
    print("Losses module created.")
    bce = get_loss_function('bce')
    print(f"Instantiated loss: {bce}")
