import random

from bs4 import BeautifulSoup


class MarkovCadence:
    """
    Markov Chain Behavioral Cadence Simulator.
    Models human browsing habits:
    - Initial page scanning
    - Content reading proportional to DOM complexity and text length (Pareto / Log-normal distribution)
    - Natural hesitation / micro-distraction
    """

    STATES = ["SCAN_HEADER", "READ_CONTENT", "HESITATE", "PREPARE_NEXT"]

    TRANSITIONS = {
        "SCAN_HEADER": [("READ_CONTENT", 0.7), ("HESITATE", 0.2), ("PREPARE_NEXT", 0.1)],
        "READ_CONTENT": [("READ_CONTENT", 0.4), ("HESITATE", 0.4), ("PREPARE_NEXT", 0.2)],
        "HESITATE": [("READ_CONTENT", 0.6), ("SCAN_HEADER", 0.2), ("PREPARE_NEXT", 0.2)],
        "PREPARE_NEXT": [("READ_CONTENT", 0.3), ("HESITATE", 0.2), ("DONE", 0.5)],
    }

    @staticmethod
    def calculate_reading_dwell_time(
        html_or_soup: str | BeautifulSoup,
        min_seconds: float = 0.8,
        max_seconds: float = 4.5,
    ) -> float:
        """
        Calculates a realistic human dwell time based on text volume and DOM complexity,
        bounded between min_seconds and max_seconds using a Pareto distribution.
        """
        if isinstance(html_or_soup, str):
            text_length = len(html_or_soup) // 10
        else:
            text = html_or_soup.get_text()
            text_length = len(text.split())

        estimated_reading_secs = min(max_seconds, max(min_seconds, (text_length / 250.0) * 60.0 * 0.1))
        pareto_jitter = random.paretovariate(alpha=2.5) * 0.4
        dwell_time = estimated_reading_secs + pareto_jitter

        return min(max_seconds, max(min_seconds, dwell_time))

    @classmethod
    def generate_behavioral_sequence(cls, max_steps: int = 4) -> list[tuple[str, float]]:
        """
        Generates a sequence of (state_name, duration_seconds) using Markov chain state transitions.
        """
        current_state = "SCAN_HEADER"
        sequence = []

        for _ in range(max_steps):
            if current_state == "DONE":
                break

            if current_state == "SCAN_HEADER":
                duration = random.uniform(0.3, 0.9)
            elif current_state == "READ_CONTENT":
                duration = random.uniform(0.8, 2.2)
            elif current_state == "HESITATE":
                duration = random.uniform(0.2, 0.7)
            else:
                duration = random.uniform(0.2, 0.5)

            sequence.append((current_state, duration))

            options = cls.TRANSITIONS.get(current_state, [("DONE", 1.0)])
            choices, weights = zip(*options)
            current_state = random.choices(choices, weights=weights)[0]

        return sequence
