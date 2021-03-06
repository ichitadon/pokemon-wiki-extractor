class PokemonWikiExtractorError(Exception):
    pass

class PokedexBasicInfoNotFoundError(PokemonWikiExtractorError):
    pass

class PokedexDescriptionNotFoundError(PokemonWikiExtractorError):
    pass

class PokedexNumberNotFoundError(PokemonWikiExtractorError):
    pass

class PokedexEvolutionNotFoundError(PokemonWikiExtractorError):
    pass

class MovesBasicInfoNotFoundError(PokemonWikiExtractorError):
    pass

class MovesDescriptionNotFoundError(PokemonWikiExtractorError):
    pass
