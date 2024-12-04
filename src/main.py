import pygame
from pytmx import load_pygame, pytmx

import pygame
from pytmx import load_pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from map_renderer import MapRenderer
from player import Player


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Back to Work!")

    # On charge la carte TMX
    tmx_data = load_pygame("../map/BacktoWork.tmx")

    # On initialise le joueur et le renderer de la carte
    player = Player(380, 340, tmx_data, "../assets/characters/teacher.png")
    map_renderer = MapRenderer(tmx_data)

    # Boucle principale
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Animation unique (toggle sortir le téléphone et le ranger)
        if keys[pygame.K_f] and player.unique_animation is None:
            if player.action != "idle_phone":
                player.play_unique_animation([56 * 6 + i for i in range(4)], "idle_phone")
            else:
                player.play_unique_animation([56 * 6 + 8 + i for i in range(4)])

        # On met à jour les portes
        map_renderer.update_doors(player)

        # On dessine la carte sous le joueur
        screen.fill((58, 58, 80))  # Couleur de fond
        map_renderer.draw(screen, 0, player)

        # On met à jour le joueur et on le dessine
        player.update(keys)
        player.draw(screen)

        # On dessine la partie de la carte au-dessus du joueur
        map_renderer.draw(screen, 2, player)
        pygame.display.flip()

        # Latence pour maintenir un taux de rafraîchissement constant de 60 FPS
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()