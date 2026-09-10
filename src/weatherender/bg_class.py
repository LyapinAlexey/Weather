def determine_bg_class(condition_text: str) -> str:
    """Determine the appropriate CSS background class name based on the weather condition text.

    Returns one of 'sunny', 'rainy', 'cloudy', or 'thunder'.
    """
    text = condition_text.lower()
    if any(word in text for word in ["clear", "sunny"]):
        return "sunny"
    if "rain" in text:
        return "rainy"
    if "cloud" in text:
        return "cloudy"
    if "thunder" in text:
        return "thunder"
    return "sunny"
