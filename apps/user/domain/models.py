from apps.user.application.schemas import UserBaseModel
from sqlmodel import Field,SQLModel

#############################
##### Database model ########
#############################

class Users(UserBaseModel,table=True):
    email: str = Field(default=None, primary_key=True)
    password: str