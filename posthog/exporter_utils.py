from django.conf import settings


# TODO: Obviously this needs to be some sort of actual security like a JWT
def generate_exporter_token(type: str, id: str):
    return f"exp-{type}-{id}"


def validate_exporter_token(token: str):
    parts = token.split("-")

    if len(parts) != 3 or parts[0] != "exp":
        return None

    return {"type": parts[1], "id": parts[2]}
