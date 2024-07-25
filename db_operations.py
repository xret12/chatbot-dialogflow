import mysql.connector


class DBOperations:
    def __init__(self, host, user, password, database):
        self.cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

    def save_to_db(self, order: dict):
        next_order_id = self.get_next_order_id()

        # Insert individual items along with quantity in orders table
        for food_item, quantity in order.items():
            rcode = self.insert_order_item(
                food_item,
                quantity,
                next_order_id
            )

            if rcode == -1:
                return -1

        # Now insert order tracking status
        self.insert_order_tracking(next_order_id, "in progress")
        return next_order_id

    def insert_order_tracking(self, order_id, status):
        cursor = self.cnx.cursor()

        # Inserting the record into the order_tracking table
        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s);"
        cursor.execute(insert_query, (order_id, status))

        # Committing the changes
        self.cnx.commit()

        # Closing the cursor
        cursor.close()

    def get_next_order_id(self):
        cursor = self.cnx.cursor()

        # Executing the SQL query to get the next available order_id
        query = "SELECT MAX(order_id) FROM orders;"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()[0]

        # Closing the cursor
        cursor.close()

        # Returning the next available order_id
        if result is None:
            return 1
        else:
            return result + 1

    def insert_order_item(self, food_item, quantity, order_id):
        try:
            cursor = self.cnx.cursor()

            # Calling the stored procedure
            cursor.callproc('insert_order_item',
                            (food_item, quantity, order_id))

            # Committing the changes
            self.cnx.commit()

            # Closing the cursor
            cursor.close()

            print("Order item inserted successfully!")

            return 1

        except mysql.connector.Error as err:
            print(f"Error inserting order item: {err}")

            # Rollback changes if necessary
            self.cnx.rollback()

            return -1

        except Exception as e:
            print(f"An error occurred: {e}")
            # Rollback changes if necessary
            self.cnx.rollback()

            return -1

    def get_order_status(self, order_id):
        """
        Retrieves the status of an order from the `order_tracking` table in the database.

        Parameters:
            order_id (int): The ID of the order.

        Returns:
            str or None: The status of the order if it exists, otherwise None.
        """
        cursor = self.cnx.cursor()

        # Executing the SQL query to fetch the order status
        query = f"SELECT status FROM order_tracking WHERE order_id = {order_id};"
        cursor.execute(query)

        result = cursor.fetchone()

        # Closing the cursor
        cursor.close()

        # Returning the order status
        if result:
            return result[0]
        else:
            return None

    def get_total_order_price(self, order_id):
        cursor = self.cnx.cursor()

        # Executing the SQL query to get the total order price
        query = f"SELECT get_total_order_price({order_id});"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()[0]

        # Closing the cursor
        cursor.close()

        return result
