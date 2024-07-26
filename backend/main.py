from fastapi import FastAPI, Request
from dotenv import load_dotenv
from chatbot_operations import ChatBotOperations

# Access environment variables
load_dotenv()


app = FastAPI()


@app.post("/")
async def handle_request(request: Request):
    """
    Handle a POST request to the root endpoint of the API.

    This function is an asynchronous handler for the POST request to the root endpoint of the API. It retrieves the JSON data from the request, creates a `ChatBotOperations` object with the payload, and prints the intent and session ID. 

    It then creates a dictionary `intent_handler_dict` that maps intent strings to corresponding methods of the `ChatBotOperations` object. The method corresponding to the intent in the `chatbot` object is called and the result is returned.

    Parameters:
    - `request` (Request): The incoming request object.

    Returns:
    - The result of calling the corresponding method in `ChatBotOperations` based on the intent.
    """
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Create a ChatBotOperations object with the payload
    chatbot = ChatBotOperations(payload=payload)

    # Print the intent and session ID
    print('MY INTENT:', chatbot.intent)
    print('SESSION ID:', chatbot.session_id)

    # Create a dictionary that maps intent strings to corresponding methods of the ChatBotOperations object
    # The method corresponding to the intent in the chatbot object is called and the result is returned
    intent_handler_dict = {
        'order-remove (context: ongoing-order)': chatbot.remove_from_order,
        'order-complete (context: ongoing-order)': chatbot.complete_order,
        'track-order (context: ongoing-tracking)': chatbot.track_order,
        'order-add (context: ongoing-order)': chatbot.add_to_order
    }

    # Call the corresponding method in ChatBotOperations based on the intent and return the result
    return intent_handler_dict[chatbot.intent]()


