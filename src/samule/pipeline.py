import json
from src.samule.collector import collector
from src.samule.analyzer import analyzer
from src.samule.generator import generator

def run_pipeline():
    print("Starting SAMULE Self-Improvement Pipeline...")
    
    # 1. Collect Traces
    traces = collector.fetch_traces(limit=10)
    if not traces:
        print("No traces found. Run the agent first to generate data.")
        return
    
    # 2. Analyze Failures
    failures = analyzer.identify_failures(traces)
    
    if not failures:
        print("No failures detected by analyzer. Pipeline complete.")
        return
    
    print(f"Processing {len(failures)} failures...")
    
    # 3. Generate Synthetic Data
    dataset = []
    for failure in failures:
        print(f"Generating correction for trace {failure.get('id', 'unknown')}...")
        try:
            example = generator.create_sft_example(failure)
            dataset.append(example)
        except Exception as e:
            print(f"Failed to generate correction: {e}")
            
    # 4. Export Dataset
    if dataset:
        output_file = "data/sft_dataset.json"
        with open(output_file, "w") as f:
            json.dump(dataset, f, indent=2)
        print(f"Successfully exported {len(dataset)} SFT examples to {output_file}")
    else:
        print("No dataset generated.")

if __name__ == "__main__":
    run_pipeline()
