from fastapi.templating import Jinja2Templates
from app.utils.time import get_now

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["now"] = get_now
