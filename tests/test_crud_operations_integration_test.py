from tests.conftest import client


def check_response(response, expected_status, expected_json=None):
    """
    Helper method to assert response status and optional JSON body
    """
    assert response.status_code == expected_status
    if expected_json:
        assert response.json == expected_json


def test_scenario_1(client):
    # Set key-value pairs
    response = client.put("/set", json={"namespace": "a", "key": "b", "value": "c"})
    check_response(response, 200, {"data": "c", "message": "Success"})

    response = client.put("/set", json={"namespace": "z", "key": "b", "value": "d"})
    check_response(response, 200, {"data": "d", "message": "Success"})

    # Get the values
    response = client.get("/get", query_string={"namespace": "a", "key": "b"})
    check_response(response, 200, {"data": "c"})

    response = client.get("/get", query_string={"namespace": "z", "key": "b"})
    check_response(response, 200, {"data": "d"})

    # Delete key and verify
    response = client.delete("/delete", json={"namespace": "a", "key": "b"})
    check_response(response, 200)

    response = client.get("/get", query_string={"namespace": "a", "key": "b"})
    check_response(
        response,
        404,
        {"error": "No key b found in namespace a", "message": "Key Not Found in Table"},
    )


def test_scenario_2(client):
    # Set key-value pairs
    response = client.put("/set", json={"namespace": "a", "key": "b", "value": "c"})
    check_response(response, 200)

    response = client.put("/set", json={"namespace": "z", "key": "b", "value": "c"})
    check_response(response, 200)

    response = client.put("/set", json={"namespace": "z", "key": "bb", "value": "c"})
    check_response(response, 200)

    # Count occurrences of a value within a namespace
    response = client.get("/count", query_string={"namespace": "a", "value": "c"})
    check_response(response, 200, {"count": 1})

    response = client.get("/count", query_string={"namespace": "z", "value": "c"})
    check_response(response, 200, {"count": 2})

    # Count value globally across namespaces
    response = client.get("/countGlobal", query_string={"value": "c"})
    check_response(response, 200, {"count": 3})


def test_scenario_3(client):
    # Set key-value pair
    response = client.put("/set", json={"namespace": "a", "key": "b", "value": "c"})
    check_response(response, 200, {"data": "c", "message": "Success"})

    # Overwrite the value
    response = client.put("/set", json={"namespace": "a", "key": "b", "value": "d"})
    check_response(response, 200)

    # Get the updated value
    response = client.get("/get", query_string={"namespace": "a", "key": "b"})
    check_response(response, 200, {"data": "d"})


def test_scenario_4(client):
    # Missing value parameter
    response = client.put("/set", json={"namespace": "a", "key": "b"})
    check_response(
        response,
        400,
        {
            "error": "value is a required non-empty string field in request.",
            "message": "Bad Request",
        },
    )

    # Invalid value type
    response = client.put("/set", json={"namespace": "a", "key": "b", "value": 12345})
    check_response(
        response,
        400,
        {
            "error": "value is a required non-empty string field in request.",
            "message": "Bad Request",
        },
    )

    # Testing idempotency with a get request where the key does not exist
    response = client.get("/get", query_string={"namespace": "a", "key": "b"})
    check_response(
        response,
        404,
        {"error": "No key b found in namespace a", "message": "Key Not Found in Table"},
    )

    # Trying to delete a non-existing key
    response = client.delete("/delete", json={"namespace": "a", "key": "b"})
    check_response(
        response,
        404,
        {"error": "No key b found in namespace a", "message": "Key Not Found in Table"},
    )


def test_scenario_5(client):
    # Set a value
    response = client.put("/set", json={"namespace": "a", "key": "b", "value": "c"})
    check_response(response, 200)

    # Delete the key
    response = client.delete("/delete", json={"namespace": "a", "key": "b"})
    check_response(response, 200)

    # Trying to delete a now non-existing key
    response = client.delete("/delete", json={"namespace": "a", "key": "b"})
    check_response(response, 404)

    # Get the value to verify deletion
    response = client.get("/get", query_string={"namespace": "a", "key": "b"})
    check_response(
        response,
        404,
        {"error": "No key b found in namespace a", "message": "Key Not Found in Table"},
    )
