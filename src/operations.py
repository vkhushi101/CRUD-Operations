from functools import wraps

from flask import jsonify, request
from src.operationsDao import DataAccessObject


class Endpoints:
    """
    Wraps each endpoint request with an isolated database connection to better handle errors and improving resource efficiency.
    Ex. for better error handling: If a DB server becomes unavailable/ connection times out, failure will be isolated to the specific request.
    """

    def __init__(self, app):
        self.app = app
        self.dao = DataAccessObject()
        self.register_routes()

    @staticmethod
    def with_connection(func):
        """
        Wrapper establishes a database connection before request processing and surrenders the connection after processing completed.
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.dao.get_connection()
            try:
                result = func(self, *args, **kwargs)
            finally:
                self.dao.close()
            return result

        return wrapper

    # Helper methods

    def all_required_fields(self, operations, request_fields):
        """
        Checks request body fields for /set and /delete to validate that fields are of a compatible type.
        """
        print(
            f"Validating all required request fields {operations} are non-null strings."
        )
        fields = dict()
        for required_operation in operations:
            found_operation = request_fields.get(required_operation)

            # Check if the field is missing, empty, or not of string type
            if (
                not found_operation
                or not isinstance(found_operation, str)
                or found_operation.strip() == ""
            ):
                raise ValueError(
                    f"{required_operation} is a required non-empty string field in request."
                )

            fields[required_operation] = found_operation

        return fields

    def bad_request(self, error):
        """
        Error handler for 400 Bad Request
        """
        return jsonify({"message": "Bad Request", "error": str(error)}), 400

    def not_found(self, error):
        """
        Error handler for 404 Not Found
        """
        return jsonify({"message": "Key Not Found in Table", "error": str(error)}), 404

    def internal_error(self, error):
        """
        Error handler for 500 Internal Server Error
        """
        return jsonify({"message": "Internal Server Error", "error": str(error)}), 500

    def register_routes(self):
        """
        Register the routes to the app
        """
        self.app.route("/set", methods=["PUT"])(self.set_key_value_in_namespace)
        self.app.route("/get", methods=["GET"])(self.get_value_in_namespace)
        self.app.route("/delete", methods=["DELETE"])(
            self.delete_key_value_from_namespace
        )
        self.app.route("/count", methods=["GET"])(self.count_value_in_namespace)
        self.app.route("/countGlobal", methods=["GET"])(self.count_global_value)

    # Business logic

    @with_connection
    def set_key_value_in_namespace(self):
        """
        Sets the key-value pair in a namespace in the table. If the key already exists in the namespace, updates the associated value.

        Returns:
            500 Internal Error: Error performing the CRUD operations from request.
            400 Bad Request:    Cannot identify a namespace, key, or value as * string * from the request. Optional to remove specification to str type, this is for a more rigid type expectation.
            200 Success:        Success message indicating correctly sets the value.
        """

        try:
            data = request.get_json()
            namespace: str = data.get("namespace")
            key: str = data.get("key")
            value: str = data.get("value")

            fields_data = self.all_required_fields(["namespace", "key", "value"], data)
            namespace, key, value = (
                fields_data["namespace"],
                fields_data["key"],
                fields_data["value"],
            )
        except Exception as e:
            return self.bad_request(e)

        print(f"Attempting to set key {key} to value {value} in namespace {namespace}")

        try:
            self.dao.set(namespace, key, value)
            return jsonify({"message": "Success", "data": value}), 200
        except Exception as e:
            return self.internal_error(e)

    @with_connection
    def get_value_in_namespace(self):
        """
        Gets the value from an entry that is expected to exist in the table.

        Returns:
            500 Internal Error: Error performing the CRUD operations from request.
            404 Not Found:      If key is not found in namespace.
            400 Bad Request:    Cannot identify a namespace, key, or value as * string * from the request. Optional to remove specification to str type, this is for a more rigid type expectation.
            200 Success:        Returns the correct value.
        """

        try:
            namespace: str = request.args.get("namespace")
            key: str = request.args.get("key")
        except Exception as e:
            return self.bad_request(e)

        print(f"Attempting to get value for key {key} in namespace {namespace}")

        try:
            value: str = self.dao.get(namespace, key)
            if value:
                return jsonify({"data": value}), 200
            return self.not_found(f"No key {key} found in namespace {namespace}")
        except Exception as e:
            return self.internal_error(e)

    @with_connection
    def delete_key_value_from_namespace(self):
        """
        Deletes the key-value pair from the given namespace where it is expected to exist in the table.

        Returns:
            500 Internal Error: Error performing the CRUD operations from request.
            404 Not Found:      If key is not found in namespace.
            400 Bad Request:    Cannot identify a namespace, key, or value as * string * from the request. Optional to remove specification to str type, this is for a more rigid type expectation.
            200 Success:        Returns a SUCCESS message.
        """

        try:
            data = request.get_json()
            namespace: str = data.get("namespace")
            key: str = data.get("key")

            fields_data = self.all_required_fields(["namespace", "key"], data)
            namespace, key = fields_data["namespace"], fields_data["key"]
        except Exception as e:
            return self.bad_request(e)

        print(f"Attempting to delete entry with key {key} in namespace {namespace}")

        try:
            value: str = self.dao.delete(namespace, key)
            if value:
                return jsonify({"message": "Success"}), 200
            return self.not_found(f"No key {key} found in namespace {namespace}")
        except Exception as e:
            return self.internal_error(e)

    @with_connection
    def count_value_in_namespace(self):
        """
        Counts the number of instances of given value in specified namespace.

        Returns:
            500 Internal Error: Error performing the CRUD operations from request.
            400 Bad Request:    Cannot identify a namespace, key, or value as * string * from the request. Optional to remove specification to str type, this is for a more rigid type expectation.
            200 Success:        Returns the count value.
        """

        try:
            namespace: str = request.args.get("namespace")
            value: str = request.args.get("value")
        except Exception as e:
            return self.bad_request(e)

        print(
            f"Attempting to count entries with value {value} in namespace {namespace}"
        )

        try:
            count: int = self.dao.count(namespace, value)
            return jsonify({"count": count}), 200
        except Exception as e:
            return self.internal_error(e)

    @with_connection
    def count_global_value(self):
        """
        Counts the number of instances of given value across all namespaces.

        Returns:
            500 Internal Error: Error performing the CRUD operations from request.
            400 Bad Request:    Cannot identify a namespace, key, or value as * string * from the request. Optional to remove specification to str type, this is for a more rigid type expectation.
            200 Success:        Returns the count value.
        """

        try:
            value: str = request.args.get("value")
        except Exception as e:
            return self.bad_request(e)

        print(f"Attempting to count entries with value {value} across namespaces")

        try:
            count: int = self.dao.count_global(value)
            return jsonify({"count": count}), 200
        except Exception as e:
            return self.internal_error(e)
