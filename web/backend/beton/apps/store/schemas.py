from pydantic import BaseModel


class ProductListOffsetScheme(BaseModel):
    start: int
    end: int
