import json
import pandas as pd

# Load JSON data
with open("test/end_to_end/results_v2.json") as f:
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

# Process results
for result in data["results"]["results"]:
    if result["testCase"]["vars"]["enable_test"] == "TRUE":
        is_plain = result["testCase"]["vars"]["is_plain_text"]

        if not result["gradingResult"]:
            print(f"[INFO] Skipping result with no grading result")
            continue

        for component in result["gradingResult"]["componentResults"]:
            test_type = component["assertion"]["value"]

            # Determine if this is a remove_latex test
            has_remove_latex = "remove_latex" in test_type
            latex_key = "no_latex" if has_remove_latex else "with_latex"

            # Check which base test type this belongs to
            for base_type in base_test_types:
                if base_type in test_type:
                    counts[base_type][(is_plain, latex_key)]["total"] += 1
                    if component["pass"]:
                        counts[base_type][(is_plain, latex_key)]["passed"] += 1
                    break

# Create DataFrames for each base test type
dfs = {}
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

# Save to CSV file
OUTPUT_CSV = "results_analysis_by_test_type.csv"
with open(OUTPUT_CSV, "w") as f:
    for base_type in base_test_types:
        f.write(f"\n{base_type}\n")
        dfs[base_type].to_csv(f)

print(f"\nResults have been saved to {OUTPUT_CSV}")
print("\nFinal tables:")
for base_type in base_test_types:
    print(f"\n{base_type}:")
    print(dfs[base_type])
