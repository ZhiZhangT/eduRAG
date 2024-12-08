import json
import pandas as pd

# Load JSON data
with open("test/end_to_end/results.json") as f:
    data = json.load(f)

# Initialize counters for each test type and plain_text flag
test_types = [
    "python_script",
    "llm_step_by_step",
    "llm_judge",
    "python_script_remove_latex",
    "llm_step_by_step_remove_latex",
    "llm_judge_remove_latex",
]
test_types_set = set(test_types)
results = {"TRUE": {t: 0 for t in test_types}, "FALSE": {t: 0 for t in test_types}}

# Process results
for result in data["results"]["results"]:
    if result["testCase"]["vars"]["enable_test"] == "TRUE":
        is_plain = result["testCase"]["vars"]["is_plain_text"]

        for component in result["gradingResult"]["componentResults"]:
            if component["pass"]:
                test_type = component["assertion"]["value"]
                for t in test_types:
                    # the ".py" is used to ensure that the test type is not a substring of another test type
                    # eg: we need to distinguish between "llm_judge" and "llm_judge_remove_latex"
                    if f"{t}.py" in test_type:
                        results[is_plain][t] += 1
                        break

# Create DataFrame
df = pd.DataFrame(results).T
df.index.name = "is_plain_text"

# Save to CSV file
df.to_csv("results_analysis.csv")

print("\nResults have been saved to results_analysis.csv")
