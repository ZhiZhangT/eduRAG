import json
import pandas as pd
import os

# Load and combine JSON data from multiple files
json_files = [
    "test/end_to_end/results1.json",
    "test/end_to_end/results1_mean_median.json",
    "test/end_to_end/results234.json",
]

# Initialize combined data structure
combined_data = {"results": {"results": []}}

# Load and combine each JSON file
for json_file in json_files:
    try:
        with open(json_file) as f:
            file_data = json.load(f)
            # Append results from each file to the combined results
            combined_data["results"]["results"].extend(file_data["results"]["results"])
    except FileNotFoundError:
        print(f"Warning: File {json_file} not found")
    except json.JSONDecodeError:
        print(f"Warning: File {json_file} contains invalid JSON")

# Use combined_data instead of data for the rest of the script
data = combined_data


# Initialize dictionary to store results
results = {}

# Process results
for result in data["results"]["results"]:
    if result["testCase"]["vars"]["enable_test"] != "TRUE":
        continue

    # Extract variables for grouping
    use_image = result["testCase"]["vars"]["use_image"]
    retrieved_docs_count = result["testCase"]["vars"]["retrieved_docs_count"]
    use_few_shot = result["testCase"]["vars"]["use_few_shot"]

    # Create key for grouping
    group_key = (use_image, retrieved_docs_count, use_few_shot)

    # Initialize counters for this group if not exists
    if group_key not in results:
        results[group_key] = {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "total": 0}

    if not result["gradingResult"]:
        continue

    # Track results for python_script and llm_step_by_step
    python_result = False
    step_result = False

    for component in result["gradingResult"]["componentResults"]:
        test_type = component["assertion"]["value"]
        if "python_script" in test_type:
            python_result = component["pass"]
        elif "llm_step_by_step" in test_type:
            step_result = component["pass"]

    # Update counters
    results[group_key]["total"] += 1
    if python_result and step_result:
        results[group_key]["PASS"] += 1
    elif python_result or step_result:
        results[group_key]["PARTIAL"] += 1
    else:
        results[group_key]["FAIL"] += 1

# Convert results to DataFrame
rows = []
for (use_image, retrieved_docs_count, use_few_shot), counts in results.items():
    # Calculate pass percentage
    pass_percentage = (
        (counts["PASS"] / counts["total"] * 100) if counts["total"] > 0 else 0
    )

    row = {
        "use_image": use_image,
        "retrieved_docs_count": retrieved_docs_count,
        "use_few_shot": use_few_shot,
        "PASS": counts["PASS"],
        "PARTIAL": counts["PARTIAL"],
        "FAIL": counts["FAIL"],
        "total": counts["total"],
        "PASS_PERCENTAGE": f"{pass_percentage:.2f}%",
    }
    rows.append(row)

new_df = pd.DataFrame(rows)

# Sort DataFrame by PASS_PERCENTAGE in descending order
new_df = new_df.sort_values(by="PASS_PERCENTAGE", ascending=False)

# File path
output_file = "results_matrix_analysis.csv"

# Check if file exists and load it
if os.path.exists(output_file):
    existing_df = pd.read_csv(output_file)

    # Create a merge key for comparison
    merge_cols = ["use_image", "retrieved_docs_count", "use_few_shot"]

    # Find new combinations that don't exist in the current file
    existing_combinations = set(existing_df[merge_cols].apply(tuple, axis=1))
    new_combinations = set(new_df[merge_cols].apply(tuple, axis=1))

    # Only add rows that don't exist in the current file
    new_rows = new_df[
        ~new_df[merge_cols].apply(tuple, axis=1).isin(existing_combinations)
    ]

    if not new_rows.empty:
        # Concatenate new rows with existing DataFrame
        final_df = pd.concat([existing_df, new_rows], ignore_index=True)
        # Sort the final DataFrame by PASS_PERCENTAGE
        final_df = final_df.sort_values(by="PASS_PERCENTAGE", ascending=False)
        final_df.to_csv(output_file, index=False)
        print(f"Updated {output_file} with {len(new_rows)} new combinations")
    else:
        print("No new combinations to add")
else:
    # Create new file
    new_df.to_csv(output_file, index=False)
    print(f"Created new file: {output_file}")

print("\nFinal Results (sorted by PASS_PERCENTAGE):")
print(new_df)
