from psychopy import visual, core, event
import random


WindowSize = (900, 700)
BackgroundColor = "black"
DefaultTextColor = "white"
HighlightColor = "red"

FlashDurationSeconds = 0.12
InterStimulusIntervalSeconds = 0.12
NumberOfTrials = 40

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


def create_window():
    return visual.Window(
        size=WindowSize,
        color=BackgroundColor,
        units="norm",
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


def run_flash_loop(window, instruction, grid, flash_groups):
    instruction.draw()
    draw_grid(grid)
    window.flip()
    core.wait(1.5)

    for trial_index in range(NumberOfTrials):
        if "escape" in event.getKeys():
            break

        group_type, group_index, group = random.choice(flash_groups)

        set_group_color(group, HighlightColor)

        instruction.draw()
        draw_grid(grid)
        window.flip()

        core.wait(FlashDurationSeconds)

        reset_group_color(group)

        instruction.draw()
        draw_grid(grid)
        window.flip()

        core.wait(InterStimulusIntervalSeconds)


def main():
    window = create_window()
    instruction = create_instruction_text(window)
    grid = create_grid(window)

    row_groups = extract_row_groups(grid)
    column_groups = extract_column_groups(grid)
    flash_groups = build_flash_groups(row_groups, column_groups)

    try:
        run_flash_loop(window, instruction, grid, flash_groups)
    finally:
        window.close()
        core.quit()


if __name__ == "__main__":
    main()