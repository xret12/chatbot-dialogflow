
from db_operations import DBOperations
import utils
import os

# create a global dictionary
INPROGRESS_ORDERS = {}

class ChatBotOperations:
    def __init__(self, payload: dict):
        self.intent = payload['queryResult']['intent']['displayName']
        self.parameters = payload['queryResult']['parameters']
        self.output_contexts = payload['queryResult']['outputContexts']
        self.session_id = utils.extract_session_id(
            self.output_contexts[0]["name"])

        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_name = os.getenv('DB_NAME')
        self.db_connection = DBOperations(
            host=db_host, user=db_user, password=db_password, database=db_name)
        

    def track_order(self):
        order_id = int(self.parameters['order_id'])
        order_status = self.db_connection.get_order_status(order_id)
        if order_status:
            fulfillment_text = f"The order status for order ID # {order_id} is: {order_status.title()}"
        else:
            fulfillment_text = f"No order found with order ID: # {order_id}"

        return {"fulfillmentMessages": [
            {
                "text": {
                    "text": [fulfillment_text]
                }
            }
        ]}


    def complete_order(self):
        if self.session_id not in INPROGRESS_ORDERS:
            fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        else:
            order = INPROGRESS_ORDERS[self.session_id]
            order_id = self.db_connection.save_to_db(order)
            if order_id == -1:
                fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                    "Please place a new order again"
            else:
                order_total = self.db_connection.get_total_order_price(order_id) 

                fulfillment_text = f"Awesome. We have placed your order. " \
                    f"Here is your order id # {order_id}. " \
                    f"Your order total is {order_total} which you can pay at the time of delivery!"

            del INPROGRESS_ORDERS[self.session_id]
            print(INPROGRESS_ORDERS)
        return {"fulfillmentMessages": [
            {
                "text": {
                    "text": [fulfillment_text]
                }
            }
        ]}

    def add_to_order(self):
        food_items = self.parameters["food_item"]
        quantities = self.parameters["number"]

        if len(food_items) != len(quantities):
            fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
        else:
            new_food_dict = dict(zip(food_items, quantities))

            if self.session_id in INPROGRESS_ORDERS:
                current_food_dict = INPROGRESS_ORDERS[self.session_id]
                current_food_dict.update(new_food_dict)
                INPROGRESS_ORDERS[self.session_id] = current_food_dict
            else:
                INPROGRESS_ORDERS[self.session_id] = new_food_dict

            order_str = utils.get_str_from_food_dict(
                INPROGRESS_ORDERS[self.session_id])
            fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"
            print(INPROGRESS_ORDERS)
        return {"fulfillmentMessages": [
            {
                "text": {
                    "text": [fulfillment_text]
                }
            }
        ]}

    def remove_from_order(self):
        if self.session_id not in INPROGRESS_ORDERS:
            return {"fulfillmentMessages": [
                    {
                        "text": {
                            "text": ["I'm having a trouble finding your order. Sorry! Can you place a new order please?"]
                        }
                    }
                    ]}

        food_items = self.parameters["food_item"]
        current_order = INPROGRESS_ORDERS[self.session_id]

        removed_items = []
        no_such_items = []

        for item in food_items:
            if item not in current_order:
                no_such_items.append(item)
            else:
                removed_items.append(item)
                del current_order[item]

        if len(removed_items) > 0:
            fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

        if len(no_such_items) > 0:
            fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'

        if len(current_order.keys()) == 0:
            fulfillment_text += " Your order is empty!"
        else:
            order_str = utils.get_str_from_food_dict(current_order)
            fulfillment_text += f" Here is what is left in your order: {order_str}"
        print(INPROGRESS_ORDERS)
        return {"fulfillmentMessages": [
            {
                "text": {
                    "text": [fulfillment_text]
                }
            }
        ]}
