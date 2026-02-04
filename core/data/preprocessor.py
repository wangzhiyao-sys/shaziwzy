import numpy as np
import pandas as pd
from typing import List, Dict, Any

class DataPreprocessor:
    def __init__(self):
        pass

    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Performs data cleaning, such as handling missing values.
        """
        data = data.dropna()
        return data

    def feature_engineering(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Creates new features from existing ones.
        """
        # Example: length of the content
        if 'content' in data.columns:
            data['content_length'] = data['content'].apply(len)
        return data

    def augment_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Performs data augmentation.
        Placeholder for more complex augmentation techniques.
        """
        # Example: simple duplication for minority class
        if 'label' in data.columns and data['label'].nunique() > 1:
            minority_class = data['label'].value_counts().idxmin()
            minority_data = data[data['label'] == minority_class]
            augmented_data = pd.concat([data, minority_data], ignore_index=True)
            return augmented_data
        return data

    def preprocess(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Full preprocessing pipeline.
        """
        df = pd.DataFrame(data)
        df = self.clean_data(df)
        df = self.feature_engineering(df)
        # Augmentation might be better applied only to the training set
        # df = self.augment_data(df)
        return df

if __name__ == '__main__':
    preprocessor = DataPreprocessor()
    print("Data preprocessor module created.")
    # Example usage:
    # sample_data = [{'content': 'I am a villager', 'label': 0}, {'content': 'Player 3 is a wolf', 'label': 1}]
    # processed_df = preprocessor.preprocess(sample_data)
    # print(processed_df)
