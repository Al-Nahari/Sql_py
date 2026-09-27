import pandas as pd
import path
file_path = path("data/raw/students.csv")
df = pd.read_csv(file_path)

print(df.shape)
print(df.columns.tolist)
print(df.dtypes)
print(df.isna().sum())