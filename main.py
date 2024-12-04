import pygame
from pytmx import load_pygame, pytmx

# Constants
TILE_SIZE = 32  # Taille d'une tuile en pixels
SCREEN_WIDTH = 26 * TILE_SIZE
SCREEN_HEIGHT = 27 * TILE_SIZE

class TileMap:
    def __init__(self, filename, tile_width, tile_height):
        self.tiles = self.load_tilemap(filename, tile_width, tile_height)

    def load_tilemap(self, filename, tile_width, tile_height):
        """Charge une feuille de sprites (tilemap) et découpe chaque tuile."""
        tilemap = pygame.image.load(filename).convert_alpha()
        tiles = []
        map_width, map_height = tilemap.get_size()

        for y in range(0, map_height, tile_height):
            for x in range(0, map_width, tile_width):
                rect = pygame.Rect(x, y, tile_width, tile_height)
                tile = tilemap.subsurface(rect)
                tiles.append(tile)

        return tiles


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
        self.animation_speed = 3
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

        # Vérifier que la tuile n'est pas bloquante
        return self.path_layer.data[tile_y_left][tile_x_left] != 0 and self.path_layer.data[tile_y_right][tile_x_right] != 0

    def update(self, keys):
        """Met à jour la position et l'animation du joueur."""
        speed = 4
        new_x, new_y = self.x, self.y
        new_action = "idle"
        new_direction = self.direction

        if keys[pygame.K_SPACE]:
            new_direction = "down"
            new_action = "read"
        if keys[pygame.K_LEFT]:
            new_x -= speed
            new_direction = "left"
            new_action = "walk"
        if keys[pygame.K_RIGHT]:
            new_x += speed
            new_direction = "right"
            new_action = "walk"
        if keys[pygame.K_UP]:
            new_y -= speed
            new_direction = "up"
            new_action = "walk"
        if keys[pygame.K_DOWN]:
            new_y += speed
            new_direction = "down"
            new_action = "walk"
        if keys[pygame.K_LSHIFT]:
            self.play_unique_animation([56 * 7 + i for i in range(4)])

        # Réinitialiser l'animation si l'action ou la direction change
        if new_direction != self.direction or new_action != self.action:
            self.animation_frame = 0

        # Vérifier si la nouvelle position est valide
        if self.can_move_to(new_x, new_y):
            self.x, self.y = new_x, new_y

        self.direction = new_direction
        self.action = new_action
        self.animate()

    def animate(self):
        """Gère l'animation du joueur."""
        self.animation_timer += 1
        direction_frames = {"down": 3, "left": 2, "right": 0, "up": 1}

        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = [i for i in range(direction_frames[self.direction] * 6, direction_frames[self.direction] * 6 + 6)]

            if self.action == "idle":
                self.sprite = self.tiles[56 * 1 + frames[self.animation_frame]]
            elif self.action == "walk":
                self.sprite = self.tiles[56 * 2 + frames[self.animation_frame]]
            elif self.action == "read":
                frames = [i for i in range(12)]
                self.sprite = self.tiles[56 * 7 + frames[self.animation_frame]]

            self.animation_frame = (self.animation_frame + 1) % 6

    def play_unique_animation(self, animation_frames):
        """Joue une animation unique qui se répète une seule fois."""

        # Logique pour démarrer l'animation unique
        self.unique_animation = animation_frames
        self.unique_animation_frame = 0

        # Gérer l'animation frame par frame
        if self.unique_animation_frame < len(self.unique_animation):
            frame = self.unique_animation[self.unique_animation_frame]
            self.sprite = self.tiles[frame]  # Mise à jour du sprite avec la frame actuelle
            self.unique_animation_frame += 1
        else:
            # Une fois l'animation terminée, on la réinitialise
            self.unique_animation = None
            self.unique_animation_frame = 0
            self.action = "idle"  # Retour à l'état normal

    def draw(self, screen):
        """Dessine le joueur à l'écran."""
        screen.blit(self.sprite, (self.x, self.y - TILE_SIZE * 5 / 4))


class MapRenderer:
    def __init__(self, tmx_data):
        self.tmx_data = tmx_data

    def draw(self, screen, layer_index, player):
        """Dessine la carte et gère les animations de tuiles."""
        current_time = pygame.time.get_ticks()

        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "properties") and layer.properties.get("invisible", False):
                continue
            if hasattr(layer, "z") and layer.z != layer_index:
                continue

            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid == 0:
                        continue  # Ignorer les tuiles vides

                    # Vérification et gestion des tuiles animées
                    gid = self.handle_tile_animation(gid, current_time) or gid

                    # Dessiner la tuile (fixe ou animée)
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))

    def handle_tile_animation(self, gid, current_time):
        """Gère l'animation des tuiles."""
        properties = self.tmx_data.get_tile_properties_by_gid(gid)
        if properties and "frames" in properties:
            frames = properties["frames"]
            animation_duration = sum(frame.duration for frame in frames)
            time_in_animation = current_time % animation_duration
            cumulative_time = 0
            for frame in frames:
                cumulative_time += frame.duration
                if time_in_animation < cumulative_time:
                    return frame.gid  # Retourne le GID de la frame active


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Projet POA")

    # Charger la carte TMX
    tmx_data = load_pygame("ClassRoomPOA.tmx")

    # Initialiser le joueur
    player = Player(416, 432, tmx_data, "Char01.png")
    map_renderer = MapRenderer(tmx_data)

    # Boucle principale
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Dessiner la carte sous le joueur
        screen.fill((0, 0, 0))  # Fond noir
        map_renderer.draw(screen, 0, player)

        # Mettre à jour et dessiner le joueur
        player.update(keys)
        player.draw(screen)

        # Dessiner la carte au-dessus du joueur
        map_renderer.draw(screen, 2, player)
        pygame.display.flip()

        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
