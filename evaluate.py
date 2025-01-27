import sys
import pandas as pd

def evaluate_queries(df):
    pass

def load_dataset(benchmark_file_name):
    try:
        return pd.read_csv(benchmark_file_name)
    except Exception as ex:
        print(f'error loading {benchmark_file_name}: {ex} ')
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f'usage: python {sys.argv[0]} <input_file>')
        exit(1)
    benchmark_file_name = sys.argv[1]
    print(f'loading {benchmark_file_name}...')
    df = load_dataset(benchmark_file_name=benchmark_file_name)
    print(f'{df.shape[0]} geo queries loaded. evaluating...')
    evaluate_queries(df)
    print('Evaluate queries finished')
