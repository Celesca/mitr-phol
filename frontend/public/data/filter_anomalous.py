import json
import random

# Load the original data
with open('anomalous_farms_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Original data: {len(data)} farms")

# Separate anomalous and normal farms
anomalous_farms = [farm for farm in data if farm['is_anomaly']]
normal_farms = [farm for farm in data if not farm['is_anomaly']]

print(f"Anomalous farms: {len(anomalous_farms)}")
print(f"Normal farms: {len(normal_farms)}")

# Keep only 20% of anomalous farms (reduce by 80%)
reduced_anomalous = random.sample(anomalous_farms, int(len(anomalous_farms) * 0.2))

print(f"Reduced anomalous farms: {len(reduced_anomalous)}")

# Combine the data
filtered_data = normal_farms + reduced_anomalous

# Shuffle to mix anomalous and normal farms
random.shuffle(filtered_data)

print(f"Final data: {len(filtered_data)} farms")

# Save the filtered data
with open('anomalous_farms_data_filtered.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=2)

print("Filtered data saved to anomalous_farms_data_filtered.json")