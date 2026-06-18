import py5

def setup():
    py5.size(400, 400)
    py5.background(255)

def draw():
    py5.background(255)
    py5.no_stroke()

    py5.fill(255, 0, 0)
    py5.circle(100, 200, 100)

    py5.fill(0, 255, 0)
    py5.circle(200, 200, 100)

    py5.fill(0, 0, 255)
    py5.circle(300, 200, 100)

py5.run_sketch()
