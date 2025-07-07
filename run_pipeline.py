#!/usr/bin/env python3
"""
AgeRate Prompt Evaluation Pipeline
Unified runner for the complete evaluation workflow.
"""

import sys
import json
import argparse
from pathlib import Path

def run_data_enrichment(limit_rows=None, test_random=False):
    """Run data enrichment pipeline."""
    print("🔄 Running data enrichment pipeline...")
    sys.path.append("02_data_preparation")
    from enrichment_pipeline import enrich_dataset
    
    input_csv = "05_artifacts/datasets/youtube_channel_ground_truth.csv"
    output_csv = "05_artifacts/datasets/youtube_channel_ground_truth_enriched.csv"
    
    return enrich_dataset(input_csv, output_csv, limit_rows, test_random)

def run_prompt_evaluation(variant="v11_enriched", dataset="gold"):
    """Run prompt evaluation."""
    print(f"🔄 Running prompt evaluation with variant: {variant}")
    sys.path.append("03_evaluation")
    from prompt_evaluator import SimpleAgerateEval, load_samples
    
    # Load dataset
    if dataset == "gold":
        dataset_path = "05_artifacts/datasets/gold_dataset.jsonl"
    else:
        print(f"❌ Unknown dataset: {dataset}")
        return None
    
    if not Path(dataset_path).exists():
        print(f"❌ Dataset not found: {dataset_path}")
        return None
    
    samples = load_samples(dataset_path)
    evaluator = SimpleAgerateEval(variant=variant)
    
    results = []
    for sample in samples:
        result = evaluator.eval_sample(sample)
        results.append(result)
        print(f"✓ {sample['input']}: Expected {result['expected_age']} | Predicted {result['predicted_age']} | MAE {result['mae']}")
    
    # Calculate summary metrics
    valid_results = [r for r in results if r['valid_response']]
    if valid_results:
        avg_mae = sum(r['mae'] for r in valid_results) / len(valid_results)
        exact_matches = sum(r['exact_match'] for r in valid_results)
        accuracy = exact_matches / len(valid_results)
        
        summary = {
            "variant": variant,
            "total_samples": len(results),
            "valid_responses": len(valid_results),
            "average_mae": avg_mae,
            "accuracy": accuracy,
            "results": results
        }
        
        # Save results
        output_path = f"04_experiments/benchmarks/{variant}_evaluation.json"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Summary:")
        print(f"   Average MAE: {avg_mae:.2f}")
        print(f"   Accuracy: {accuracy:.1%}")
        print(f"   Valid responses: {len(valid_results)}/{len(results)}")
        print(f"   Results saved: {output_path}")
        
        return summary
    else:
        print("❌ No valid responses generated")
        return None

def main():
    parser = argparse.ArgumentParser(description="AgeRate Prompt Evaluation Pipeline")
    parser.add_argument("command", choices=["enrich", "evaluate", "full"], 
                       help="Pipeline command to run")
    parser.add_argument("--variant", default="v11_enriched", 
                       help="Prompt variant for evaluation")
    parser.add_argument("--dataset", default="gold", 
                       help="Dataset to use for evaluation")
    parser.add_argument("--limit-rows", type=int, 
                       help="Limit rows for enrichment (testing)")
    parser.add_argument("--test-random", action="store_true",
                       help="Use random sampling for enrichment testing")
    
    args = parser.parse_args()
    
    print(f"🚀 Starting AgeRate Pipeline: {args.command}")
    
    if args.command in ["enrich", "full"]:
        try:
            result = run_data_enrichment(args.limit_rows, args.test_random)
            print(f"✅ Data enrichment completed: {result}")
        except Exception as e:
            print(f"❌ Data enrichment failed: {e}")
            if args.command == "full":
                return
    
    if args.command in ["evaluate", "full"]:
        try:
            result = run_prompt_evaluation(args.variant, args.dataset)
            if result:
                print("✅ Prompt evaluation completed")
            else:
                print("❌ Prompt evaluation failed")
        except Exception as e:
            print(f"❌ Prompt evaluation failed: {e}")

if __name__ == "__main__":
    main()