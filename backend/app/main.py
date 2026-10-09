from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .database import init_db, get_db_connection
from .services import load_csv_data, generate_reconciliation_html

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and load data
    init_db()
    load_csv_data()
    yield
    # Shutdown

app = FastAPI(title="Better Cotton Exercise API", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Better Cotton Exercise API!"}

@app.get("/organisations")
def get_organisations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM organisations")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/transactions")
def get_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/reconciliation", response_class=HTMLResponse)
def get_reconciliation_view():
    return generate_reconciliation_html()
