from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import assignees, report, scenario
from .routers import zones, plants, cameras, detection
from . import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager


def prepopulate_plants(db: Session):
    if db.query(models.Plant).count() == 0:
        plants = [
            models.Plant(name="Aptar Annecy", description="France Manufacturing", address="19 Avenue des Vieux Moulins 74000 Annecy,France", plantConfidence=0.75),
            models.Plant(name="Aptar Berazategui", description="Argentina Manufacturing", address="Colectora Autovía 2 El Pato, Argentina", plantConfidence=0.75),
            models.Plant(name="Aptar Brecey", description="France Manufacturing", address="Rue du Bocage 50370 Brécey, Normandie", plantConfidence=0.75),
            models.Plant(name="Aptar Cajamar", description="Colombia Manufacturing", address="2121 Avenida Doutor Antônio João Abdala, Colombia", plantConfidence=0.75),
            models.Plant(name="Aptar Cali", description="Colombia Manufacturing", address="6763537 Cantarrana, Valle del Cauca Colombia", plantConfidence=0.75),
            models.Plant(name="Aptar Camaçari", description="Brazil Manufacturing", address="13 2° Travessa Massaranduba, Brazil", plantConfidence=0.75),
            models.Plant(name="Aptar Cary", description="USA Manufacturing", address="1160 Silver Lake Road 60013 Cary, IL", plantConfidence=0.75),
            models.Plant(name="Aptar Charleval", description="France Manufacturing", address="La Vente Cartier - RD 149 - route de Vascoeuil 27380 Charleval, Normandie France", plantConfidence=0.75),
            models.Plant(name="Aptar Chavanod - Reboul", description="France Manufacturing", address="31 rue Polaris 74650 Chavanod, Auvergne-Rhône-Alpes France", plantConfidence=0.75),
            models.Plant(name="Aptar Chieti", description="Italy Manufacturing", address="66020 San Giovanni Teatino, Chieti, Italy", plantConfidence=0.75),
            models.Plant(name="Aptar Chonburi", description="Thailand Manufacturing", address="20160 ตำบล บ้านเก่า, จ.ชลบุรี Thailand", plantConfidence=0.75),
            models.Plant(name="Aptar Congers", description="NY Manufacturing", address="250 North Route 303 10920 Congers, NY", plantConfidence=0.75),
            models.Plant(name="Aptar Dortmund", description="Germany Manufacturing", address="44319 Dortmund, NRW, Germany", plantConfidence=0.75),
            models.Plant(name="Aptar Eatontown", description="USA Manufacturing", address="611 Industrial Way West 07724 Eatontown, NJ", plantConfidence=0.75),
            models.Plant(name="Aptar Freyung", description="Germany Manufacturing", address="1 Löfflerstraße 94078 Freyung, BY Germany", plantConfidence=0.75),
            models.Plant(name="Aptar Granville", description="France Manufacturing", address="123 Rue du Conillot 50400 Granville, Normandie France", plantConfidence=0.75),
            models.Plant(name="Aptar Guangzhou", description="China Manufacturing", address="No.98 Fenghuang 8th Road Sino-Singapore Guangzhou Knowledge City Huangpu District Guangzhou, Guangdong 510700, China ", plantConfidence=0.75),
            models.Plant(name="Aptar Hyderabad", description="India Manufacturing", address="Aptar Pharma India Pvt. Ltd. Survey No 790, Kistapur, Village, Medchal, Hyderabad, Telangana 501401", plantConfidence=0.75),
            models.Plant(name="Aptar Jundiai", description="Brazil Manufacturing", address="151 Rua Gil Teixeira Lino SP Brazil", plantConfidence=0.75),
            models.Plant(name="Aptar Le Neubourg", description="France Manufacturing", address="Lieu-Dit Le Prieuré 56 avenue du Doyen Jussiaume 27110 Le Neubourg, Normandie France", plantConfidence=0.75),
            models.Plant(name="Aptar Le Vaudreuil", description="France Manufacturing", address="Route des Falaises 27100 Le Vaudreuil, Normandie France", plantConfidence=0.75),
            models.Plant(name="Aptar Leeds", description="United Kingdom Manufacturing", address="LS27 0SS Morley, England, United Kingdom", plantConfidence=0.75),
            models.Plant(name="Aptar Lincolton", description="USA Manufacturing", address="3300 Finger Mill Road 28092 Lincolnton, NC", plantConfidence=0.75),
            models.Plant(name="Aptar Madrid", description="Spain Manufacturing", address="28806 Alcalá de Henares, MD, Spain", plantConfidence=0.75),
            models.Plant(name="Aptar Maringa", description="Spain Manufacturing", address="Rua Pioneira Maria Cavalcante Ruy 87065-090 PR Brazil", plantConfidence=0.75),
            models.Plant(name="Aptar Aptar McHenry", description="USA Manufacturing", address="4900 Prime Parkway 60050 McHenry, IL", plantConfidence=0.75),
            models.Plant(name="Aptar Menden", description="Germany Manufacturing", address="15-21 Franz-Kissing-Straße 58706 Menden, NRW Germany", plantConfidence=0.75),
            models.Plant(name="Aptar Mezzovico", description="Switzerland Manufacturing", address="Via Cantonale 6805 Mezzovico-Vira, TI Switzerland", plantConfidence=0.75),
            models.Plant(name="Aptar Midland", description="USA Manufacturing", address="2202 Ridgewood Drive 48642 Midland, MI", plantConfidence=0.75),
            models.Plant(name="Aptar Mukwonago", description="USA Manufacturing", address="711 Fox Street 53149 Mukwonago, WI", plantConfidence=0.75),
            models.Plant(name="Aptar Oyonnax", description="France Manufacturing", address="165 rue des Cherolles 01100 Oyonnax, Auvergne-Rhône-Alpes France", plantConfidence=0.75),
            models.Plant(name="Aptar Pescara", description="Italy Manufacturing", address="65024, Manoppello Scalo,Pescara, Italy", plantConfidence=0.75),
            models.Plant(name="Aptar Poincy", description="France Manufacturing", address="44 Avenue de Meaux 77470 Poincy, IDF France", plantConfidence=0.75),
            models.Plant(name="Aptar Querétaro", description="Mexico Manufacturing", address="33 Circuito el Marqués Norte 76246 Santiago de Querétaro, Qro. Mexico", plantConfidence=0.75),
            models.Plant(name="Aptar Radolfzell", description="Germany Manufacturing", address="4 Unter den Reben 78253 Eigeltingen, BW German", plantConfidence=0.75),
            models.Plant(name="Aptar Suzhou", description="China Manufacturing", address="No.2 Dongwang Road, Suzhou, Jiangsu, 215123, China", plantConfidence=0.75),
            models.Plant(name="Aptar Torello", description="Spain Manufacturing", address="Calle Gorg Negre 10 Poligono Industrial Puigba 08570 TORELLO, Barcelona, Spain", plantConfidence=0.75),
            models.Plant(name="Aptar Tortuguitas", description="Argentina Manufacturing", address="3867 Venezuela C1211 AAW, CABA Argentina", plantConfidence=0.75),
            models.Plant(name="Aptar Val-de-Reuil", description="France Manufacturing", address="Route des Falaises 27100 Val-de-Reuil, Normandie France", plantConfidence=0.75),
            models.Plant(name="Aptar Villingen", description="Germany Manufacturing", address="36 Auf Herdenen 78052 Villingen-Schwenningen, BW Germany", plantConfidence=0.75),
            models.Plant(name="Aptar Vladimir", description="Russian federation Manufacturing", address="ul. Mostostroevskaya 4 Vladimir, The Vladimir Area Russian Federation, 600033", plantConfidence=0.75),
            models.Plant(name="Aptar Weihai", description="China Manufacturing", address="Weihai, Shandong 264204, China", plantConfidence=0.75),

        ]
        db.add_all(plants)
        db.commit()
        print("Pre-populated plants table with initial data.")
    else:
        print("Plants table is already populated.")


def prepopulate_detection_types(db: Session):
    if db.query(models.DetectionType).count() == 0:
        detection_types = [
            models.DetectionType(name="PPE Detection", description="Detects PPE compliance", modelpath="./yolomodels/best_ppe.pt", task_name="run_ppe_detection"),
            models.DetectionType(name="Pallet Detection", description="Detects pallets in the area", modelpath="./yolomodels/best_pallet.pt", task_name="run_pallet_detection"),
            models.DetectionType(name="Proximity Detection", description="Detects proximity between forklift and person", modelpath="./yolomodels/forklift_best.pt", task_name="run_proximity_detection"),
        ]
        db.add_all(detection_types)
        db.commit()
        print("Pre-populated detection types table with initial data.")
    else:
        print("Detection types table is already populated.")

def init_db():
    db = SessionLocal()
    try:
        prepopulate_detection_types(db)
        prepopulate_plants(db)
    finally:
        db.close()


#models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Aptar Rest API",
    version="1.0.0",
    contact={
        "name": "Minase Mengistu, Mariama Serafim de Oliveira",
        "email": "minase.mengistu@abo.fi",
    },
    lifespan=lifespan,
)

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(zones.router)
app.include_router(plants.router)
app.include_router(cameras.router)
app.include_router(detection.router)
app.include_router(scenario.router)
app.include_router(assignees.router)
app.include_router(report.router)
