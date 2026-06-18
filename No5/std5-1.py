import py5

values = []
index = 0
ufo_img = None

def setup():
    py5.size(600, 400)
    global ufo_img
    ufo_img = py5.load_image("ufo.png")

    lines = py5.load_strings("acc_y.csv")
    for line in lines[1:]:
        parts = line.split(",")
        values.append(float(parts[1]))

def draw():
    global index
    py5.background(135, 206, 235)

    x = py5.remap(index, 0, len(values), 50, py5.width - 50)

    y = py5.remap(values[index], -10, 10, py5.height - 80, 80)
    py5.image(ufo_img, x, y, 80, 80)

    index += 1
    if index >= len(values):
        index = 0

py5.run_sketch()
