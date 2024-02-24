from pydantic import BaseModel

class User(BaseModel):
    id: str |None = ""
    name: str
    email: str
    disable: bool | None = False

    def get_disable(self):
        return self.disable
    
    def set_disable(self, on_off: bool):
        self.disable = on_off
    
    

class UserPW(User):
    passwd: str
    
    attemp_false_loging: int | None = 0
    

