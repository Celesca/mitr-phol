import pandas as pd
import json
import ast

# Read the CSV file
df = pd.read_csv('anomalous_farms_df.csv')

# Select only the required columns
required_columns = [
    'farm_id', 'farmer_name', 'neighborhood_avg_yield_difference',
    'is_anomaly', 'llm_reasoning', 'nearest_neighbors_indices',
    'latitude', 'longitude'
]

# Filter the dataframe to only include required columns
filtered_df = df[required_columns].copy()

# Convert nearest_neighbors_indices from string to list
def parse_neighbors_indices(indices_str):
    try:
        # Parse the string representation of list
        return ast.literal_eval(indices_str)
    except:
        return []

filtered_df['nearest_neighbors_indices'] = filtered_df['nearest_neighbors_indices'].apply(parse_neighbors_indices)

# Convert to the format expected by the React app
farm_data = []
for _, row in filtered_df.iterrows():
    farm_data.append({
        'farm_id': str(row['farm_id']),
        'farmer_name': str(row['farmer_name']),
        'neighborhood_avg_yield_difference': float(row['neighborhood_avg_yield_difference']),
        'is_anomaly': bool(row['is_anomaly']),
        'llm_reasoning': str(row['llm_reasoning']),
        'nearest_neighbors_indices': row['nearest_neighbors_indices'],
        'latitude': float(row['latitude']),
        'longitude': float(row['longitude'])
    })

# Save to JSON file
with open('anomalous_farms_data.json', 'w', encoding='utf-8') as f:
    json.dump(farm_data, f, ensure_ascii=False, indent=2)

print(f"Converted {len(farm_data)} farm records to JSON format")
print("Sample record:")
print(json.dumps(farm_data[0], ensure_ascii=False, indent=2))