from pydantic import BaseModel, Field, model_validator

class AdCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=10000)

    @model_validator(mode="after")
    def strip_fields(self):
        self.title = self.title.strip()
        self.description = self.description.strip()
        # После strip() min_length снова проверится автоматически
        return self


class AdUpdateSchema(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=10000)

    @model_validator(mode="after")
    def strip_fields(self):
        if self.title is not None:
            self.title = self.title.strip()
        if self.description is not None:
            self.description = self.description.strip()
        return self