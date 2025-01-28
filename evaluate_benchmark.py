import sys
import pandas as pd
from models.geo_agent import GeoAgent

def evaluate_queries(df):
    agent = GeoAgent()
    def evaluate_query(row):
        query = row['query']
        input = f'return only the sql statement for the following query: {query}'
        return agent.process_input(input)
    df['sql'] = df.apply(evaluate_query, axis=1)
    return df

def load_dataset(benchmark_file_name):
    try:
        df = pd.read_csv(benchmark_file_name)
        return df.dropna(subset=['query'])
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
    df = evaluate_queries(df.loc[:5])
    print('Evaluate queries finished')
    output_file = benchmark_file_name.replace('.csv', '_sql.csv')
    print(f'Evaluate queries finished, save results to {output_file}')
    df.to_csv(output_file)

