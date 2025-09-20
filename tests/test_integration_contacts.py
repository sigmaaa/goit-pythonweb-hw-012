from datetime import date


def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts/",
        json={
            "name": "John",
            "surname": "Doe",
            "email": "john.doe@example.com",
            "phone": "+380123456789",
            "birthday": str(date(1990, 1, 1)),
            "extra_info": "Friend from school",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "John"
    assert data["surname"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert "id" in data


def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "John"
    assert data["surname"] == "Doe"


def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    response = client.get(
        "/api/contacts/", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "name" in data[0]
    assert "surname" in data[0]


def test_update_contact(client, get_token):
    response = client.put(
        "/api/contacts/1",
        json={
            "name": "Johnny",
            "surname": "Doe",
            "email": "johnny.doe@example.com",
            "phone": "+380987654321",
            "birthday": str(date(1991, 1, 1)),
            "extra_info": "Updated contact info",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Johnny"
    assert data["email"] == "johnny.doe@example.com"


def test_update_contact_not_found(client, get_token):
    response = client.put(
        "/api/contacts/999",
        json={
            "name": "Ghost",
            "surname": "User",
            "email": "ghost@example.com",
            "phone": "+380000000000",
            "birthday": str(date(2000, 1, 1)),
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] in ["John", "Johnny"]
    assert "id" in data


def test_repeat_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"
