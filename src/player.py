import pygame

from constants import TILE_SIZE
from tilemap import TileMap


class Player:
    def __init__(self, x, y, tmx_data, filename):
        self.x = x
        self.y = y
        self.tmx_data = tmx_data
        self.tiles = TileMap(filename, TILE_SIZE, TILE_SIZE * 2).tiles
        self.sprite = self.tiles[3]
        self.animation_frame = 0
        self.direction = "down"
        self.action = "idle"
        self.animation_speed = 6
        self.speed = 2
        self.animation_timer = self.animation_speed
        self.path_layer = self.get_path_layer()
        self.unique_animation = None
        self.unique_animation_frame = 0

    def get_path_layer(self):
        """Récupère la couche 'path' de la carte TMX."""
        for layer in self.tmx_data.layers:
            if layer.name == "path":
                return layer
        raise ValueError("Aucune couche 'path' trouvée dans le fichier TMX")

    def can_move_to(self, x, y):
        """Vérifie si le joueur peut se déplacer sur la case donnée."""
        if x < 0 or x + TILE_SIZE > self.tmx_data.width * TILE_SIZE or y - TILE_SIZE < 0 or y > self.tmx_data.height * TILE_SIZE:
            return False

        tile_x_left = x // TILE_SIZE
        tile_y_left = y // TILE_SIZE
        tile_x_right = (x + TILE_SIZE - 1) // TILE_SIZE
        tile_y_right = y // TILE_SIZE

        # On vérifie que la tuile n'est pas bloquante
        return self.path_layer.data[tile_y_left][tile_x_left] != 0 and self.path_layer.data[tile_y_right][
            tile_x_right] != 0

    def move(self, direction):
        """Met à jour la position et l'animation du joueur."""
        new_x, new_y = self.x, self.y

        # None si l'action en cours ne contient pas idle
        new_action = self.action if "idle" in self.action else "idle"
        new_direction = self.direction

        if direction == "down":
            new_y += self.speed
            new_direction = "down"
            new_action = "walk"
        elif direction == "up":
            new_y -= self.speed
            new_direction = "up"
            new_action = "walk"
        elif direction == "left":
            new_x -= self.speed
            new_direction = "left"
            new_action = "walk"
        elif direction == "right":
            new_x += self.speed
            new_direction = "right"
            new_action = "walk"

        elif direction == "read":
            new_direction = "down"
            new_action = "read"

        # On réinitialise l'animation si l'action ou la direction change
        if new_direction != self.direction or new_action != self.action:
            self.animation_frame = 0

        # On vérifie si la nouvelle position est valide
        if self.can_move_to(new_x, new_y):
            self.x, self.y = new_x, new_y

        self.direction = new_direction
        self.action = new_action

        # Si une animation unique est en cours, on la joue
        if self.unique_animation:
            self.play_unique_animation()
        else:
            self.animate()

    def update(self, keys):
        """Met à jour la position et l'animation du joueur."""
        new_x, new_y = self.x, self.y

        # None si l'action en cours ne contient pas idle
        new_action = self.action if "idle" in self.action else "idle"
        new_direction = self.direction

        # Bloquer le mouvement si UP et DOWN sont pressés en même temps
        if keys[pygame.K_UP] and keys[pygame.K_DOWN]:
            return

        # Bloquer le mouvement si LEFT et RIGHT sont pressés en même temps
        if keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]:
            return

        if keys[pygame.K_DOWN]:
            new_y += self.speed
            new_direction = "down"
            new_action = "walk"
        elif keys[pygame.K_UP]:
            new_y -= self.speed
            new_direction = "up"
            new_action = "walk"
        elif keys[pygame.K_LEFT]:
            new_x -= self.speed
            new_direction = "left"
            new_action = "walk"
        elif keys[pygame.K_RIGHT]:
            new_x += self.speed
            new_direction = "right"
            new_action = "walk"

        elif keys[pygame.K_SPACE]:
            new_direction = "down"
            new_action = "read"

        # On réinitialise l'animation si l'action ou la direction change
        if new_direction != self.direction or new_action != self.action:
            self.animation_frame = 0

        # On vérifie si la nouvelle position est valide
        if self.can_move_to(new_x, new_y):
            self.x, self.y = new_x, new_y

        self.direction = new_direction
        self.action = new_action

        # Si une animation unique est en cours, on la joue
        if self.unique_animation:
            self.play_unique_animation()
        else:
            self.animate()

    def animate(self):
        """Gère l'animation du joueur."""
        self.animation_timer += 1
        direction_frames = {"down": 3, "left": 2, "right": 0, "up": 1}

        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0

            if self.action == "walk":
                self.sprite = self.tiles[56 * 2 + direction_frames[self.direction] * 6 + self.animation_frame]
                self.animation_frame = (self.animation_frame + 1) % 6
            elif self.action == "read":
                self.sprite = self.tiles[56 * 7 + self.animation_frame]
                self.animation_frame = (self.animation_frame + 1) % 12
            elif self.action == "idle_phone":
                self.sprite = self.tiles[56 * 6 + 4 + self.animation_frame]
                self.animation_frame = (self.animation_frame + 1) % 4

            # Si aucune action n'est en cours (ou idle), on joue l'animation idle
            else:
                self.sprite = self.tiles[56 * 1 + direction_frames[self.direction] * 6 + self.animation_frame]
                self.animation_frame = (self.animation_frame + 1) % 6


    def play_unique_animation_by_name(self, name):
        direction_frames = {"down": 3, "left": 2, "right": 0, "up": 1}
        if name == "phone":
            if self.action != "idle_phone":
                self.play_unique_animation([56 * 6 + i for i in range(4)], "idle_phone")
            else:
                self.play_unique_animation([56 * 6 + 8 + i for i in range(4)])
        elif name == "hurt":
            self.play_unique_animation([56 * 19 + i + direction_frames[self.direction] * 3 for i in range(3)], "hurt")
        elif name == "shoot":
            self.play_unique_animation([56 * 18 + i + direction_frames[self.direction] * 3 for i in range(3)], "shoot")
        elif name == "catch":
            self.play_unique_animation([56 * 15 + i + direction_frames[self.direction] * 6 for i in range(6)], "catch")


    def play_unique_animation(self, animation_frames=None, action="idle"):
        """Joue une animation unique qui se répète une seule fois."""
        self.animation_timer += 1

        if animation_frames is not None or self.animation_timer >= self.animation_speed:
            self.animation_timer = 0

            # Logique pour démarrer l'animation unique
            if animation_frames:
                self.unique_animation = animation_frames
                self.unique_animation_frame = 0
                self.action = action

            # Gestion de l'animation frame par frame
            if self.unique_animation_frame < len(self.unique_animation):
                frame = self.unique_animation[self.unique_animation_frame]
                self.sprite = self.tiles[frame]  # Mise à jour du sprite avec la frame actuelle
                self.unique_animation_frame += 1
            else:
                # Une fois l'animation terminée, on la réinitialise
                self.unique_animation = None
                self.unique_animation_frame = 0

    def draw(self, screen):
        """Dessine le joueur à l'écran."""
        screen.blit(self.sprite, (self.x, self.y - TILE_SIZE * 5 / 4))
