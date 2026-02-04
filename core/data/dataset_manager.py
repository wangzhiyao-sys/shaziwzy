from sklearn.model_selection import train_test_split
import pandas as pd

class DatasetManager:
    def __init__(self, test_size=0.2, val_size=0.2, random_state=42):
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state

    def split_data(self, df: pd.DataFrame):
        """
        Splits a DataFrame into training, validation, and test sets.
        """
        if df.empty:
            return None, None, None
            
        features = df.drop('label', axis=1)
        labels = df['label']

        # Split into train and temp (test)
        X_train, X_temp, y_train, y_temp = train_test_split(
            features, labels, test_size=self.test_size, random_state=self.random_state, stratify=labels if labels.nunique() > 1 else None
        )

        # Split temp into validation and test
        val_size_adjusted = self.val_size / (self.test_size + self.val_size)
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=val_size_adjusted, random_state=self.random_state, stratify=y_temp if y_temp.nunique() > 1 else None
        )

        return (X_train, y_train), (X_val, y_val), (X_test, y_test)

if __name__ == '__main__':
    manager = DatasetManager()
    print("Dataset manager module created.")
    # Example usage:
    # data = {'feature1': range(100), 'label': [0]*50 + [1]*50}
    # df = pd.DataFrame(data)
    # train_set, val_set, test_set = manager.split_data(df)
    # if train_set:
    #     print(f"Train set size: {len(train_set[0])}")
    #     print(f"Validation set size: {len(val_set[0])}")
    #     print(f"Test set size: {len(test_set[0])}")

