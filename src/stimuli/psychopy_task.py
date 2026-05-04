from psychopy import visual, core, event
import csv
import random
from pathlib import Path
from src.modeling.p300_decoder import P300Decoder


WindowSize = (900, 700)
BackgroundColor = "black"
DefaultTextColor = "white"
HighlightColor = "red"

FlashDurationSeconds = 0.12
InterStimulusIntervalSeconds = 0.12
SelectionRepetitions = 4

GridRows = 6
GridColumns = 6

GridSymbols = [
    ["A", "B", "C", "D", "E", "F"],
    ["G", "H", "I", "J", "K", "L"],
    ["M", "N", "O", "P", "Q", "R"],
    ["S", "T", "U", "V", "W", "X"],
    ["Y", "Z", "_", "DEL", "1", "2"],
    ["3", "4", "5", "6", "7", "8"],
]

XPositions = [-0.8, -0.48, -0.16, 0.16, 0.48, 0.8]
YPositions = [0.6, 0.36, 0.12, -0.12, -0.36, -0.6]

ProjectRoot = Path(__file__).resolve().parents[2]
LogsDirectory = ProjectRoot / "data" / "logs"
LogsDirectory.mkdir(parents=True, exist_ok=True)


def create_window():
    return visual.Window(
        size=WindowSize,
        color=BackgroundColor,
        units="norm",
        checkTiming=False,
    )


def create_instruction_text(window, target_symbol):
    return visual.TextStim(
        window,
        text=f"focus on {target_symbol}. press escape to quit.",
        pos=(0, 0.85),
        color=DefaultTextColor,
        height=0.04,
    )


def create_status_text(window):
    return visual.TextStim(
        window,
        text="",
        pos=(0, -0.88),
        color=DefaultTextColor,
        height=0.05,
    )


def create_grid(window):
    grid = []

    for row_index in range(GridRows):
        current_row = []

        for column_index in range(GridColumns):
            symbol = GridSymbols[row_index][column_index]
            text_stimulus = visual.TextStim(
                window,
                text=symbol,
                pos=(XPositions[column_index], YPositions[row_index]),
                color=DefaultTextColor,
                height=0.08,
            )
            current_row.append(text_stimulus)

        grid.append(current_row)

    return grid


def extract_row_groups(grid):
    return grid


def extract_column_groups(grid):
    column_groups = []

    for column_index in range(GridColumns):
        column = [grid[row_index][column_index] for row_index in range(GridRows)]
        column_groups.append(column)

    return column_groups


def draw_grid(grid):
    for row in grid:
        for stimulus in row:
            stimulus.draw()


def set_group_color(group, color):
    for stimulus in group:
        stimulus.color = color


def reset_group_color(group):
    set_group_color(group, DefaultTextColor)


def build_flash_groups(row_groups, column_groups):
    flash_groups = []

    for index in range(len(row_groups)):
        flash_groups.append(("row", index, row_groups[index]))

    for index in range(len(column_groups)):
        flash_groups.append(("column", index, column_groups[index]))

    return flash_groups


def build_flash_sequence(flash_groups, repetitions):
    flash_sequence = []

    for _ in range(repetitions):
        repeated_groups = flash_groups.copy()
        random.shuffle(repeated_groups)
        flash_sequence.extend(repeated_groups)

    return flash_sequence


def find_target_position(grid, target_symbol):
    for row_index, row in enumerate(grid):
        for column_index, stimulus in enumerate(row):
            if stimulus.text == target_symbol:
                return row_index, column_index

    raise ValueError(f"Target symbol {target_symbol} was not found in the grid.")


def write_log_row(csv_writer, timestamp, trial_index, group_type, group_index, is_target_flash):
    csv_writer.writerow(
        [
            timestamp,
            trial_index,
            group_type,
            group_index,
            int(is_target_flash),
        ]
    )


def run_selection_cycle(window, grid, flash_groups, target_symbol, run_index, status_text):
    decoder = P300Decoder(GridSymbols)
    log_file_path = LogsDirectory / f"session_{run_index:03d}_{target_symbol}.csv"

    row_scores = [0] * GridRows
    column_scores = [0] * GridColumns

    target_row_index, target_column_index = find_target_position(grid, target_symbol)
    flash_sequence = build_flash_sequence(flash_groups, SelectionRepetitions)

    clock = core.Clock()

    with log_file_path.open("w", newline="", encoding="utf-8") as log_file:
        csv_writer = csv.writer(log_file)
        csv_writer.writerow(
            [
                "timestamp",
                "trial_index",
                "group_type",
                "group_index",
                "is_target_flash",
            ]
        )

        for trial_index, flash_group in enumerate(flash_sequence):
            if "escape" in event.getKeys():
                raise KeyboardInterrupt

            group_type, group_index, group = flash_group

            is_target_flash = (
                (group_type == "row" and group_index == target_row_index)
                or (group_type == "column" and group_index == target_column_index)
            )

            predicted_is_target_flash = is_target_flash

            if predicted_is_target_flash:
                if group_type == "row":
                    decoder.register_row_prediction(group_index)
                else:
                    decoder.register_column_prediction(group_index)

            set_group_color(group, HighlightColor)

            status_text.text = f"typing target {target_symbol}"
            draw_grid(grid)
            status_text.draw()
            window.flip()

            timestamp = clock.getTime()
            write_log_row(
                csv_writer=csv_writer,
                timestamp=timestamp,
                trial_index=trial_index,
                group_type=group_type,
                group_index=group_index,
                is_target_flash=predicted_is_target_flash,
            )

            print(
                f"trial={trial_index} type={group_type} index={group_index} target={predicted_is_target_flash}"
            )

            core.wait(FlashDurationSeconds)

            reset_group_color(group)
            draw_grid(grid)
            status_text.draw()
            window.flip()

            core.wait(InterStimulusIntervalSeconds)

    selection_result = decoder.resolve_selection()
    selected_symbol = selection_result.selected_symbol
    return selected_symbol


def run_phrase_demo(window, grid, flash_groups):
    target_sequence = ["H", "I"]
    typed_text = ""
    status_text = create_status_text(window)

    for run_index, target_symbol in enumerate(target_sequence, start=1):
        instruction_text = create_instruction_text(window, target_symbol)
        selected_symbol = run_selection_cycle(
            window=window,
            grid=grid,
            flash_groups=flash_groups,
            target_symbol=target_symbol,
            run_index=run_index,
            status_text=status_text,
        )
        typed_text += selected_symbol
        print(f"selected_symbol={selected_symbol}")

        confirmation_text = visual.TextStim(
            window,
            text=f"selected {selected_symbol}",
            pos=(0, 0.8),
            color=DefaultTextColor,
            height=0.05,
        )
        confirmation_text.draw()
        draw_grid(grid)
        status_text.draw()
        instruction_text.draw()
        window.flip()
        core.wait(1.0)

    final_text = visual.TextStim(
        window,
        text=f"typed text: {typed_text}",
        pos=(0, 0),
        color=DefaultTextColor,
        height=0.06,
    )
    final_text.draw()
    window.flip()
    event.waitKeys(keyList=["space", "escape"])


def main():
    window = create_window()
    grid = create_grid(window)

    row_groups = extract_row_groups(grid)
    column_groups = extract_column_groups(grid)
    flash_groups = build_flash_groups(row_groups, column_groups)

    try:
        run_phrase_demo(window=window, grid=grid, flash_groups=flash_groups)
    finally:
        window.close()
        core.quit()


if __name__ == "__main__":
    main()