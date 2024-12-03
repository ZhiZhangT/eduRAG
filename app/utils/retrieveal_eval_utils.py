# Contains utility functions for retrieval evaluation for the RAG pipeline.
# Expects two lists of docID strings, one for the ground truth and one for the predictions.
# Returns a dictionary with the following keys:
#     - "precision": precision score
#     - "recall": recall score
#     - "f1": F1 score
#     - "jaccard": Jaccard score
#     - "mean_avg_prec": Mean Average Precision score
#     - "mrr": Mean Reciprocal Rank score
#     - "doc_ids": list of document IDs in the intersection of the ground truth and predictions

from typing import Dict, List, Union

def calculate_mean_avg_prec(ground_truth: List[str], predictions: List[str]) -> float:
    # Calculate mean average precision
    avg_prec = 0
    num_correct = 0
    for i, doc_id in enumerate(predictions):
        if doc_id in ground_truth:
            num_correct += 1
            avg_prec += num_correct / (i + 1)
    return avg_prec / len(ground_truth) if len(ground_truth) > 0 else 0

def calculate_mrr(ground_truth: List[str], predictions: List[str]) -> float:
    # Calculate mean reciprocal rank
    for i, doc_id in enumerate(predictions):
        if doc_id in ground_truth:
            return 1 / (i + 1)
    return 0

def evaluate_retrieval(ground_truth: List[str], predictions: List[str]) -> Dict[str, Union[float, List[str]]]:
    
    # Calculate precision, recall, F1, Jaccard, MAP, MRR
    intersection = set(ground_truth).intersection(set(predictions))
    precision = len(intersection) / len(predictions) if len(predictions) > 0 else 0
    recall = len(intersection) / len(ground_truth) if len(ground_truth) > 0 else 0
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if precision + recall > 0
        else 0
    )
    jaccard = len(intersection) / len(set(ground_truth).union(set(predictions)))
    mean_avg_prec = calculate_mean_avg_prec(ground_truth, predictions)
    mrr = calculate_mrr(ground_truth, predictions)
    doc_ids = list(intersection)
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "jaccard": jaccard,
        "mean_avg_prec": mean_avg_prec,
        "mrr": mrr,
        "doc_ids": doc_ids,
    }