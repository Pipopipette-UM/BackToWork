import pygame
from pytmx import load_pygame, pytmx

import pygame
from pytmx import load_pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from map_renderer import MapRenderer
from player import Player
from agent import State
from teacher_agent import TeacherAgent
from child_agent import ChildAgent
from toybox import Toybox

from pathfinding import Dijkstra
from pathfinding import AStar

def checkCollision(environment, childs, teacher, toybox):

    pos_teacher = get_tile_coordinate(environment["teacher"][0], environment["teacher"][1])
    pos_toybox = get_tile_coordinate(environment["toybox_pos"][0], environment["toybox_pos"][1])
    pos_player = get_tile_coordinate(environment["player"][0], environment["player"][1])
    for i in range (len(environment["child"])):
        if childs[i].state == State.HUNGRY:
            pos_child = get_tile_coordinate(environment["child"][i].player.x, environment["child"][i].player.y)
            if pos_child[0] == pos_teacher[0] and pos_child[1] == pos_teacher[1] or pos_child[2] == pos_teacher[2] and pos_child[3] == pos_teacher[3]:
                childs[i].teacher_caught_you()
                teacher.child_caught()
            if (pos_child[0] == pos_toybox[0] and pos_child[1] == pos_toybox[1] or pos_child[2] == pos_toybox[2] and pos_child[3] == pos_toybox[3]) and toybox.is_full:
                childs[i].play_with_toy()
                toybox.is_used()
    if ((pos_player[0] == pos_toybox[0] and pos_player[1] == pos_toybox[1]) or (pos_player[2] == pos_toybox[2] and pos_player[3] == pos_toybox[3])) and  toybox.is_full:
        toybox.is_used()



def get_tile_coordinate(player_x, player_y):
    tile_x_left = player_x // TILE_SIZE
    tile_y_left = player_y // TILE_SIZE
    tile_x_right = (player_x + TILE_SIZE - 1) // TILE_SIZE
    tile_y_right = player_y // TILE_SIZE

    return tile_x_left, tile_y_left, tile_x_right, tile_y_right


def draw_scores(screen, scores,font):
    """Dessine les scores à l'écran."""
    score_texts = [
        f"Child: {scores['child']}",
        f"Teacher: {scores['teacher']}"
    ]

    # Affichage des scores en haut à gauche
    for i, text in enumerate(score_texts):
        score_surface = font.render(text, True, (255, 255, 255))  # Texte blanc
        screen.blit(score_surface, (SCREEN_WIDTH-150, 10 + i * 30))  # Décalage entre chaque ligne

def display_path(grid,color,screen,font):
    font = pygame.font.Font(None, 24)
    for y, row in enumerate(zip(*grid)): 
                for x, cell in enumerate(row):
                    if cell == 1: #Mur 
                        text = font.render(str(cell), True, (255, 255, 255))
                        #pygame.draw.rect(screen, (255, 255, 255), (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 50)
                    if cell == -1: #Chemin
                        pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

def main():
    dt = 0
    pygame.init()
    pygame.font.init()

    # Choisir une police et une taille
    font = pygame.font.SysFont("Arial", 24)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Back to Work!")

    # On charge la carte TMX
    tmx_data = load_pygame("../map/BacktoWork.tmx")

    # On initialise le joueur et le renderer de la carte
    player = Player(380, 340, tmx_data, "../assets/characters/teacher.png")
    map_renderer = MapRenderer(tmx_data)
    teacher = TeacherAgent(4*TILE_SIZE, 10*TILE_SIZE, tmx_data, "../assets/characters/teacher.png")
    child  = ChildAgent(19*TILE_SIZE, 14*TILE_SIZE, tmx_data, "../assets/characters/01.png")
    
    toybox = Toybox(32*6, 32*9, tmx_data, "../assets/object/toybox_empty.png","../assets/object/toybox_full.png")
    candy_pos = (TILE_SIZE*6, TILE_SIZE*9)
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
                
                candy_pos = (tile_x*TILE_SIZE, tile_y*TILE_SIZE)
                print("new candy position ", environment["toybox_pos"])
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
        map_renderer.update_doors(player)

        # On dessine la carte sous le joueur
        screen.fill((58, 58, 80))  # Couleur de fond
        map_renderer.draw(screen, 0, player)

        # On creer notre environnement
        environment = {
            "toybox_pos": (toybox.x, toybox.y),
            "child": [child],
            "teacher": (teacher.player.x, teacher.player.y),
            "player": (player.x, player.y)
        }



        # On vérifie les collisions
        checkCollision(environment, [child], teacher, toybox)

        scores = {
            "child": child.score,
            "teacher": teacher.score
        }

        draw_scores(screen, scores, font)

        toybox.animate()
        toybox.draw(screen)
        
        # On met à jour le joueur et on le dessine
        player.update(keys)
        player.draw(screen)

        # On met à jour les agents
        teacher.update(environment, dt)
        teacher.player.draw(screen)

        child.update(environment, dt)
        child.player.draw(screen)

        
        display_path(teacher.grid,(255,0,0),screen,font)

        display_path(child.grid,(0,255,0),screen,font)
        

        # On dessine la partie de la carte au-dessus du joueur
        map_renderer.draw(screen, 2, player)
        pygame.display.flip()

        # Latence pour maintenir un taux de rafraîchissement constant de 60 FPS
        dt = clock.tick(60) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()
