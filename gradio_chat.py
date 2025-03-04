import gradio as gr
import sys
from models.geo_agent import GeoAgent
from tools.visualize_on_map_tool import create_map
from utils.geo_state_manager import GeoStateManager

geo_state = GeoStateManager()

def chat_ui():
    agent = GeoAgent()

    def handle_query(query, history):
        history_prompt = " and ".join([query['content'] for query in history if query['role'] == 'user'])
        prompt = f'{history_prompt} {query}'
        results = agent.process_input(prompt)
        return results

    def visualize():
        m = create_map()
        map_html = m._repr_html_()
        map_html = map_html.replace("position:relative;width:100%;height:0;padding-bottom:60%;",
                                    "position:relative;width:100%;height:0;padding-bottom:100%;", 1)
        map_html = map_html.replace("height: 500.0px;",
                                    "height: 800.0px;",1)
        return map_html
    with gr.Blocks() as iface:
        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                chatbot = gr.Chatbot(height=800, type="messages")

                def handle_clear():
                    geo_state.reset()

                chatbot.clear(handle_clear)

                def handle_like(data: gr.LikeData):
                    if data.liked:
                        print("You upvoted this response: ", data.value)
                    else:
                        print("You downvoted this response: ", data.value)

                chatbot.like(handle_like, None, None)

                gr.ChatInterface(fn=handle_query,
                                 # description="roads within 5 km from Hamra street ",
                                 type="messages",
                                 theme="ocean",
                                 chatbot=chatbot)

            with gr.Column(scale=2, min_width=200):
                visualize_btn = gr.Button("Refresh")
                output = gr.HTML(label="Map Visualization")
                visualize_btn.click(fn=visualize, outputs=output, api_name="Map")

    if len(sys.argv) == 1:
        iface.launch(server_name='0.0.0.0', server_port=7867)
    else:
        iface.launch(share=True)


if __name__ == "__main__":
    chat_ui()
