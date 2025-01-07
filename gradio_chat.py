import gradio as gr
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
        return m._repr_html_()

    with gr.Blocks() as iface:
        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                chatbot = gr.Chatbot(height=570)

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

    iface.launch(server_name='0.0.0.0', server_port=7866)


if __name__ == "__main__":
    chat_ui()
