from psychopy import visual, core

win = visual.Window(size=(900, 700), color="black", units="norm")

rows, cols = 6, 6

x_positions = [-0.8, -0.48, -0.16, 0.16, 0.48, 0.8]
y_positions = [0.6, 0.36, 0.12, -0.12, -0.36, -0.6]

symbols = [
    ["A","B","C","D","E","F"],
    ["G","H","I","J","K","L"],
    ["M","N","O","P","Q","R"],
    ["S","T","U","V","W","X"],
    ["Y","Z","_","DEL","1","2"],
    ["3","4","5","6","7","8"]
]

grid = []

for i in range(rows):
    row = []
    for j in range(cols):
        stim = visual.TextStim(
            win,
            text=symbols[i][j],
            pos=(x_positions[j], y_positions[i]),
            color="white",
            height=0.08
        )
        row.append(stim)
    grid.append(row)


for row in grid:
    for stim in row:
        stim.draw()

win.flip()
core.wait(20)

win.close()
core.quit()