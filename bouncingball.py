import pygame as pg
import objects
pg.init()

# värit
black = [0, 0, 0]
white = (255, 255, 255)
# peli-ikkunan aloitus
width = 800
height = 600
size = [width, height]
screen = pg.display.set_mode(size)

# kappaleet
camera = objects.camera(size)
ball = objects.ball([width/2, height/2], [0, 0], 20, white)
obstacles = camera.openlevel("levels/level1.json")

# kello
clock = pg.time.Clock()
rate = 60

goleft = False
goright = False
goup = False
godown = False

done = False
while not done:

    clock.tick(rate)

    # nappien painallus logiikka:
    for event in pg.event.get():
        if event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
            goleft = True
        if event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
            goright = True
        if event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
            godown = True
        if event.type == pg.KEYUP and event.key == pg.K_LEFT:
            goleft = False
        if event.type == pg.KEYUP and event.key == pg.K_RIGHT:
            goright = False
        if event.type == pg.KEYUP and event.key == pg.K_DOWN:
            godown = False
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            done = True

    if goleft:
        ball.vel[0] -= 0.3
    if goright:
        ball.vel[0] += 0.3
    if godown:
        ball.vel[1] += 0.1

    # tarkistaa onko este ruudulla
    camera.checkobstacles(obstacles)
    # kappaleiden liikutus:
    ball.move()
    camera.move(ball.pos)
    ball.update(camera.pos, camera.deltapos, size)
    for obstacle in camera.nearobstacles:
        obstacle.update(camera.deltapos)
    ball.check(camera.nearobstacles)

    # peli-ikkunan piirto:
    screen.fill(black)
    for obstacle in camera.nearobstacles:
        obstacle.draw(screen)
    ball.draw(screen)
    pg.display.flip()

pg.quit()
