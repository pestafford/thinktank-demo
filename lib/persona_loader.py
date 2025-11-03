"""
ThinkTank Demo - Persona Loader
Load agent personas from JSON files
"""

import json
import os


def load_personas(personas_file="personas/personas.json"):
    """
    Load agent personas from JSON file.

    Args:
        personas_file: Path to personas JSON file

    Returns:
        list: List of persona dictionaries
    """
    if not os.path.exists(personas_file):
        raise FileNotFoundError(
            f"Personas file not found: {personas_file}\n"
            "Please ensure personas.json exists in the personas/ directory."
        )

    with open(personas_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both formats: array or object with "personas" key
    if isinstance(data, list):
        personas = data
    elif isinstance(data, dict) and "personas" in data:
        personas = data["personas"]
    else:
        raise ValueError(f"Invalid personas file format: {personas_file}")

    return personas


def load_foreperson(foreperson_file="personas/foreperson.json"):
    """
    Load foreperson persona from JSON file.

    Args:
        foreperson_file: Path to foreperson JSON file

    Returns:
        dict: Foreperson persona dictionary
    """
    if not os.path.exists(foreperson_file):
        raise FileNotFoundError(
            f"Foreperson file not found: {foreperson_file}\n"
            "Please ensure foreperson.json exists in the personas/ directory."
        )

    with open(foreperson_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both formats
    if isinstance(data, dict) and "personas" in data:
        # Take first persona if array
        return data["personas"][0] if isinstance(data["personas"], list) else data["personas"]
    elif isinstance(data, list):
        return data[0]
    else:
        return data
