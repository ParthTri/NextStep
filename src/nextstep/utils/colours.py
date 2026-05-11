import random
from typing import List


def generate_dynamic_neobrutal():
    """Generates random colors but keeps them highly saturated."""
    # We keep at least one channel at max (255) and one channel low (<100)
    # to ensure the color is 'loud' and not 'muddy'.
    channels = [255, random.randint(0, 255), random.randint(0, 100)]
    random.shuffle(channels)

    return channels


def format_channels(channels: List[int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*channels).upper()


def darker_variant(channels: List[int], factor: float = 0.6) -> List[int]:
    """
    Takes a list of RGB channels [R, G, B] and returns a darker
    variant by scaling each channel down.

    :param channels: List of 3 integers (0-255)
    :param factor: Multiplier (0.0 to 1.0). Lower = Darker.
    :return: List of 3 darkened integers
    """
    # We use max(0, ...) to ensure we don't hit negative numbers
    # and int() to keep the values compatible with hex conversion.
    return [max(0, int(c * factor)) for c in channels]
