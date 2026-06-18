# 画像を1枚だけ表示する最小例
import py5

img = None

def setup():
    global img
    py5.size(500, 320)
    py5.background(20, 30, 60)
    img = py5.load_image("star.png")
    py5.image(img, 200, 110, 100, 100)  # x, y, w, h

py5.run_sketch()