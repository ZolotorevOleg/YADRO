from xml.etree import ElementTree as ET


def parse_cbr_xml(root: ET.Element) -> dict:
    result = {}

    for valute in root.findall("Valute"):
        char_code = valute.findtext("CharCode")
        value_text = valute.findtext("Value")

        if not char_code or not value_text:
            continue

        value = float(value_text.replace(",", "."))
        result[char_code] = round(value, 4)

    return result