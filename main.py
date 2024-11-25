from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Хранилище заявок
requests_db = []
request_id_counter = 1


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.post("/create", response_class=RedirectResponse)
async def create_request(request: Request,
                         equipment: str = Form(...),
                         fault_type: str = Form(...),
                         description: str = Form(...),
                         client: str = Form(...)):
    global request_id_counter
    service_request = {
        "id": request_id_counter,
        "date_added": datetime.now(),
        "equipment": equipment,
        "fault_type": fault_type,
        "description": description,
        "client": client,
        "status": "в ожидании",
        "responsible": None,
        "comments": [],
        "completion_time": None,
    }
    requests_db.append(service_request)
    request_id_counter += 1
    return RedirectResponse(url="/list", status_code=303)


@app.get("/list", response_class=HTMLResponse)
async def list_requests(request: Request):
    return templates.TemplateResponse("list.html", {"request": request, "requests_db": requests_db})


@app.get("/update/{request_id}", response_class=HTMLResponse)
async def update_request_form(request: Request, request_id: int):
    service_request = next((r for r in requests_db if r["id"] == request_id), None)
    if service_request is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return templates.TemplateResponse("update.html", {"request": request, "service_request": service_request})


@app.post("/update/{request_id}", response_class=RedirectResponse)
async def update_request(request_id: int,
                         status: str = Form(...),
                         description: str = Form(...),
                         responsible: str = Form(None)):
    service_request = next((r for r in requests_db if r["id"] == request_id), None)
    if service_request is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    service_request.update({
        "status": status,
        "description": description,
        "responsible": responsible if responsible else service_request["responsible"]
    })

    if status == "выполнено" and not service_request["completion_time"]:
        service_request["completion_time"] = datetime.now()

    return RedirectResponse(url="/list", status_code=303)


@app.post("/add_comment/{request_id}", response_class=RedirectResponse)
async def add_comment(request_id: int, comment: str = Form(...)):
    service_request = next((r for r in requests_db if r["id"] == request_id), None)
    if service_request is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    service_request["comments"].append({"comment": comment, "date": datetime.now()})
    return RedirectResponse(url=f"/update/{request_id}", status_code=303)


@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    completed_count = sum(1 for r in requests_db if r["status"] == "выполнено")
    
    average_time = 0
    completed_requests = [r for r in requests_db if r["status"] == "выполнено"]
    
    if completed_requests:
        total_time = 0
        for r in completed_requests:
            if r.get('completion_time'):
                total_time += (r['completion_time'] - r['date_added']).total_seconds()
        
        if completed_count > 0:
            average_time = total_time / completed_count
    
    fault_types = {}
    for r in requests_db:
        fault_type = r["fault_type"]
        fault_types[fault_type] = fault_types.get(fault_type, 0) + 1

    return templates.TemplateResponse("stats.html", {
        "request": request,
        "completed_count": completed_count,
        "average_time": average_time,
        "fault_types": fault_types
    })


@app.post("/delete/{request_id}", response_class=RedirectResponse)
async def delete_request(request_id: int):
    global requests_db
    requests_db = [r for r in requests_db if r["id"] != request_id]
    return RedirectResponse(url="/list", status_code=303)