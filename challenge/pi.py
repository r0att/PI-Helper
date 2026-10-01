from pathlib import Path


PI_FILE = Path(__file__).resolve().parent.parent / "data" / "pi.txt"

def get_pi_digits():
    return PI_FILE.read_text().strip()

def get_pi_range(start, end):
    digits = get_pi_digits()

    if end is None:
        return digits[start - 1:]

    return digits[start - 1:end]