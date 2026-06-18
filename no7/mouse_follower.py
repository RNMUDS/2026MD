import py5

trail = []
particles = []
rings = []
grid_offset = 0

def setup():
    py5.size(800, 600)
    py5.no_stroke()

def draw():
    py5.background(10, 10, 20)

    for i in range(3):
        py5.fill(255, 255, 255, 3)
        py5.rect(0, 0, py5.width, py5.height)

    global grid_offset
    grid_offset = (grid_offset + 0.5) % 40

    py5.stroke(40, 40, 80, 50)
    py5.stroke_weight(1)
    for x in range(0, py5.width, 40):
        py5.line(x, 0, x, py5.height)
    for y in range(int(-grid_offset), py5.height, 40):
        py5.line(0, y, py5.width, y)

    x, y = py5.mouse_x, py5.mouse_y

    if x > 0 and y > 0:
        trail.append([x, y, py5.frame_count])
        if len(trail) > 80:
            trail.pop(0)

    for i, p in enumerate(trail):
        age = py5.frame_count - p[2]
        if age > 60:
            continue
        pos = remap(age, 0, 60, 0, 1)
        alpha = remap(age, 0, 60, 255, 0)
        size = remap(pos, 0, 1, 3, 25)

        py5.no_stroke()
        py5.fill(255, 100, 200, alpha)
        py5.circle(p[0], p[1], size)

        py5.fill(100, 200, 255, alpha * 0.5)
        py5.circle(p[0], p[1], size * 1.8)

    if py5.is_mouse_pressed:
        for _ in range(8):
            angle = py5.random(py5.TWO_PI)
            speed = py5.random(3, 12)
            particles.append({
                'x': x,
                'y': y,
                'vx': py5.cos(angle) * speed,
                'vy': py5.sin(angle) * speed,
                'life': 100,
                'size': py5.random(5, 15),
                'hue': py5.random(360)
            })

        if py5.frame_count % 4 == 0:
            rings.append({
                'x': x,
                'y': y,
                'size': 10,
                'life': 40,
                'hue': py5.random(360)
            })

    for p in particles[:]:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['vx'] *= 0.96
        p['vy'] *= 0.96
        p['life'] -= 1.5

        if p['life'] <= 0:
            particles.remove(p)
            continue

        py5.no_stroke()
        py5.color_mode(py5.HSB, 360, 100, 100, 100)
        py5.fill(p['hue'], 80, 100, p['life'])
        py5.circle(p['x'], p['y'], p['size'] * p['life'] / 50)

        py5.fill(p['hue'], 40, 100, p['life'] * 0.5)
        py5.circle(p['x'], p['y'], p['size'] * p['life'] / 30)

    for r in rings[:]:
        r['size'] += 8
        r['life'] -= 1

        if r['life'] <= 0:
            rings.remove(r)
            continue

        py5.no_stroke()
        py5.color_mode(py5.HSB, 360, 100, 100, 100)
        py5.no_fill()
        py5.stroke(r['hue'], 90, 100, r['life'] * 2.5)
        py5.stroke_weight(3)
        py5.circle(r['x'], r['y'], r['size'])

        py5.stroke(r['hue'], 60, 100, r['life'])
        py5.stroke_weight(6)
        py5.circle(r['x'], r['y'], r['size'])

    py5.color_mode(py5.RGB)
    py5.no_stroke()
    py5.fill(255, 255, 255, 200)
    py5.circle(x, y, 15)

    py5.fill(255, 100, 100, 150)
    py5.circle(x, y, 25)

    if py5.is_mouse_pressed:
        py5.fill(255, 200, 50, 100)
        py5.circle(x, y, 40 + py5.sin(py5.frame_count * 0.5) * 10)

    dist_to_center = py5.dist(x, y, py5.width/2, py5.height/2)
    if dist_to_center < 100:
        py5.fill(0, 255, 150, 100)
        for i in range(6):
            angle = py5.frame_count * 0.03 + i * py5.TWO_PI / 6
            px = py5.width/2 + py5.cos(angle) * 50
            py5.circle(px, py5.height/2, 20)

    py5.fill(255)
    py5.text_size(14)
    py5.text("click & drag!", 20, 30)
    py5.text("go to center for bonus!", 20, 50)

def remap(value, start1, stop1, start2, stop2):
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))

py5.run_sketch()