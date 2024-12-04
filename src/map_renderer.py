import pygame
from pytmx import pytmx

from constants import TILE_SIZE


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
                                {"x": x, "y": y + 1, "gid": gid + 2, "frames": properties_middle["frames"]},
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
                    return frame.gid  # Retourne le GID de la frame actuelle
