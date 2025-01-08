from sqlmodel import SQLModel, Field


#############################
##### PYDANTIC schemas ######
#############################

class UserBaseModel(SQLModel):
    id: int 
    username:str
    name:str| None = Field(default=None)
    first_name:str| None = Field(default=None)
    last_name:str| None = Field(default=None)
    is_superuser :bool = Field(default=False)
    is_staff :bool = Field(default=False)


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str
    email: str | None = None