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
        tile_map = pygame.image.load(filename).convert_alpha()
        tiles = []
        map_width, map_height = tile_map.get_size()

        for y in range(0, map_height, tile_height):
            for x in range(0, map_width, tile_width):
                rect = pygame.Rect(x, y, tile_width, tile_height)
                tile = tile_map.subsurface(rect)
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
        return self.path_layer.data[tile_y_left][tile_x_left] != 0 and self.path_layer.data[tile_y_right][tile_x_right] != 0

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


class MapRenderer:
    def __init__(self, tmx_data):
        self.tmx_data = tmx_data
        self.doors = self.find_doors()

    def find_doors(self):
        """Trouve toutes les portes sur la carte."""
        doors = []
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and layer.name == "triggers":
                for x, y, gid in layer:
                    if gid == 0:
                        continue
                    properties = self.tmx_data.get_tile_properties_by_gid(gid)
                    if properties and properties.get("type") == "door":
                        properties_middle = self.tmx_data.get_tile_properties_by_gid(gid + 2)
                        properties_bottom = self.tmx_data.get_tile_properties_by_gid(gid + 4)
                        doors.append({
                            "x": x,
                            "y": y,
                            "state": "closed",  # État initial
                            "tiles": [
                                {"x": x, "y": y, "gid": gid, "frames": properties["frames"]},
                                {"x": x , "y": y + 1, "gid": gid + 2, "frames": properties_middle["frames"]},
                                {"x": x, "y": y + 2, "gid": gid + 4, "frames": properties_bottom["frames"]}
                            ],
                            "current_frame": 0,
                            "timer": 0,
                            "animation_speed": 100  # Vitesse d'animation en ms
                        })
        return doors

    def update_doors(self, player):
        """Met à jour l'état et l'animation des portes en fonction de la proximité du joueur."""
        for door in self.doors:
            # On calcule la position centrale de la porte
            door_center_x = (door["x"] + 0.5) * self.tmx_data.tilewidth
            door_center_y = (door["y"] + 1.5) * self.tmx_data.tileheight  # Milieu de la porte (3 tuiles de hauteur)
            distance = ((door_center_x - player.x) ** 2 + (door_center_y - player.y) ** 2) ** 0.5

            # On met à jour l'état de la porte en fonction de la distance
            if distance < 3.4 * TILE_SIZE:  # Seuil de proximité
                if door["state"] == "closed":
                    door["state"] = "opening"
            elif door["state"] == "open":
                door["state"] = "closing"

            # Animation de la porte
            self.animate_door(door)

    def animate_door(self, door):
        """Anime la porte selon son état."""
        current_time = pygame.time.get_ticks()

        if current_time - door["timer"] >= door["animation_speed"]:
            door["timer"] = current_time

            if door["state"] == "opening":
                if door["current_frame"] < len(door["tiles"][0]["frames"]) - 1:
                    door["current_frame"] += 1
                else:
                    door["state"] = "open"

            elif door["state"] == "closing":
                if door["current_frame"] > 0:
                    door["current_frame"] -= 1
                else:
                    door["state"] = "closed"

            # Met à jour les GIDs de chaque partie de la porte (haut, milieu, bas)
            for tile in door["tiles"]:
                tile["gid"] = tile["frames"][door["current_frame"]].gid


    def draw(self, screen, layer_index, player):
        """Dessine la carte et gère les animations de tuiles."""
        current_time = pygame.time.get_ticks()

        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "properties") and layer.properties.get("invisible", False):
                continue
            if layer.name == "triggers":
                continue
            if hasattr(layer, "z") and layer.z != layer_index:
                continue

            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid == 0:
                        continue  # On ignore les tuiles vides

                    # Vérification et gestion des tuiles animées
                    gid = self.handle_tile_animation(gid, current_time) or gid

                    # On dessine la tuile à l'écran
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))

        # On dessine les portes lors de la première passe pour les afficher sous le joueur
        if layer_index < 1:
            self.draw_doors(screen)

    def draw_doors(self, screen):
        """Dessine les portes avec leurs GIDs mis à jour."""
        for door in self.doors:
            for tile in door["tiles"]:
                gid = tile["gid"]
                tile_image = self.tmx_data.get_tile_image_by_gid(gid)
                if tile_image:
                    screen.blit(tile_image, (tile["x"] * self.tmx_data.tilewidth, tile["y"] * self.tmx_data.tileheight))


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
                    return frame.gid # Retourne le GID de la frame actuelle


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Back to Work!")

    # On charge la carte TMX
    tmx_data = load_pygame("ClassRoomPOA.tmx")

    # On initialise le joueur et le renderer de la carte
    player = Player(380, 340, tmx_data, "./img/characters/teacher.png")
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
            else :
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
