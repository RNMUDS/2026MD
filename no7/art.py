import py5
import random

particles = []

class Particle:
    def __init__(self, x, y):
        self.pos = py5.PVector(x, y)
        self.vel = py5.PVector(random.uniform(-2, 2), random.uniform(-2, 2))
        self.acc = py5.PVector(0, 0)
        self.lifespan = 255.0
        self.hue = (x / py5.width) * 360

    def apply_force(self, force):
        self.acc += force

    def update(self):
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0
        self.lifespan -= 2.0

    def display(self):
        py5.stroke(self.hue, 80, 100, self.lifespan)
        py5.stroke_weight(self.lifespan / 50)
        py5.point(self.pos.x, self.pos.y)

def setup():
    py5.size(800, 800)
    py5.background(0)
    py5.color_mode(py5.HSB, 360, 100, 100, 255)

def draw():
    py5.fill(0, 0, 0, 20)
    py5.rect(0, 0, py5.width, py5.height)
    
    if py5.mouse_is_pressed:
        for _ in range(5):
            particles.append(Particle(py5.mouse_x, py5.mouse_y))
            
    for p in particles[:]:
        # Attract to mouse
        mouse_pos = py5.PVector(py5.mouse_x, py5.mouse_y)
        force = mouse_pos - p.pos
        force.set_mag(0.1)
        p.apply_force(force)
        
        p.update()
        p.display()
        if p.lifespan <= 0:
            particles.remove(p)

py5.run_sketch()
