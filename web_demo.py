from transformers import AutoModel, AutoTokenizer
import gradio as gr

tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
model = model.half().cuda()
model = model.eval()

MAX_TURNS = 20
MAX_BOXES = MAX_TURNS * 2


def predict(input, history=[]):
    response, history = model.chat(tokenizer, input, history)
    updates = []
    for query, response in history:
        updates.append(gr.update(visible=True, value=query))
        updates.append(gr.update(visible=True, value=response))
    if len(updates) < MAX_BOXES:
        updates = updates + [gr.Textbox.update(visible=False)] * (MAX_BOXES - len(updates))
    return [history] + updates


with gr.Blocks() as demo:
    state = gr.State([])
    text_boxes = []
    for i in range(MAX_BOXES):
        if i % 2 == 0:
            label = "提问："
        else:
            label = "回复："
        text_boxes.append(gr.Textbox(visible=False, label=label))

    with gr.Row():
        with gr.Column(scale=4):
            txt = gr.Textbox(show_label=False, placeholder="Enter text and press enter").style(container=False)
        with gr.Column(scale=1):
            button = gr.Button("Generate")
    button.click(predict, [txt, state], [state] + text_boxes)
demo.queue().launch(share=True)
