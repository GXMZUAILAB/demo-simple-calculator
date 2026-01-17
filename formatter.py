from typing import Union

_UNIT_LABELS = {
    "h": "小时",
    "m": "分钟",
}

_ERROR_MESSAGES = {
    "div0": "Error: Div 0",
    "sort": "Error: Sort",
    "time": "Error: Time",
    "generic": "Error",
}


def _format_number_no_trailing_zero(value: Union[int, float]) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def format_result(result: Union[int, float]) -> tuple[str, str]:
    if isinstance(result, float):
        rounded = round(result, 10)
        if rounded.is_integer():
            return str(int(rounded)), ""
        return str(rounded), ""

    return str(result), ""


def format_sorted_numbers(numbers: list[Union[int, float]]) -> tuple[str, str]:
    parts = [_format_number_no_trailing_zero(n) for n in numbers]
    return ",".join(parts), "Sorted"


def format_time_conversion(
    converted_value: float,
    converted_unit: str,
    original_value: float,
    original_unit: str,
) -> tuple[str, str]:
    converted_label = _UNIT_LABELS[converted_unit]
    original_label = _UNIT_LABELS[original_unit]

    converted_text = f"{_format_number_no_trailing_zero(converted_value)}{converted_label}"
    original_text = f"{original_value}{original_label}"
    return converted_text, original_text


def format_error(kind: str) -> tuple[str, str]:
    return _ERROR_MESSAGES.get(kind, _ERROR_MESSAGES["generic"]), ""
