from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

# 1. Создаем приложение
app = FastAPI(title="Smart Caspian Transit API")

# 2. Настройка CORS (чтобы фронтендер мог отправлять запросы)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Имитация базы данных (тестовые грузы)
CARGO_DB = {
    "CASP-001": {
        "id": "CASP-001",
        "name": "Контейнер с зерном",
        "route": "Астрахань -> Энзели (Морской)",
        "status": "In Transit",
        "current_location": "Порт Оля (ожидание)",
        "distance_km": 850,
        "transport_type": "sea"
    },
    "CASP-002": {
        "id": "CASP-002",
        "name": "Промышленное оборудование",
        "route": "Махачкала -> Амирабад (ЖД + Море)",
        "status": "Customs Hold",
        "current_location": "ЖД станция Махачкала",
        "distance_km": 1200,
        "transport_type": "rail"
    }
}

# 4. Вспомогательные функции (ML и ESG)
def predict_delay(cargo: dict):
    weather_risk = random.uniform(0.1, 0.9)
    port_congestion = random.uniform(0.1, 0.9) if "Оля" in cargo["current_location"] else random.uniform(0.0, 0.4)
    risk_score = (weather_risk + port_congestion) / 2
    reason = "Штормовое предупреждение на Каспии" if weather_risk > 0.7 else "Высокая загруженность причалов"
    return round(risk_score, 2), reason

def calculate_esg(cargo: dict):
    factors = {"sea": 0.015, "rail": 0.025, "truck": 0.080}
    factor = factors.get(cargo["transport_type"], 0.050)
    return round(cargo["distance_km"] * factor, 2)

# 5. Эндпоинты (API)
@app.get("/")
def root():
    return {"message": "Бэкенд работает! Перейди на /docs"}

@app.get("/api/dashboard")
def get_dashboard():
    total_cargo = len(CARGO_DB)
    total_esg = sum(calculate_esg(c) for c in CARGO_DB.values())
    return {
        "total_active_cargo": total_cargo,
        "total_carbon_footprint_tons": round(total_esg, 2),
        "system_status": "Online"
    }

@app.get("/api/cargo/{cargo_id}")
def get_cargo_details(cargo_id: str):
    if cargo_id not in CARGO_DB:
        raise HTTPException(status_code=404, detail="Груз не найден")
    
    cargo = CARGO_DB[cargo_id].copy()
    
    delay_risk, reason = predict_delay(cargo)
    cargo["delay_probability"] = delay_risk
    cargo["delay_reason"] = reason
    cargo["carbon_footprint_tons"] = calculate_esg(cargo)
    
    if delay_risk > 0.65:
        cargo["alternative_route"] = {
            "suggestion": "Перенаправить через порт Махачкала",
            "estimated_saving_days": 3,
            "esg_impact": "Снижение выбросов на 15%"
        }
    else:
        cargo["alternative_route"] = None

    return cargo

class CustomsClearRequest(BaseModel):
    cargo_id: str

@app.post("/api/customs/clear")
def preclear_customs(request: CustomsClearRequest, x_api_key: str = Header(None)):
    if x_api_key != "secret-token-2026":
        raise HTTPException(status_code=403, detail="Доступ запрещен. Неверный API ключ.")
    
    if request.cargo_id not in CARGO_DB:
        raise HTTPException(status_code=404, detail="Груз не найден")
    
    CARGO_DB[request.cargo_id]["status"] = "Customs Pre-Cleared ✅"
    
    return {
        "status": "success",
        "message": f"Груз {request.cargo_id} успешно прошел автоматическое оформление.",
        "blockchain_tx": f"0x{random.getrandbits(64):x}... (Имитация транзакции)"
    }