import json


def userDict(item) -> dict:
    return {
        "id": str(item['_id']),
        "name": item["name"],
        "contact_number": item["contact_number"],
        "email": item["email"],
        "role": item['role'],
        "is_approved": item['is_approved'],
        "approved_by": item['approved_by']
    }


def userList(entity) -> list:
    return [userDict(a) for a in entity]


def serializeDict(a) -> json:
    return {**{i: str(a[i]) for i in a if i == '_id'}, **{i: a[i] for i in a if i != '_id'}}


def serializeList(entity) -> list:
    return [serializeDict(a) for a in entity]
