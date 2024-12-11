from constants import TILE_SIZE
from src import constants
from tilemap import TileMap


class Toybox:
    def __init__(self, x, y, tmx_data, filename_empty, filename_full):
        self.x = x
        self.y = y
        self.tmx_data = tmx_data
        self.tiles_full = TileMap(filename_full, TILE_SIZE, TILE_SIZE * 2).tiles
        self.tiles_empty = TileMap(filename_empty, TILE_SIZE, TILE_SIZE * 2).tiles
        self.sprite = self.tiles_full[0]
        self.animation_frame = 0
        self.is_full = True
        self.animation_speed = 15
        self.animation_timer = self.animation_speed
        self.path_layer = self.get_path_layer()
        self.unique_animation = None
        self.unique_animation_frame = 0

        self.timeBeforeFull = constants.TOYBOX_DELAY
        self.timePassedEmpty = 0

    def get_path_layer(self):
        """Récupère la couche 'path' de la carte TMX."""
        for layer in self.tmx_data.layers:
            if layer.name == "path":
                return layer
        raise ValueError("Aucune couche 'path' trouvée dans le fichier TMX")



    def is_used(self):
        if self.is_full:
            self.is_full = False


    def animate(self):
        """Gère l'animation du joueur."""
        self.animation_timer += 1
        direction_frames = {"down": 3, "left": 2, "right": 0, "up": 1}

        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            if self.is_full:
                self.sprite = self.tiles_full[self.animation_frame]
                self.animation_frame = (self.animation_frame + 1) % 12
            else:
                self.sprite = self.tiles_empty[self.animation_frame]
                self.animation_frame = (self.animation_frame + 1) % 12

        self.timePassedEmpty += 1
        if self.timePassedEmpty >= self.timeBeforeFull:
            self.is_full = True
            self.timePassedEmpty = 0

    def draw(self, screen):
        """Dessine la boite a jouer à l'écran."""
        screen.blit(self.sprite, (self.x, self.y - TILE_SIZE * 5 / 4))
