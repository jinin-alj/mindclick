class SignalSource:
    def predict_target_flash(self, group_type: str, group_index: int) -> tuple[bool, float]:
        raise NotImplementedError


class IdealSignalSource(SignalSource):
    def __init__(self, target_row_index: int, target_column_index: int):
        self.target_row_index = target_row_index
        self.target_column_index = target_column_index

    def predict_target_flash(self, group_type: str, group_index: int) -> tuple[bool, float]:
        if group_type == "row":
            is_target_flash = group_index == self.target_row_index
        elif group_type == "column":
            is_target_flash = group_index == self.target_column_index
        else:
            raise ValueError(f"Unsupported group type: {group_type}")

        confidence = 1.0 if is_target_flash else 0.0
        return is_target_flash, confidence