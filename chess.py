import sys
import pygame
from pygame.locals import KEYDOWN, MOUSEBUTTONDOWN, QUIT, K_b, K_c, K_v, K_p, K_SPACE
import numpy
import concurrent.futures
from board import Board, Move, PromotionMove
from state import GameState
from ui import create_background, create_sprites, draw_board


# Initialize and create UI
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
pygame.init()
WIDTH = 480
HEIGHT = 560
square_size = 58
piece_size = int(0.78*square_size)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")
background = create_background(screen)

# Create sprites and fonts
sprites = create_sprites(piece_size, square_size)
small_font = pygame.font.Font(None, 28)
controls_text = "C = AI (white),  V = AI (black),  B = undo"
controls = small_font.render(controls_text, 1, (230, 230, 120))

# Create clock, board and global game state
clock = pygame.time.Clock()
board = Board()
state = GameState(board)


def draw():
    global state

    # Update state depending on where the cursor is
    pos, mouse_x, mouse_y = state.update_based_on_cursor()

    # Event handling, perform moves
    for event in pygame.event.get():

        # Exit
        if event.type == QUIT:
            state.print_move_history()
            sys.exit()

        # Key press
        elif event.type == KEYDOWN:
            if event.key == K_b:
                state.rewind()
            elif event.key == K_c:
                state.start_ai_computation(executor, 1)
            elif event.key == K_v:
                state.start_ai_computation(executor, -1)
            elif event.key == K_p:
                state.print_move_history()
            elif event.key == K_SPACE:
                state.execute_ai_move()
            state.reset_ui()

        # Mouse click
        elif event.type == MOUSEBUTTONDOWN:
            if mouse_y < 480:
                if state.selected is None:
                    state.update_selected(pos)
                else:
                    signed_piece = state.board[state.selected]
                    player_sign = numpy.sign(signed_piece)
                    if abs(signed_piece) == 1 and pos.y in [0, 7]:
                        if state.hovered_left:
                            if state.hovered_top:
                                promoted_piece = player_sign * 2
                            else:
                                promoted_piece = player_sign * 4
                        else:
                            if state.hovered_top:
                                promoted_piece = player_sign * 3
                            else:
                                promoted_piece = player_sign * 5
                        move = PromotionMove(state.selected, pos, promoted_piece)
                    else:
                        move = Move(state.selected, pos)
                    state.perform_move(move)
                    state.reset_ui()

    # AI state
    state.check_ai_status()

    # Draw the board
    draw_board(screen, background, state, sprites, square_size, controls)


# Game loop
while 1:
    draw()
    clock.tick(60)
