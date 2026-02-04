import torch.optim as optim

def get_optimizer(params, optimizer_name: str, lr: float):
    """
    Returns an optimizer instance based on its name.
    """
    if optimizer_name.lower() == 'adam':
        return optim.Adam(params, lr=lr)
    elif optimizer_name.lower() == 'sgd':
        return optim.SGD(params, lr=lr)
    elif optimizer_name.lower() == 'rmsprop':
        return optim.RMSprop(params, lr=lr)
    else:
        raise ValueError(f"Unknown optimizer: {optimizer_name}")

if __name__ == '__main__':
    print("Optimizers module created.")
    # Example:
    # from torch import nn
    # model = nn.Linear(10, 1)
    # optimizer = get_optimizer(model.parameters(), 'adam', 0.001)
    # print(f"Instantiated optimizer: {optimizer}")
