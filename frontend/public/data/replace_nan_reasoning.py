import json

# Load the JSON file
with open('anomalous_farms_data_filtered.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Replace "nan" values in llm_reasoning with the specified text
replacement_text = "ฟาร์มรอบข้างเคียงมีการใส่ปุ๋ยแบบสูตรพิเศษ 87 แล้วมี Yield ที่สูงขึ้น สนใจอยากจะลองทำตามดูไหม"

updated_count = 0
for item in data:
    if item.get('llm_reasoning') == "nan":
        item['llm_reasoning'] = replacement_text
        updated_count += 1

# Save the updated JSON file
with open('anomalous_farms_data_filtered.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Updated {updated_count} records with the new llm_reasoning text")
print(f"Total records: {len(data)}")