import numpy as np
import pandas as pd

df = pd.read_csv(r"\test\files\recipes.csv")

# print(df.iloc[1])
new_df = df.iloc[1]

new_df.to_csv(r"\test\files\single.csv")
