from pydantic import BaseModel


class RecipeSchema(BaseModel):
    instructions: str | None = None
    youtube_url: str | None = None

    model_config = {"from_attributes": True}


class MealSchema(BaseModel):
    id: str
    name: str
    thumbnail_url: str | None = None
    recipe: RecipeSchema | None = None

    model_config = {"from_attributes": True}
