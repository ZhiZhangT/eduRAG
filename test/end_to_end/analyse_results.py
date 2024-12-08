import json
import pandas as pd

# Load JSON data
with open("test/end_to_end/results.json") as f:
    data = json.load(f)

test_types = [
    "python_script",
    "llm_step_by_step",
    "llm_judge",
    "python_script_remove_latex",
    "llm_step_by_step_remove_latex",
    "llm_judge_remove_latex",
]
test_types_set = set(test_types)

total_tests = {"TRUE": {t: 0 for t in test_types}, "FALSE": {t: 0 for t in test_types}}
passed_tests = {"TRUE": {t: 0 for t in test_types}, "FALSE": {t: 0 for t in test_types}}

# Process results
for result in data["results"]["results"]:
    if result["testCase"]["vars"]["enable_test"] == "TRUE":
        is_plain = result["testCase"]["vars"]["is_plain_text"]

        for component in result["gradingResult"]["componentResults"]:
            test_type = component["assertion"]["value"]
            for t in test_types:
                # the ".py" is used to ensure that the test type is not a substring of another test type
                # eg: we need to distinguish between "llm_judge" and "llm_judge_remove_latex"_with_percentages
                if f"{t}.py" in test_type:
                    total_tests[is_plain][t] += 1
                    if component["pass"]:
                        passed_tests[is_plain][t] += 1
                    break

# Calculate percentages
percentages = {"TRUE": {}, "FALSE": {}}

for is_plain in ["TRUE", "FALSE"]:
    for test_type in test_types:
        total = total_tests[is_plain][test_type]
        print(f"total: {total} passed: {passed_tests[is_plain][test_type]}")
        if total > 0:
            percentage = (passed_tests[is_plain][test_type] / total) * 100
        else:
            percentage = 0
        percentages[is_plain][test_type] = f"{percentage:.1f}%"

# Create DataFrames
raw_counts_df = pd.DataFrame(passed_tests).T
raw_counts_df.index.name = "is_plain_text"
raw_counts_df.columns = [f"{col}_count" for col in raw_counts_df.columns]

percentage_df = pd.DataFrame(percentages).T
percentage_df.index.name = "is_plain_text"
percentage_df.columns = [f"{col}_percentage" for col in percentage_df.columns]

# Combine the DataFrames
final_df = pd.concat([raw_counts_df, percentage_df], axis=1)

# Reorder columns to alternate between count and percentage
cols = []
for test_type in test_types:
    cols.extend([f"{test_type}_count", f"{test_type}_percentage"])
final_df = final_df[cols]

# Add total tests column
total_df = pd.DataFrame(total_tests).T
final_df["total_test_cases_per_column"] = total_tests["TRUE"]["python_script"]

OUTPUT_CSV = "results_analysis_with_percentages.csv"
# Save to CSV file
final_df.to_csv(OUTPUT_CSV)

print(f"\nResults have been saved to {OUTPUT_CSV}")
