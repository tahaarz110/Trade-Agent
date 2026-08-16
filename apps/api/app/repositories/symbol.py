from app.models.symbol import Symbol
from app.repositories.base import BaseRepository


class SymbolRepository(BaseRepository[Symbol]):
    model = Symbol
