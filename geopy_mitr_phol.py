import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import KDTree
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import folium
import os
import textwrap
from crewai import LLM, Agent, Task, Crew

def load_and_merge_data():
    """Load CSV files and merge them into a single dataframe."""
    daily_df = pd.read_csv("Daily_Farm_Log.csv")
    farm_profile = pd.read_csv("Farm_Profile.csv")
    perf_df = pd.read_csv("Sugarcane_Performance.csv")

    merged_df = pd.merge(daily_df, farm_profile, on='farm_id')
    merged_df = pd.merge(merged_df, perf_df, on='farm_id')

    print("Data loaded and merged successfully")
    print(f"Shape: {merged_df.shape}")
    print(merged_df.head())

    return merged_df

def create_process_embeddings(merged_df):
    """Create embeddings for process descriptions."""
    process_columns = [
        'irrigation_frequency_per_month',
        'irrigation_method_encoded',
        'drainage_effort_encoded',
        'soil_test_frequency_per_year',
        'fertilizer_type_organic_ratio',
        'foliar_spray_frequency_per_month',
        'leaf_stripping_frequency_per_month',
        'trashing_method_encoded',
        'hilling_up_encoded',
        'cultivation_frequency_per_cycle',
        'preventive_spraying_frequency',
        'scouting_frequency_per_month',
        'pesticide_toxicity_level',
        'soil_type',
        'cane_variety',
        'planting_type'
    ]

    merged_df['combined_process_text'] = merged_df[process_columns].astype(str).agg(' '.join, axis=1)

    print("Combined process text created")
    print(merged_df[['combined_process_text']].head())

    # Load sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    merged_df['process_embeddings'] = merged_df['combined_process_text'].apply(lambda x: model.encode(x))

    print("Process embeddings created")
    print(merged_df[['process_embeddings']].head())

    return merged_df

def define_local_neighborhoods(merged_df, k=10):
    """Define local neighborhoods using KD-tree for geographical proximity."""
    geo_data = merged_df[['latitude', 'longitude']].values

    # Build KDTree
    kdtree = KDTree(geo_data, leaf_size=15)

    # Query for k+1 nearest neighbors (including self)
    neighbor_indices = kdtree.query(geo_data, k=k + 1, return_distance=False)

    # Store indices excluding self
    merged_df['nearest_neighbors_indices'] = [indices[1:].tolist() for indices in neighbor_indices]

    print(f"Local neighborhoods defined with k={k}")
    print(merged_df[['farm_id', 'nearest_neighbors_indices']].head())

    return merged_df

def visualize_neighborhood(merged_df, farm_index=4, k=10):
    """Visualize a farm and its neighbors."""
    selected_farm = merged_df.iloc[farm_index]
    neighbor_indices = selected_farm['nearest_neighbors_indices']
    neighbors = merged_df.loc[neighbor_indices]

    plt.figure(figsize=(10, 8))

    # Plot all farms
    plt.scatter(merged_df['longitude'], merged_df['latitude'], c='gray', alpha=0.5, s=10, label='All Farms')

    # Highlight selected farm
    plt.scatter(selected_farm['longitude'], selected_farm['latitude'], c='red', s=100,
                label=f'Selected Farm (ID: {selected_farm["farm_id"]})', edgecolors='black')

    # Highlight neighbors
    plt.scatter(neighbors['longitude'], neighbors['latitude'], c='blue', s=50,
                label=f'{k} Nearest Neighbors', edgecolors='black')

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Farm Locations and Nearest Neighbors for Farm ID {selected_farm["farm_id"]}')
    plt.legend()
    plt.grid(True)
    plt.savefig('farm_neighborhood_visualization.png', dpi=300, bbox_inches='tight')
    plt.show()

    print("Neighborhood visualization saved as 'farm_neighborhood_visualization.png'")

def detect_anomalies(merged_df, threshold=1.0):
    """Detect performance anomalies by comparing to neighborhood averages."""
    neighborhood_avg_ccs_list = []
    for index, row in merged_df.iterrows():
        neighbor_indices = row['nearest_neighbors_indices']
        neighborhood_ccs = merged_df.loc[neighbor_indices, 'actual_ccs']
        neighborhood_avg_ccs = neighborhood_ccs.mean()
        neighborhood_avg_ccs_list.append(neighborhood_avg_ccs)

    merged_df['neighborhood_avg_ccs'] = neighborhood_avg_ccs_list
    merged_df['ccs_difference'] = merged_df['actual_ccs'] - merged_df['neighborhood_avg_ccs']
    merged_df['is_anomaly'] = abs(merged_df['ccs_difference']) > threshold

    print(f"Anomalies detected with threshold {threshold}")
    print(f"Number of anomalies: {merged_df['is_anomaly'].sum()}")
    print(merged_df[['farm_id', 'actual_ccs', 'neighborhood_avg_ccs', 'ccs_difference', 'is_anomaly']].head())

    return merged_df

def compare_process_actions(merged_df):
    """Compare process actions for anomalous farms using embedding similarity."""
    anomalous_farms_df = merged_df[merged_df['is_anomaly'] == True].copy()

    if anomalous_farms_df.empty:
        print("No anomalous farms found")
        return anomalous_farms_df

    cosine_similarities = []

    for index, row in anomalous_farms_df.iterrows():
        anomalous_embedding = row['process_embeddings']
        neighbor_indices = row['nearest_neighbors_indices']

        neighbor_embeddings = merged_df.loc[neighbor_indices, 'process_embeddings'].tolist()

        # Calculate cosine similarity
        similarities = [cosine_similarity([anomalous_embedding], [neighbor_embedding])[0][0]
                       for neighbor_embedding in neighbor_embeddings]
        cosine_similarities.append(similarities)

    anomalous_farms_df['neighbor_process_similarity'] = cosine_similarities

    print("Process action comparisons completed")
    print(anomalous_farms_df[['farm_id', 'neighbor_process_similarity']].head())

    return anomalous_farms_df

def setup_llm():
    """Setup LLM using environment variables for AWS credentials."""
    # Use environment variables instead of Google Colab userdata
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')

    if not aws_access_key or not aws_secret_key:
        raise ValueError("AWS credentials not found in environment variables. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")

    llm = LLM(model="us.anthropic.claude-sonnet-4-20250514-v1:0",
              aws_access_key_id=aws_access_key,
              aws_secret_access_key=aws_secret_key,
              aws_region_name=aws_region)

    return llm

def analyze_process_differences_with_llm(anomalous_farm_process, neighbor_processes, ccs_difference, llm):
    """Analyze farming process differences using LLM."""
    prompt = textwrap.dedent(f"""
    Analyze the following farming process descriptions. Farm A is an anomalous farm with a CCS difference of {ccs_difference:.2f} compared to its neighbors. The other farms (Neighbors) represent the typical processes in Farm A's local area.

    Farm A Process Description:
    {anomalous_farm_process}

    Neighbor Process Descriptions:
    {chr(10).join(neighbor_processes)}

    Identify the key differences in farming practices between Farm A and its neighbors. Based on these differences, hypothesize potential reasons why Farm A's CCS ('actual_ccs') is {'lower' if ccs_difference < 0 else 'higher'} than the neighborhood average. Consider factors such as irrigation, fertilization, pest control, soil management, and harvesting practices. Provide a concise summary of the key differences and hypothesized reasons.
    """)

    # Define agent
    process_analyzer_agent = Agent(
        role='Farming Process Analyst',
        goal='Identify key differences in farming practices and hypothesize reasons for performance anomalies.',
        backstory='An expert in agricultural practices and data analysis, capable of comparing farming processes and inferring potential impacts on crop quality and yield.',
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    # Define task
    analysis_task = Task(
        description=prompt,
        expected_output='A concise summary of key differences in farming practices and hypothesized reasons for the CCS anomaly.',
        agent=process_analyzer_agent
    )

    # Create and run crew
    crew = Crew(
        agents=[process_analyzer_agent],
        tasks=[analysis_task],
        verbose=False
    )

    try:
        result = crew.kickoff()
        return result
    except Exception as e:
        return f"Error during LLM call: {e}"

def perform_llm_reasoning(merged_df, anomalous_farms_df, limit=5):
    """Perform LLM reasoning for anomalous farms."""
    if anomalous_farms_df.empty:
        print("No anomalous farms to analyze")
        return anomalous_farms_df

    try:
        llm = setup_llm()
        print("LLM setup successful")
    except ValueError as e:
        print(f"LLM setup failed: {e}")
        print("Skipping LLM reasoning")
        return anomalous_farms_df

    llm_reasoning_list = []

    # Limit to specified number of farms
    for index, row in anomalous_farms_df.head(limit).iterrows():
        anomalous_farm_process = row['combined_process_text']
        neighbor_indices = row['nearest_neighbors_indices']
        ccs_difference = row['ccs_difference']

        neighbor_processes = merged_df.loc[neighbor_indices, 'combined_process_text'].tolist()

        # Get LLM reasoning
        llm_reasoning = analyze_process_differences_with_llm(
            anomalous_farm_process, neighbor_processes, ccs_difference, llm)
        llm_reasoning_list.append(llm_reasoning)

        print(f"LLM analysis completed for farm {row['farm_id']}")

    # Store results
    anomalous_farms_df.loc[anomalous_farms_df.head(limit).index, 'llm_reasoning'] = llm_reasoning_list

    print("LLM reasoning completed")
    print(anomalous_farms_df[['farm_id', 'ccs_difference', 'llm_reasoning']].head())

    return anomalous_farms_df

def create_interactive_map(merged_df, map_center=[13.736717, 100.523186], zoom_start=6,
                          min_lat=13.5, max_lat=14.0, min_lon=100.0, max_lon=101.0):
    """Create an interactive map of farm locations."""
    # Create map
    m = folium.Map(location=map_center, zoom_start=zoom_start)

    # Filter farms within bounding box
    focused_farms = merged_df[
        (merged_df['latitude'] >= min_lat) & (merged_df['latitude'] <= max_lat) &
        (merged_df['longitude'] >= min_lon) & (merged_df['longitude'] <= max_lon)
    ].copy()

    # Add markers for farms
    for index, row in focused_farms.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Farm ID: {row['farm_id']}<br>CCS: {row['actual_ccs']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Select a farm and highlight its neighbors
    if not focused_farms.empty:
        selected_farm = focused_farms.iloc[0]
        selected_farm_id = selected_farm['farm_id']

        # Find original index
        original_index = merged_df[merged_df['farm_id'] == selected_farm_id].index[0]
        neighbor_indices = merged_df.loc[original_index, 'nearest_neighbors_indices']
        neighbors = merged_df.loc[neighbor_indices]

        # Highlight selected farm
        folium.Marker(
            location=[selected_farm['latitude'], selected_farm['longitude']],
            popup=f"Selected Farm ID: {selected_farm['farm_id']}<br>CCS: {selected_farm['actual_ccs']}",
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)

        # Highlight neighbors
        for index, row in neighbors.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"Neighbor Farm ID: {row['farm_id']}<br>CCS: {row['actual_ccs']}",
                icon=folium.Icon(color='green', icon='leaf')
            ).add_to(m)

        # Fit bounds
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

        # Save map
        m.save('farm_locations_map.html')
        print("Interactive map saved as 'farm_locations_map.html'")
    else:
        print("No farms found within the specified bounding box")

def summarize_findings(merged_df, anomalous_farms_df):
    """Summarize the analysis findings."""
    print("\n" + "="*50)
    print("ANOMALY DETECTION SUMMARY")
    print("="*50)

    print(f"Total farms analyzed: {len(merged_df)}")
    print(f"Anomalous farms detected: {len(anomalous_farms_df)}")
    print(".1f")

    if not anomalous_farms_df.empty:
        print("\nAnomalous farms details:")
        display_cols = ['farm_id', 'ccs_difference', 'neighbor_process_similarity', 'llm_reasoning']
        available_cols = [col for col in display_cols if col in anomalous_farms_df.columns]
        print(anomalous_farms_df[available_cols])

    print("\nKey Findings:")
    print("- Farms with CCS significantly different from neighbors were identified")
    print("- Process embeddings were created and compared using cosine similarity")
    print("- LLM analysis provided insights into potential reasons for anomalies")
    print("- Interactive map shows geographical distribution of farms")

    print("\nFiles created:")
    print("- farm_neighborhood_visualization.png: Neighborhood visualization")
    print("- farm_locations_map.html: Interactive map of farm locations")

def main():
    """Main function to run the complete analysis pipeline."""
    print("Starting sugarcane farm anomaly detection analysis...")

    # Load and merge data
    merged_df = load_and_merge_data()

    # Create process embeddings
    merged_df = create_process_embeddings(merged_df)

    # Define local neighborhoods
    merged_df = define_local_neighborhoods(merged_df)

    # Visualize a neighborhood
    visualize_neighborhood(merged_df)

    # Detect anomalies
    merged_df = detect_anomalies(merged_df)

    # Compare process actions
    anomalous_farms_df = compare_process_actions(merged_df)

    # Perform LLM reasoning
    anomalous_farms_df = perform_llm_reasoning(merged_df, anomalous_farms_df)

    # Create interactive map
    create_interactive_map(merged_df)

    # Summarize findings
    summarize_findings(merged_df, anomalous_farms_df)

    print("\nAnalysis completed successfully!")

if __name__ == "__main__":
    main()