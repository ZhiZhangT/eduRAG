import json
import pandas as pd

# Load JSON data
with open("test/end_to_end/results/results_plain_text_vs_latex_3.json") as f:
    data = json.load(f)

# Define base test types
base_test_types = ["python_script", "llm_step_by_step", "llm_judge"]

# Initialize dictionaries for counting
counts = {}
for base_type in base_test_types:
    counts[base_type] = {
        ("TRUE", "with_latex"): {"total": 0, "passed": 0},
        ("TRUE", "no_latex"): {"total": 0, "passed": 0},
        ("FALSE", "with_latex"): {"total": 0, "passed": 0},
        ("FALSE", "no_latex"): {"total": 0, "passed": 0},
    }

# Initialize counters and lists for conditions
python_fail_others_pass = 0
all_fail = 0
python_pass_others_fail = 0
all_pass = 0
python_judge_pass_step_fail = 0
python_step_pass_judge_fail = 0
python_and_step_pass = 0

python_fail_others_pass_ids = []
all_fail_ids = []
python_pass_others_fail_ids = []
all_pass_ids = []
python_judge_pass_step_fail_ids = []
python_step_pass_judge_fail_ids = []
python_and_step_pass_ids = []

# Process results
for result in data["results"]["results"]:
    if result["testCase"]["vars"]["enable_test"] == "TRUE":
        is_plain = result["testCase"]["vars"]["is_plain_text"]
        query_id = result["response"]["output"]["query_id"]

        if not result["gradingResult"]:
            print(f"[INFO] Skipping result with no grading result")
            continue

        # Track results for each test type in this test case
        test_results = {base_type: False for base_type in base_test_types}

        for component in result["gradingResult"]["componentResults"]:
            test_type = component["assertion"]["value"]

            # Determine if this is a remove_latex test
            has_remove_latex = "remove_latex" in test_type
            latex_key = "no_latex" if has_remove_latex else "with_latex"

            # Check which base test type this belongs to and update counts
            for base_type in base_test_types:
                if base_type in test_type:
                    counts[base_type][(is_plain, latex_key)]["total"] += 1
                    if component["pass"]:
                        counts[base_type][(is_plain, latex_key)]["passed"] += 1
                        test_results[base_type] = True
                    break

        # Check conditions after processing all components for this test case
        if all(test_type in test_results for test_type in base_test_types):
            # Condition 1: Python and Judge pass but Step fails
            # NOTE: this MIGHT show us the number of times where step-by-step LLM is hallucinating
            if (
                test_results["python_script"]
                and test_results["llm_judge"]
                and not test_results["llm_step_by_step"]
            ):
                python_judge_pass_step_fail += 1
                python_judge_pass_step_fail_ids.append(query_id)

            # Condition 2: Python and Step pass but Judge fails
            # NOTE: this MIGHT show us the number of times where the LLM-as-judge is hallucinating
            if (
                test_results["python_script"]
                and test_results["llm_step_by_step"]
                and not test_results["llm_judge"]
            ):
                python_step_pass_judge_fail += 1
                python_step_pass_judge_fail_ids.append(query_id)

            # Condition 3: Python script fails but at least one other passes
            # TODO: manually check if the other test cases are hallucinating OR the python script is formatted wrongly
            if not test_results["python_script"] and (
                test_results["llm_step_by_step"] or test_results["llm_judge"]
            ):
                python_fail_others_pass += 1
                python_fail_others_pass_ids.append(query_id)

            # Condition 4: All test cases fail
            if not any(test_results.values()):
                all_fail += 1
                all_fail_ids.append(query_id)

            # Condition 5: Python script passes but all others fail
            # NOTE: this likely represents the number of times where the other llm-as-judge are hallucinating
            if (
                test_results["python_script"]
                and not test_results["llm_step_by_step"]
                and not test_results["llm_judge"]
            ):
                python_pass_others_fail += 1
                python_pass_others_fail_ids.append(query_id)
            # Condition 6: All test cases pass
            if all(test_results.values()):
                all_pass += 1
                all_pass_ids.append(query_id)

            # Condition 7: Python and Step pass
            if test_results["python_script"] and test_results["llm_step_by_step"]:
                python_and_step_pass += 1
                python_and_step_pass_ids.append(query_id)
dfs = {}
# First create the original DataFrames for individual test types
for base_type in base_test_types:
    rows = []
    for is_plain in ["TRUE", "FALSE"]:
        for latex_type in ["with_latex", "no_latex"]:
            total = counts[base_type][(is_plain, latex_type)]["total"]
            passed = counts[base_type][(is_plain, latex_type)]["passed"]
            percentage = (passed / total * 100) if total > 0 else 0
            rows.append(
                {
                    "is_plain_text": is_plain,
                    "latex_type": latex_type,
                    "total": total,
                    "passed": passed,
                    "percentage": f"{percentage:.1f}%",
                }
            )

    df = pd.DataFrame(rows)
    df["condition"] = df.apply(
        lambda x: f"plain_text={x['is_plain_text']}, {x['latex_type']}", axis=1
    )
    dfs[base_type] = df.set_index("condition")[["total", "passed", "percentage"]]

# Create a new DataFrame for Python & Step combined statistics
combined_rows = []
for is_plain in ["TRUE", "FALSE"]:
    for latex_type in ["with_latex", "no_latex"]:
        # Count cases where both Python and Step pass
        total = counts["python_script"][(is_plain, latex_type)]["total"]
        python_passed = set()
        step_passed = set()

        # Go through results again to count combined passes
        for result in data["results"]["results"]:
            if (
                result["testCase"]["vars"]["enable_test"] == "TRUE"
                and result["testCase"]["vars"]["is_plain_text"] == is_plain
            ):

                if result["gradingResult"]:
                    query_id = result["response"]["output"]["query_id"]
                    for component in result["gradingResult"]["componentResults"]:
                        test_type = component["assertion"]["value"]
                        has_remove_latex = "remove_latex" in test_type
                        current_latex_key = (
                            "no_latex" if has_remove_latex else "with_latex"
                        )

                        if current_latex_key == latex_type:
                            if "python_script" in test_type and component["pass"]:
                                python_passed.add(query_id)
                            elif "llm_step_by_step" in test_type and component["pass"]:
                                step_passed.add(query_id)

        # Count cases where both passed
        both_passed = len(python_passed.intersection(step_passed))
        percentage = (both_passed / total * 100) if total > 0 else 0

        combined_rows.append(
            {
                "is_plain_text": is_plain,
                "latex_type": latex_type,
                "total": total,
                "passed": both_passed,
                "percentage": f"{percentage:.1f}%",
            }
        )

df_combined = pd.DataFrame(combined_rows)
df_combined["condition"] = df_combined.apply(
    lambda x: f"plain_text={x['is_plain_text']}, {x['latex_type']}", axis=1
)
dfs["python_and_step_combined"] = df_combined.set_index("condition")[
    ["total", "passed", "percentage"]
]

# Update additional statistics DataFrame with new statistics
additional_stats = pd.DataFrame(
    [
        {
            "Statistic": "Python script fails but others pass",
            "Count": python_fail_others_pass,
        },
        {"Statistic": "All test cases fail", "Count": all_fail},
        {
            "Statistic": "Python script passes but others fail",
            "Count": python_pass_others_fail,
        },
        {"Statistic": "All test cases pass", "Count": all_pass},
        {
            "Statistic": "Python & Judge pass but Step fails",
            "Count": python_judge_pass_step_fail,
        },
        {
            "Statistic": "Python & Step pass but Judge fails",
            "Count": python_step_pass_judge_fail,
        },
        {
            "Statistic": "Python & Step pass (regardless of Judge)",
            "Count": python_and_step_pass,
        },
    ]
).set_index("Statistic")

# Update DataFrame for IDs with the new category
ids_rows = []
for id_value in python_fail_others_pass_ids:
    ids_rows.append({"Category": "Python script fails but others pass", "ID": id_value})
for id_value in all_fail_ids:
    ids_rows.append({"Category": "All test cases fail", "ID": id_value})
for id_value in python_pass_others_fail_ids:
    ids_rows.append(
        {"Category": "Python script passes but others fail", "ID": id_value}
    )
for id_value in all_pass_ids:
    ids_rows.append({"Category": "All test cases pass", "ID": id_value})
for id_value in python_judge_pass_step_fail_ids:
    ids_rows.append({"Category": "Python & Judge pass but Step fails", "ID": id_value})
for id_value in python_step_pass_judge_fail_ids:
    ids_rows.append({"Category": "Python & Step pass but Judge fails", "ID": id_value})
for id_value in python_and_step_pass_ids:
    ids_rows.append(
        {"Category": "Python & Step pass (regardless of Judge)", "ID": id_value}
    )
ids_df = pd.DataFrame(ids_rows)
# Save to CSV file
OUTPUT_CSV = "results_analysis_plain_text_vs_latex_3.csv"
with open(OUTPUT_CSV, "w", newline="") as f:
    # Write test type statistics
    for base_type in base_test_types:
        f.write(f"\n{base_type}\n")
        dfs[base_type].to_csv(f)

    # Write combined Python & Step statistics
    f.write("\nPython & Step Combined Passes\n")
    dfs["python_and_step_combined"].to_csv(f)

    # Write additional statistics
    f.write("\nAdditional Statistics\n")
    additional_stats.to_csv(f)

    # Write IDs section header
    f.write("\nTest Case IDs\n")
    f.write("Category,ID\n")

    # Write each ID on a separate row
    for _, row in ids_df.iterrows():
        f.write(f"{row['Category']},{row['ID']}\n")

print(f"\nResults have been saved to {OUTPUT_CSV}")
print("\nFinal tables:")
for base_type in base_test_types:
    print(f"\n{base_type}:")
    print(dfs[base_type])

print("\nPython & Step Combined Passes:")
print(dfs["python_and_step_combined"])

print("\nAdditional Statistics:")
print(additional_stats)

print("\nTest Case IDs by Category:")
for category in ids_df["Category"].unique():
    print(f"\n{category}:")
    print(ids_df[ids_df["Category"] == category]["ID"].tolist())
