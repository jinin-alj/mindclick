from psychopy import visual, core


win = visual.Window(
    size=(800, 600),
    color="black",
    units="norm"
)


text = visual.TextStim(win, text="Hello World", color="white")

text.draw()
win.flip()


core.wait(2)


win.close()
core.quit()