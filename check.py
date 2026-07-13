import pandas as pd

for h in [0, 1, 2]:
    print(f"\n===== HEADER = {h} =====")
    df = pd.read_excel("data/raw/analysis.xlsx", header=h)
    print(df.columns.tolist())
    print(df.head(2))