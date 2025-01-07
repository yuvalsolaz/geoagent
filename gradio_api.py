import sys
from gradio_client import Client

if __name__ == '__main__':
    client = Client("http://localhost:7866/")
    if len(sys.argv) < 2:
        print(client.view_api())
        print()
        print(f'usage: python {sys.argv[0]} <query>')
        print(f'usage examples: clear , "roads within 4 km from the center of beirut city"')
        exit(1)

    input = sys.argv[1]
    if input in ["clear"]:
        print(f"handle {input}")
        res = client.predict(api_name=f"/handle_{input}")
        exit(2)

    res = client.predict(sys.argv[1], api_name="/chat")
    print(res)
