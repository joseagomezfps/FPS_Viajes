from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Match

db = SessionLocal()

partidos_iniciales = [
    {
        "home_team": "Getafe FC",
        "away_team": "Sevilla FC",
        "stadium": "Coliseum",
        "city": "Getafe",
        # 1/11/2026 - a las 21:00 h
        "match_date": datetime(2026, 11, 1, 21, 0)
    },
    {
        "home_team": "Real Sociedad",
        "away_team": "Sevilla FC",
        "stadium": "Reale Arena",
        "city": "San Sebastián",
        # 29/11/2026 - a las 21:00 h
        "match_date": datetime(2026, 11, 29, 21, 0)
    }
]

for p in partidos_iniciales:
    db.add(Match(**p))

db.commit()
db.close()
print("¡Partidos cargados correctamente en la base de datos!")