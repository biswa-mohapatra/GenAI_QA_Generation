from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
import uvicorn
from llm import GenAi

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

users_db = {}
sessions = {}

class User(BaseModel):
    name: str
    email: str
    password: str

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = users_db.get(email)
    if user and user["password"] == password:
        session_token = str(uuid4())
        sessions[session_token] = user
        response = RedirectResponse(url="/home", status_code=303)
        response.set_cookie(key="session_token", value=session_token)
        return response
    raise HTTPException(status_code=400, detail="Invalid email or password")

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    users_db[email] = {"name": name, "email": email, "password": password}
    return RedirectResponse(url="/", status_code=303)

@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    session_token = request.cookies.get("session_token")
    user = sessions.get(session_token)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "generated_text": "", "user": user})

@app.post("/", response_class=HTMLResponse)
async def generate_text(request: Request, query: str = Form(...)):
    generated_text = GenAi(prompt=query)
    text = generated_text.get_feedback()
    session_token = request.cookies.get("session_token")
    user = sessions.get(session_token)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "generated_text": text, "user": user})

@app.get("/with_sidebar", response_class=HTMLResponse)
async def get_form_with_sidebar(request: Request):
    session_token = request.cookies.get("session_token")
    user = sessions.get(session_token)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("index_with_sidebar.html", {"request": request, "generated_text": "", "user": user})

@app.post("/generate_with_params", response_class=HTMLResponse)
async def generate_text_with_params(request: Request, query: str = Form(...), subject: str = Form(...), topic: str = Form(...), subtopic: str = Form(...)):
    if subject and topic and subtopic:
        prompt = f"Subject: {subject}\nTopic: {topic}\nSub-topic: {subtopic}\n\n{query}"
    else:
        prompt = query
    generated_text = GenAi(prompt=prompt)
    text = generated_text.get_feedback()
    session_token = request.cookies.get("session_token")
    user = sessions.get(session_token)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("index_with_sidebar.html", {"request": request, "generated_text": text, "user": user})

@app.get("/logout")
async def logout(request: Request):
    session_token = request.cookies.get("session_token")
    sessions.pop(session_token, None)
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_token")
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
