import pygame
from pytmx import load_pygame

from agent import State
from child_agent import ChildAgent
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CHILDREN_POS, TOYBOX_POS, CHILDREN_COUNT
from map_renderer import MapRenderer
from player import Player
from src.toybox import Toybox
from teacher_agent import TeacherAgent


def check_collision(environment, children, teacher, toybox):
    pos_teacher = get_tile_coordinate(environment["teacher"][0], environment["teacher"][1])
    pos_toybox = get_tile_coordinate(environment["toybox_pos"][0], environment["toybox_pos"][1])
    pos_player = get_tile_coordinate(environment["player"][0], environment["player"][1])
    for i in range (len(environment["children"])):
        if children[i].state == State.HUNGRY:
            pos_child = get_tile_coordinate(environment["children"][i].player.x, environment["children"][i].player.y)
            if pos_child[0] == pos_teacher[0] and pos_child[1] == pos_teacher[1] or pos_child[2] == pos_teacher[2] and pos_child[3] == pos_teacher[3]:
                children[i].teacher_caught_you()
                teacher.child_caught()
                childs[i].player.stun_timer = 60
                teacher.player.stun_timer = 60
            if (pos_child[0] == pos_toybox[0] and pos_child[1] == pos_toybox[1] or pos_child[2] == pos_toybox[2] and pos_child[3] == pos_toybox[3]) and toybox.is_full:
                children[i].play_with_toy()
                toybox.is_used()
    if ((pos_player[0] == pos_toybox[0] and pos_player[1] == pos_toybox[1]) or (pos_player[2] == pos_toybox[2] and pos_player[3] == pos_toybox[3])) and  toybox.is_full:
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
    tmx_data = load_pygame("../map/BacktoWork.tmx")

    # On initialise le joueur et le renderer de la carte
    player = Player(380, 340, tmx_data, "../assets/characters/teacher.png")
    map_renderer = MapRenderer(tmx_data)
    teacher = TeacherAgent(12*TILE_SIZE, 12*TILE_SIZE, tmx_data, "../assets/characters/teacher.png")

    # On initialise les enfants avec leurs positions
    children = [ChildAgent(CHILDREN_POS[i][0], CHILDREN_POS[i][1], tmx_data, "../assets/characters/0" + str(i + 1) + ".png") for i in range(CHILDREN_COUNT)]
    toybox = Toybox(TOYBOX_POS[0], TOYBOX_POS[1], tmx_data, "../assets/object/toybox_empty.png","../assets/object/toybox_full.png")
    candy_pos = TOYBOX_POS

    environment = {
        "toybox_pos": (candy_pos[0], candy_pos[1]),
        "children": children,
        "teacher": (teacher.player.x, teacher.player.y),
        "player": (player.x, player.y)
    }

    # Boucle principale
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                tile_x, tile_y = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE

                environment["toybox_pos"] = (tile_x*TILE_SIZE, tile_y*TILE_SIZE)
                print("new candy position ", environment["toybox_pos"])
                for child in children:
                    child.state = State.HUNGRY

        keys = pygame.key.get_pressed()

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
        map_renderer.update_doors([player, teacher.player] + [child.player for child in children])

        # On dessine la carte sous le joueur
        screen.fill((58, 58, 80))  # Couleur de fond
        map_renderer.draw(screen, 0, player)

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
        player.update(keys)
        player.draw(screen)

        # On met à jour les agents
        teacher.update(environment, dt)
        teacher.player.draw(screen)

        for child in children:
            child.update(environment, dt)
            child.player.draw(screen)

        # On dessine les chemins des agents
        display_path(teacher.grid, (255, 0, 0), screen, font)
        for child in children:
            display_path(child.grid, (0, 255, 0), screen, font)

        # On dessine la partie de la carte au-dessus du joueur
        map_renderer.draw(screen, 2, player)
        pygame.display.flip()

        # Latence pour maintenir un taux de rafraîchissement constant de 60 FPS
        dt = clock.tick(60) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()
