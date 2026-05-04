from psychopy import visual, core, event
import csv
import random
from pathlib import Path


WindowSize = (900, 700)
BackgroundColor = "black"
DefaultTextColor = "white"
HighlightColor = "red"

FlashDurationSeconds = 0.12
InterStimulusIntervalSeconds = 0.12
NumberOfTrials = 40

GridRows = 6
GridColumns = 6
TargetSymbol = "H"
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
LogsFilePath = LogsDirectory / "session_001.csv"

def create_window():
    return visual.Window(
        size=WindowSize,
        color=BackgroundColor,
        units="norm",
        checkTiming=False,
    )


def create_instruction_text(window):
    return visual.TextStim(
        window,
        text="rows and columns will flash. focus on one target. press escape to quit.",
        pos=(0, 0.85),
        color=DefaultTextColor,
        height=0.04,
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

def find_target_position(grid, target_symbol):
    for row_index, row in enumerate(grid):
        for column_index, stimulus in enumerate(row):
            if stimulus.text == target_symbol:
                return row_index, column_index

    raise ValueError(f"Target symbol {target_symbol} was not found in the grid.")


def group_contains_target(group, target_symbol):
    return any(stimulus.text == target_symbol for stimulus in group)


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

def run_flash_loop(window, instruction, grid, flash_groups, target_symbol):
    log_file = LogsFilePath.open("w", newline="", encoding="utf-8")
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

    clock = core.Clock()
    target_row_index, target_column_index = find_target_position(grid, target_symbol)

    instruction.draw()
    draw_grid(grid)
    window.flip()
    core.wait(1.5)

    event.clearEvents()

    for trial_index in range(NumberOfTrials):
        pressed_keys = event.getKeys()
        if "escape" in pressed_keys:
            break

        group_type, group_index, group = random.choice(flash_groups)

        is_target_flash = (
            (group_type == "row" and group_index == target_row_index)
            or (group_type == "column" and group_index == target_column_index)
        )

        set_group_color(group, HighlightColor)

        instruction.draw()
        draw_grid(grid)
        window.flip()

        timestamp = clock.getTime()
        write_log_row(
            csv_writer=csv_writer,
            timestamp=timestamp,
            trial_index=trial_index,
            group_type=group_type,
            group_index=group_index,
            is_target_flash=is_target_flash,
        )

        print(
            f"trial={trial_index} type={group_type} index={group_index} target={is_target_flash}"
        )

        core.wait(0.5)

        reset_group_color(group)

        instruction.draw()
        draw_grid(grid)
        window.flip()

        core.wait(0.3)

    log_file.close()


def main():
    window = create_window()
    instruction = create_instruction_text(window)
    grid = create_grid(window)

    row_groups = extract_row_groups(grid)
    column_groups = extract_column_groups(grid)
    flash_groups = build_flash_groups(row_groups, column_groups)

    try:
        run_flash_loop(
            window=window,
            instruction=instruction,
            grid=grid,
            flash_groups=flash_groups,
            target_symbol=TargetSymbol,
        )
    finally:
        window.close()
        core.quit()


if __name__ == "__main__":
    main()