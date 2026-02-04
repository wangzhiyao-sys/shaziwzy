from torch.optim.lr_scheduler import ReduceLROnPlateau, StepLR

def get_scheduler(optimizer, scheduler_name: str = 'plateau', **kwargs):
    """
    Returns a learning rate scheduler instance.
    """
    if scheduler_name == 'plateau':
        # Reduce learning rate when a metric has stopped improving.
        return ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=5, **kwargs)
    elif scheduler_name == 'step':
        # Decays the learning rate of each parameter group by gamma every step_size epochs.
        return StepLR(optimizer, step_size=10, gamma=0.1, **kwargs)
    else:
        # Return None if no scheduler is specified
        return None

if __name__ == '__main__':
    print("Schedulers module created.")
    # Example:
    # from torch import nn, optim
    # model = nn.Linear(10, 1)
    # optimizer = optim.Adam(model.parameters(), lr=0.001)
    # scheduler = get_scheduler(optimizer, 'plateau')
    # print(f"Instantiated scheduler: {scheduler}")
