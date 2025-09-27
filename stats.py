import pandas as pd

file_path = '~/Downloads/results_with_context_check.csv'
df = pd.read_csv(file_path)

counts = df['contains in context'].value_counts()

print(counts)
