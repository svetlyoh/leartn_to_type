from urllib.parse import parse_qs


def parse_urlencoded_pin(body: bytes) -> str:
    values = parse_qs(body.decode("utf-8", errors="strict"), keep_blank_values=True)
    return values.get("pin", [""])[0].strip()
