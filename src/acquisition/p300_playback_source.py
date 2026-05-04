from dataclasses import dataclass
from pathlib import Path
import csv
from typing import Any


def build_flash_sequence_from_replay(
    replay_path: str | Path,
    flash_groups: list[tuple[str, int, Any]],
) -> list[tuple[str, int, Any]]:
    flash_group_lookup = {
        (group_type, group_index): group
        for group_type, group_index, group in flash_groups
    }

    path = Path(replay_path)

    with path.open("r", newline="", encoding="utf-8") as replay_file:
        reader = csv.DictReader(replay_file)
        replay_rows = sorted(reader, key=lambda row: int(row["trial_index"]))

    flash_sequence: list[tuple[str, int, Any]] = []

    for row in replay_rows:
        group_type = row["group_type"].strip()
        group_index = int(row["group_index"])
        key = (group_type, group_index)

        if key not in flash_group_lookup:
            raise ValueError(f"Replay references unknown flash group {key}")

        flash_sequence.append((group_type, group_index, flash_group_lookup[key]))

    return flash_sequence


@dataclass(frozen=True)
class ReplayPrediction:
    trial_index: int
    group_type: str
    group_index: int
    predicted_is_target_flash: bool
    confidence: float


class ReplaySignalSource:
    def __init__(self, replay_file_path: str | Path):
        self.replay_file_path = Path(replay_file_path)
        self.predictions = self._load_predictions()
        self.cursor = 0

    def _load_predictions(self) -> list[ReplayPrediction]:
        if not self.replay_file_path.exists():
            raise FileNotFoundError(
                f"Replay file not found: {self.replay_file_path}"
            )

        predictions: list[ReplayPrediction] = []

        with self.replay_file_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            fieldnames = set(reader.fieldnames or [])
            required_fields = {"trial_index", "group_type", "group_index"}
            missing_fields = required_fields - fieldnames

            if missing_fields:
                missing_list = ", ".join(sorted(missing_fields))
                raise ValueError(
                    f"Replay file is missing required fields: {missing_list}"
                )

            if "predicted_is_target_flash" in fieldnames:
                boolean_column = "predicted_is_target_flash"
            elif "is_target_flash" in fieldnames:
                boolean_column = "is_target_flash"
            else:
                raise ValueError(
                    "Replay file needs predicted_is_target_flash or is_target_flash"
                )

            for row in reader:
                confidence_text = row.get("confidence", "1.0").strip()

                predictions.append(
                    ReplayPrediction(
                        trial_index=int(row["trial_index"]),
                        group_type=row["group_type"].strip(),
                        group_index=int(row["group_index"]),
                        predicted_is_target_flash=self._parse_boolean(
                            row[boolean_column]
                        ),
                        confidence=float(confidence_text),
                    )
                )

        if not predictions:
            raise ValueError("Replay file is empty.")

        return predictions

    def predict_target_flash(
        self,
        group_type: str,
        group_index: int,
    ) -> tuple[bool, float]:
        if self.cursor >= len(self.predictions):
            raise IndexError(
                "ReplaySignalSource ran out of predictions before the flash loop ended."
            )

        prediction = self.predictions[self.cursor]
        self.cursor += 1

        if prediction.group_type != group_type:
            raise ValueError(
                f"Replay mismatch for flash {prediction.trial_index}: "
                f"expected group_type={prediction.group_type}, got {group_type}"
            )

        if prediction.group_index != group_index:
            raise ValueError(
                f"Replay mismatch for flash {prediction.trial_index}: "
                f"expected group_index={prediction.group_index}, got {group_index}"
            )

        return (
            prediction.predicted_is_target_flash,
            prediction.confidence,
        )

    def reset(self) -> None:
        self.cursor = 0

    @staticmethod
    def _parse_boolean(value: str) -> bool:
        normalized_value = value.strip().lower()

        if normalized_value in {"1", "true", "yes", "y"}:
            return True

        if normalized_value in {"0", "false", "no", "n"}:
            return False

        raise ValueError(f"Cannot parse boolean value: {value}")