from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


passports = []
passport_id_counter = 1

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.post("/create", response_class=RedirectResponse)
async def create_passport(request: Request, 
                          first_name: str = Form(...), 
                          last_name: str = Form(...),
                          patronymic: str = Form(...), 
                          passport_series: str = Form(...), 
                          passport_number: str = Form(...)):
    global passport_id_counter
    passport = {
        "id": passport_id_counter,
        "first_name": first_name,
        "last_name": last_name,
        "patronymic": patronymic,
        "passport_series": passport_series,
        "passport_number": passport_number
    }
    passports.append(passport)
    passport_id_counter += 1
    return RedirectResponse(url="/list", status_code=303)

@app.get("/list", response_class=HTMLResponse)
async def list_passports(request: Request):
    return templates.TemplateResponse("list.html", {"request": request, "passports": passports})

@app.get("/update/{passport_id}", response_class=HTMLResponse)
async def update_passport_form(request: Request, passport_id: int):
    passport = next((p for p in passports if p["id"] == passport_id), None)
    if passport is None:
        raise HTTPException(status_code=404, detail="Паспорт не найден")
    return templates.TemplateResponse("update.html", {"request": request, "passport": passport})

@app.post("/update/{passport_id}", response_class=RedirectResponse)
async def update_passport(passport_id: int,
                          first_name: str = Form(...),
                          last_name: str = Form(...),
                          patronymic: str = Form(...),
                          passport_series: str = Form(...),
                          passport_number: str = Form(...)):
    passport = next((p for p in passports if p["id"] == passport_id), None)
    if passport is None:
        raise HTTPException(status_code=404, detail="Паспорт не найден")
    
    passport.update({
        "first_name": first_name,
        "last_name": last_name,
        "patronymic": patronymic,
        "passport_series": passport_series,
        "passport_number": passport_number
    })
    return RedirectResponse(url="/list", status_code=303)

@app.post("/delete/{passport_id}", response_class=RedirectResponse)
async def delete_passport(passport_id: int):
    global passports
    passports = [p for p in passports if p["id"] != passport_id]
    return RedirectResponse(url="/list", status_code=303)
