import pygame
from pytmx import load_pygame

from agent import State
from child_agent import ChildAgent
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHILDREN_POS, TOYBOX_POS, CHILDREN_COUNT, DISPLAY_PATH, USE_PLAYER, FRAMES_PER_SECOND, MAX_HUNGRY_TIMER
from map_renderer import MapRenderer
from player import Player
from src import constants
from src.constants import TEST_MODE
from toybox import Toybox
from teacher_agent import TeacherAgent


def check_collision(environment, children, teacher, toybox):
    pos_teacher = get_tile_coordinate(environment["teacher"].player.x, environment["teacher"].player.y)
    pos_toybox = get_tile_coordinate(environment["toybox_pos"][0], environment["toybox_pos"][1])
    for child in children:
        if child.state == State.HUNGRY:
            pos_child = get_tile_coordinate(child.player.x, child.player.y)
            if pos_child[0] == pos_teacher[0] and pos_child[1] == pos_teacher[1] or pos_child[2] == pos_teacher[2] and pos_child[3] == pos_teacher[3]:
                child.teacher_caught_you()
                teacher.child_caught()
            if (pos_child[0] == pos_toybox[0] and pos_child[1] == pos_toybox[1] or pos_child[2] == pos_toybox[2] and pos_child[3] == pos_toybox[3]) and toybox.is_full:
                child.play_with_toy()
                toybox.is_used()

    if USE_PLAYER:
        pos_player = get_tile_coordinate(environment["player"][0], environment["player"][1])
        if ((pos_player[0] == pos_toybox[0] and pos_player[1] == pos_toybox[1]) or (pos_player[2] == pos_toybox[2] and pos_player[3] == pos_toybox[3])) and toybox.is_full:
            toybox.is_used()



def get_tile_coordinate(player_x, player_y):
    tile_x_left = player_x // TILE_SIZE
    tile_y_left = player_y // TILE_SIZE
    tile_x_right = (player_x + TILE_SIZE - 1) // TILE_SIZE
    tile_y_right = player_y // TILE_SIZE

    return tile_x_left, tile_y_left, tile_x_right, tile_y_right


def draw_scores(screen, scores, font):
    """Dessine les scores à l'écran."""
    score_texts = [
        f"Child: {scores['children']}",
        f"Teacher: {scores['teacher']}"
    ]

    # Affichage des scores en haut à gauche
    for i, text in enumerate(score_texts):
        score_surface = font.render(text, True, (255, 255, 255))  # Texte blanc
        screen.blit(score_surface, (SCREEN_WIDTH - 150, 10 + i * 30))  # Décalage entre chaque ligne


def display_path(grid, color, screen, font):
    for y, row in enumerate(zip(*grid)):
        for x, cell in enumerate(row):
            if cell == -1:  # Chemin
                pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)


def main():
    dt = 0
    pygame.init()
    pygame.font.init()

    # On définit la police d'écriture et sa taille
    font = pygame.font.SysFont("Arial", 22)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Back to Work!")

    # On charge la carte TMX
    tmx_data = load_pygame("./map/BacktoWork.tmx")

    # On initialise le renderer de la carte et les agents
    map_renderer = MapRenderer(tmx_data)
    teacher = TeacherAgent(12 * TILE_SIZE, 12 * TILE_SIZE, tmx_data, "./assets/characters/teacher.png")
    children = [ChildAgent(CHILDREN_POS[i][0], CHILDREN_POS[i][1], tmx_data, "./assets/characters/0" + str(i + 1) + ".png" if i + 1 < 10 else "./assets/characters/" + str(i + 1) + ".png") for i in range(CHILDREN_COUNT)]
    toybox = Toybox(TOYBOX_POS[0], TOYBOX_POS[1], tmx_data, "./assets/object/toybox_empty.png","./assets/object/toybox_full.png")
    player = None

    environment = {
        "toybox_pos": (TOYBOX_POS[0], TOYBOX_POS[1]),
        "children": children,
        "teacher": teacher,
    }

    if USE_PLAYER:
        player = Player(380, 340, tmx_data, "./assets/characters/teacher.png")
        environment["player"] = (player.x, player.y)

    # Boucle principale
    clock = pygame.time.Clock()
    running = True
    frame_count = 0
    while running:
        # On affiche les fps dans le caption de la fenêtre
        pygame.display.set_caption(f"Back to Work! - FPS: {int(clock.get_fps())}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Si on clique sur la souris, on change la position de la boîte à jouet et on met les enfants en état de faim
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                tile_x, tile_y = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE

                environment["toybox_pos"] = (tile_x*TILE_SIZE, tile_y*TILE_SIZE)
                print("new candy position ", environment["toybox_pos"])
                for child in children:
                    child.state = State.HUNGRY

        keys = pygame.key.get_pressed()

        if USE_PLAYER:
            # Animation unique (toggle sortir le téléphone et le ranger)
            if keys[pygame.K_f] and player.unique_animation is None:
                player.play_unique_animation_by_name("phone")

            if keys[pygame.K_k] and player.unique_animation is None:
                player.play_unique_animation_by_name("hurt")

            if keys[pygame.K_l] and player.unique_animation is None:
                player.play_unique_animation_by_name("shoot")

            if keys[pygame.K_n] and player.unique_animation is None:
                player.play_unique_animation_by_name("catch")

        # On met à jour les portes

        if USE_PLAYER:
            map_renderer.update_doors([player, teacher.player] + [child.player for child in children])
        else :
            map_renderer.update_doors([teacher.player] + [child.player for child in children])

        # On dessine la carte sous le joueur
        screen.fill((58, 58, 80))  # Couleur de fond
        map_renderer.draw(screen, 0)

        # On vérifie les collisions
        check_collision(environment, children, teacher, toybox)

        scores = {
            "children": sum([child.score for child in children]),
            "teacher": teacher.score
        }
        draw_scores(screen, scores, font)

        # On dessine la boîte à jouet
        toybox.animate()
        toybox.draw(screen)
        
        # On met à jour le joueur et on le dessine
        if USE_PLAYER:
            player.update(keys)
            player.draw(screen)

        # On met à jour les agents
        teacher.update(environment, dt)
        for child in children:
            child.update(environment, dt)

        # On dessine les chemins des agents
        if DISPLAY_PATH:
            display_path(teacher.grid, (255, 0, 0), screen, font)
            for child in children:
                display_path(child.grid, (0, 255, 0), screen, font)

        # On dessine les agents de haut en bas
        for agent in sorted(children + [teacher], key=lambda x: x.player.y):
            agent.player.draw(screen)

        # On dessine la partie de la carte au-dessus du joueur
        map_renderer.draw(screen, 2)
        pygame.display.flip()

        # Latence pour maintenir un taux de rafraîchissement constant de 60 FPS
        dt = clock.tick(FRAMES_PER_SECOND) / 1000

        if TEST_MODE:
            frame_count += 1

            # On vérifie si on a atteint le nombre de frames par seconde
            if frame_count >= 60 * 60:
                print(f"ToyBoxDelay : {constants.TOYBOX_DELAY} - Scores :" + str(scores))
                frame_count = 0
                for child in children:
                    child.player.x = CHILDREN_POS[children.index(child)][0]
                    child.player.y = CHILDREN_POS[children.index(child)][1]
                    child.state = State.IDLE
                    child.score = 0
                    child.hungry_timer = 0
                    child.path = []
                    child.grid = []
                teacher.state = State.IDLE
                teacher.score = 0
                teacher.path = []
                teacher.grid = []
                teacher.player.x = 12 * TILE_SIZE
                teacher.player.y = 12 * TILE_SIZE

                teacher.state = State.IDLE
                constants.TOYBOX_DELAY += 1

    pygame.quit()


if __name__ == "__main__":
    main()
