from dataclasses import dataclass


@dataclass(frozen=True)
class SelectionResult:
    selected_row_index: int
    selected_column_index: int
    selected_symbol: str


class P300Decoder:
    def __init__(self, grid_symbols: list[list[str]]):
        if not grid_symbols or not grid_symbols[0]:
            raise ValueError("Grid symbols cannot be empty.")

        expected_row_length = len(grid_symbols[0])

        for row in grid_symbols:
            if len(row) != expected_row_length:
                raise ValueError("All grid rows must have the same length.")

        self.grid_symbols = grid_symbols
        self.row_scores = [0.0 for _ in range(len(grid_symbols))]
        self.column_scores = [0.0 for _ in range(expected_row_length)]

    def register_row_prediction(self, row_index: int, confidence: float = 1.0) -> None:
        self.row_scores[row_index] += confidence

    def register_column_prediction(
        self,
        column_index: int,
        confidence: float = 1.0,
    ) -> None:
        self.column_scores[column_index] += confidence

    def resolve_selection(self) -> SelectionResult:
        selected_row_index = max(
            range(len(self.row_scores)),
            key=self.row_scores.__getitem__,
        )
        selected_column_index = max(
            range(len(self.column_scores)),
            key=self.column_scores.__getitem__,
        )
        selected_symbol = self.grid_symbols[selected_row_index][selected_column_index]

        return SelectionResult(
            selected_row_index=selected_row_index,
            selected_column_index=selected_column_index,
            selected_symbol=selected_symbol,
        )

    def reset(self) -> None:
        self.row_scores = [0.0 for _ in range(len(self.grid_symbols))]
        self.column_scores = [0.0 for _ in range(len(self.grid_symbols[0]))]