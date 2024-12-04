import pygame


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
