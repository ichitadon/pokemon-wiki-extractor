class PokemonWikiExtractorError(Exception):
    pass

class PokedexBasicInfoNotFoundError(PokemonWikiExtractorError):
    pass

class PokedexDescriptionNotFoundError(PokemonWikiExtractorError):
    pass
