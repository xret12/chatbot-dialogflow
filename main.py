from fastapi import FastAPI, Request
from dotenv import load_dotenv
from chatbot_operations import ChatBotOperations

# Access environment variables
load_dotenv()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    chatbot = ChatBotOperations(payload=payload)
    print('MY INTENT:', chatbot.intent)
    print('SESSION ID:', chatbot.session_id)

    intent_handler_dict = {
        'order-remove (context: ongoing-order)': chatbot.remove_from_order,
        'order-complete (context: ongoing-order)': chatbot.complete_order,
        'track-order (context: ongoing-tracking)': chatbot.track_order,
        'order-add (context: ongoing-order)': chatbot.add_to_order
    }

    return intent_handler_dict[chatbot.intent]()
