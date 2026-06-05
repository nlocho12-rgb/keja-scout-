import sys
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core_backend.storage import LocalStorageEngine
from core_backend.engine import HousingEngine
from core_backend.ai_scout import run_smart_scout

app = FastAPI(title="KejaScout Web Client")
templates = Jinja2Templates(directory=os.path.abspath(os.path.join(os.path.dirname(__file__), "templates")))

storage = LocalStorageEngine("../storage")
engine = HousingEngine(storage)

@app.get("/", response_class=HTMLResponse)
def index_view(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "listings": engine.get_all_properties(),
        "ai_response": None
    })

@app.post("/scout-query", response_class=HTMLResponse)
def web_ai_query(request: Request, query: str = Form(...)):
    ai_data = run_smart_scout(query)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "listings": engine.get_all_properties(),
        "ai_response": ai_data,
        "query_text": query
    })

@app.post("/book/{property_id}")
def web_book(property_id: str):
    success, msg = engine.process_safelock_trigger(property_id, "demo_student")
    return {"success": success, "message": msg}

@app.post("/report/{property_id}")
def web_report(property_id: str):
    success, msg = engine.report_listing(property_id)
    return {"success": success, "message": msg}
