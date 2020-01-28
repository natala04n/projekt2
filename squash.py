# -*- coding: utf-8 -*-

from psychopy import visual, event, core
import multiprocessing as mp
import pygame as pg
import pandas as pd
import filterlib as flt
import blink as blk
#from pyOpenBCI import OpenBCIGanglion


def blinks_detector(quit_program, blink_det, blinks_num, blink,):
    def detect_blinks(sample):
        if SYMULACJA_SYGNALU:
            smp_flted = sample
        else:
            smp = sample.channels_data[0]
            smp_flted = frt.filterIIR(smp, 0)
        #print(smp_flted)

        brt.blink_detect(smp_flted, -38000)
        if brt.new_blink:
            if brt.blinks_num == 1:
                #connected.set()
                print('CONNECTED. Speller starts detecting blinks.')
            else:
                blink_det.put(brt.blinks_num)
                blinks_num.value = brt.blinks_num
                blink.value = 1

        if quit_program.is_set():
            if not SYMULACJA_SYGNALU:
                print('Disconnect signal sent...')
                board.stop_stream()


####################################################
    SYMULACJA_SYGNALU = True
####################################################
    mac_adress = 'd2:b4:11:81:48:ad'
####################################################

    clock = pg.time.Clock()
    frt = flt.FltRealTime()
    brt = blk.BlinkRealTime()

    if SYMULACJA_SYGNALU:
        df = pd.read_csv('dane_do_symulacji/data.csv')
        for sample in df['signal']:
            if quit_program.is_set():
                break
            detect_blinks(sample)
            clock.tick(200)
        print('KONIEC SYGNAŁU')
        quit_program.set()
    else:
        board = OpenBCIGanglion(mac=mac_adress)
        board.start_stream(detect_blinks)

if __name__ == "__main__":


    blink_det = mp.Queue()
    blink = mp.Value('i', 0)
    blinks_num = mp.Value('i', 0)
    #connected = mp.Event()
    quit_program = mp.Event()

    proc_blink_det = mp.Process(
        name='proc_',
        target=blinks_detector,
        args=(quit_program, blink_det, blinks_num, blink,)
        )

    # rozpoczęcie podprocesu
    proc_blink_det.start()
    print('subprocess started')

    ############################################
    # Poniżej należy dodać rozwinięcie programu
    ############################################

    import random
    import pygame, sys
    from pygame.locals import *

    pygame.init()
    fps = pygame.time.Clock()

    #colors
    WHITE = (255,255,255)
    RED = (179,0,0)
    BLUE = (0, 45, 179)
    BEIGE = (255, 218, 179)
    ORANGE = (255, 184, 77)

    #globals
    WIDTH = 600
    HEIGHT = 400
    BALL_RADIUS = 20
    PAD_WIDTH = 12
    PAD2_WIDTH = 8
    PAD_HEIGHT = 120
    PAD2_HEIGHT = 700
    HALF_PAD_WIDTH = PAD_WIDTH // 2
    HALF_PAD2_WIDTH = PAD2_WIDTH // 2
    HALF_PAD_HEIGHT = PAD_HEIGHT // 2
    HALF_PAD2_HEIGHT = PAD2_HEIGHT // 2
    ball_pos = [0,0]
    ball_vel = [0,0]
    paddle1_vel = 6
    paddle2_vel = 2
    score = 0

    #canvas declaration
    window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
    pygame.display.set_caption('Super Squash')

    # helper function that spawns a ball, returns a position vector and a velocity vector
    # if right is True, spawn to the right, else spawn to the left
    def ball_init(right):
        global ball_pos, ball_vel # these are vectors stored as lists
        ball_pos = [WIDTH//2,HEIGHT//2]
        horz = random.randrange(2,4)
        vert = random.randrange(1,3)

        if right == False:
            horz = - horz

        ball_vel = [horz,-vert]

    # define event handlers
    def init():
        global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel, score
        global score
        paddle1_pos = [HALF_PAD_WIDTH - 1,HEIGHT//6]
        paddle2_pos = [WIDTH +1 - HALF_PAD_WIDTH,HEIGHT//2]
        score = 0
        if random.randrange(0,2) == 0:
            ball_init(True)
        else:
            ball_init(False)


    #draw function of canvas
    def draw(canvas):
        global paddle1_pos, paddle2_pos, ball_pos, ball_vel, score

        # rysowanie boiska
        canvas.fill(BEIGE)
        pygame.draw.line(canvas, WHITE, [WIDTH // 2, 0],[WIDTH // 2, HEIGHT], 2)
        pygame.draw.line(canvas, WHITE, [PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 2)
        pygame.draw.line(canvas, WHITE, [WIDTH - PAD_WIDTH, 0],[WIDTH - PAD_WIDTH, HEIGHT], 2)
        pygame.draw.circle(canvas, WHITE, [WIDTH//2, HEIGHT//2], 70, 2)

        # update paddle's vertical position, keep paddle on the screen
        if paddle1_pos[1] > HALF_PAD_HEIGHT and paddle1_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
            paddle1_pos[1] += paddle1_vel
        elif paddle1_pos[1] == HALF_PAD_HEIGHT and paddle1_vel > 0:
            paddle1_pos[1] += paddle1_vel
        elif paddle1_pos[1] == HEIGHT - HALF_PAD_HEIGHT and paddle1_vel < 0:
            paddle1_pos[1] += paddle1_vel

        if paddle2_pos[1] > HALF_PAD_HEIGHT and paddle2_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
            paddle2_pos[1] += paddle2_vel
        elif paddle2_pos[1] == HALF_PAD_HEIGHT and paddle2_vel > 0:
            paddle2_pos[1] += paddle2_vel
        elif paddle2_pos[1] == HEIGHT - HALF_PAD_HEIGHT and paddle2_vel < 0:
            paddle2_pos[1] += paddle2_vel

        #update ball
        ball_pos[0] += int(ball_vel[0])
        ball_pos[1] += int(ball_vel[1])

        #draw paddles and ball
        pygame.draw.circle(canvas, BLUE, ball_pos, 20, 0)
        pygame.draw.polygon(canvas, ORANGE, [[paddle1_pos[0] - HALF_PAD2_WIDTH, paddle1_pos[1] - HALF_PAD2_HEIGHT], [paddle1_pos[0] - HALF_PAD2_WIDTH, paddle1_pos[1] + HALF_PAD2_HEIGHT], [paddle1_pos[0] + HALF_PAD2_WIDTH, paddle1_pos[1] + HALF_PAD2_HEIGHT], [paddle1_pos[0] + HALF_PAD2_WIDTH, paddle1_pos[1] - HALF_PAD2_HEIGHT]], 0)
        pygame.draw.polygon(canvas, RED, [[paddle2_pos[0] - HALF_PAD_WIDTH, paddle2_pos[1] - HALF_PAD_HEIGHT], [paddle2_pos[0] - HALF_PAD_WIDTH, paddle2_pos[1] + HALF_PAD_HEIGHT], [paddle2_pos[0] + HALF_PAD_WIDTH, paddle2_pos[1] + HALF_PAD_HEIGHT], [paddle2_pos[0] + HALF_PAD_WIDTH, paddle2_pos[1] - HALF_PAD_HEIGHT]], 0)


        #ball collision check on top and bottom walls
        if int(ball_pos[1]) <= BALL_RADIUS:
            ball_vel[1] = - ball_vel[1]
        if int(ball_pos[1]) >= HEIGHT + 1 - BALL_RADIUS:
            ball_vel[1] = -ball_vel[1]

        #ball collison check on gutters or paddles
        if int(ball_pos[0]) <= BALL_RADIUS + PAD2_WIDTH and int(ball_pos[1]) in range(paddle1_pos[1] - PAD2_HEIGHT,paddle1_pos[1] + PAD2_HEIGHT,1):
            ball_vel[0] = -ball_vel[0]
            ball_vel[0] *= 1.1
            ball_vel[1] *= 1.1
        elif int(ball_pos[0]) <= BALL_RADIUS + PAD2_WIDTH: #poprawione odbijanie od ściany
            ball_init(True)

        if int(ball_pos[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH and int(ball_pos[1]) in range(paddle2_pos[1] - HALF_PAD_HEIGHT,paddle2_pos[1] + HALF_PAD_HEIGHT,1):
            ball_vel[0] = -ball_vel[0]
            ball_vel[0] *= 1.1
            ball_vel[1] *= 1.1
            score += 1 #dodawanie punktu po odbiciu piłki
        elif int(ball_pos[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH:
            score -= 1 #odejmowanie punktu po nietrafieniu piłki
            ball_init(False)

        #update scores
        myfont = pygame.font.SysFont("Verdana", 20)
        label = myfont.render("Score: "+str(score), 1, (0,0,0))
        canvas.blit(label, (310, 10))


    #kontrola paletki
    def move(event):
        global paddle2_vel

        if blink.value == 1:
            paddle2_vel = -paddle2_vel
            blink.value = 0
    init()



    #game loop
    while True:
        draw(window)
        paddle1_vel = 1

        for event in pygame.event.get():
            if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
        if blink.value==1:
            print('BLINK!')
            move(event)

        pygame.display.update()
        fps.tick(200)


# Zakończenie podprocesów
    proc_blink_det.join()
