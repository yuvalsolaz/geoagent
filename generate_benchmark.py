import pandas as pd

from models.generate_query_agent import GenerateQueryAgent
from utils.postgres_handler import PostgresHandler
from config import SCHEMA_NAME, TABLE_NAME

def main_chat():
    agent = GenerateQueryAgent()

    print("input location coordinates for generating specific location query (or 'quit' to exit):")
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
            if user_input.lower() == 'quit':
                break

            result = agent.process_input(user_input)
            print("Answer:", result)
            print("\nInput another location (or 'quit' to exit):")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("\nPlease try again:")
            continue


def load_Locations(schema, table):
    # load location table
    try:
        with PostgresHandler() as db:
            select_all_sql = f'''select 
                                    ce.*,
                                    ST_AsText(ce.geog) AS geometry_wkt from {schema}.{table} ce '''
            result = db.execute_query(select_all_sql)
            if not result:
                print(f'Error loading locations data from {schema}.{table}')
                return None
        df = pd.DataFrame(result["data"])
        return df
    except Exception as ex:
        print(f'Error loading locations data from {schema}.{table}: {ex}')
        return None


from shapely.geometry import shape
from shapely import wkt

def generate(df):

    if df.empty:
        return
    agent = GenerateQueryAgent()
    for rec in df.iterrows():
        c = shape(wkt.loads(rec[1]['geometry_wkt'])).centroid
        date = rec[1]['startdate']
        input = f'{c.x} {c.y} {date.month}:{date.year}'
        agent.process_input(input)

if __name__ == "__main__":
    # main_chat()
    print(f'loading locations from {SCHEMA_NAME}.{TABLE_NAME}...')
    df = load_Locations(schema=SCHEMA_NAME, table=TABLE_NAME)
    if df.empty:
        exit(1)
    print(f'{df.shape[0]} locations loaded. generating geo queries...')
    generate(df)
    output_file = f'{TABLE_NAME}_queries.csv'
    print(f'Generating queries finished, save results to {output_file}')
    df.to_csv(output_file)




