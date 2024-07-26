
from db_operations import DBOperations
import utils
import os

# create a global dictionary
INPROGRESS_ORDERS = {}


class ChatBotOperations:
    def __init__(self, payload: dict):
        """
        Initializes a new instance of the ChatBotOperations class.

        Args:
            payload (dict): A dictionary containing the payload data.

        Initializes the following instance variables:
            - self.intent (str): The display name of the intent.
            - self.parameters (dict): The parameters of the query result.
            - self.output_contexts (list): The output contexts of the query result.
            - self.session_id (str): The session ID extracted from the output contexts.
            - self.db_connection (DBOperations): An instance of the DBOperations class for database operations.

        Retrieves the following environment variables:
            - DB_HOST (str): The host of the database.
            - DB_USER (str): The user of the database.
            - DB_PASSWORD (str): The password of the database.
            - DB_NAME (str): The name of the database.

        Raises:
            KeyError: If any of the required keys are missing in the payload dictionary.
        """
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
        """
        Retrieves the status of an order from the `order_tracking` table in the database.

        Returns:
            dict: A dictionary containing the fulfillment messages for the order status.
                  The fulfillment messages include the order status and the order ID.
        """
        order_id = int(self.parameters['order_id'])
        order_status = self.db_connection.get_order_status(order_id)
        if order_status:
            fulfillment_text = f"The order status for order ID # {order_id} is: {order_status.title()}"
        else:
            fulfillment_text = f"No order found with order ID: # {order_id}"

        return {
            "fulfillmentText": fulfillment_text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [fulfillment_text]
                    }
                }
            ]}

    def complete_order(self):
        """
        Completes the order for the current session.

        Returns:
            dict: A dictionary containing the fulfillment messages for the order completion.
                The fulfillment messages include the order status, order ID, and order total.
        """
        if self.session_id not in INPROGRESS_ORDERS:
            fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        else:
            order = INPROGRESS_ORDERS[self.session_id]
            order_id = self.db_connection.save_to_db(order)
            if order_id == -1:
                fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                    "Please place a new order again"
            else:
                order_total = self.db_connection.get_total_order_price(
                    order_id)

                fulfillment_text = f"Awesome. We have placed your order. " \
                    f"Here is your order id # {order_id}. " \
                    f"Your order total is {order_total} which you can pay at the time of delivery!"

            del INPROGRESS_ORDERS[self.session_id]
            print(INPROGRESS_ORDERS)
        return {
            "fulfillmentText": fulfillment_text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [fulfillment_text]
                    }
                }
            ]}

    def add_to_order(self):
        """
        Adds food items to the ongoing order for the current session.

        This method takes in the food items and quantities from the parameters
        and checks if they are of the same length. If they are not, it sets
        the fulfillment_text to indicate that the items and quantities need to
        be specified clearly.

        If the items and quantities are of the same length, it creates a new
        dictionary from the zipped items and quantities. Then, it checks if
        there is an ongoing order for the current session. If there is, it updates
        the current order with the new items. If there is no ongoing order, it
        creates a new order with the new items.

        After updating the order, it retrieves the string representation of the
        order and sets the fulfillment_text to indicate the items that have been
        added to the order so far.

        Finally, it prints the ongoing orders and returns a dictionary with the
        fulfillment_text as the response.

        Returns:
            dict: A dictionary with the fulfillment_text as the response.
        """
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
        return {
            "fulfillmentText": fulfillment_text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [fulfillment_text]
                    }
                }
            ]}

    def remove_from_order(self):
        """
        Removes items from the current order based on the provided parameters.

        Returns:
            dict: A dictionary containing the fulfillment messages. The fulfillment messages include information about the removed items and the remaining items in the order.
        """
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
            fulfillment_text = f'Removed {", ".join(removed_items)} from your order!'

        if len(no_such_items) > 0:
            fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'

        if len(current_order.keys()) == 0:
            fulfillment_text += " Your order is empty!"
        else:
            order_str = utils.get_str_from_food_dict(current_order)
            fulfillment_text += f" Here is what is left in your order: {order_str}"
        print(INPROGRESS_ORDERS)
        return {
            "fulfillmentText": fulfillment_text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [fulfillment_text]
                    }
                }
            ]}
