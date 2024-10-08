from sqlalchemy.orm import Session
from . import models

def prepopulate_plants(db: Session):
    
    france = "France Manufacturing"
    usa = "USA Manufacturing"
    germany = "Germany Manufacturing"
    china = "China Manufacturing"
    spain = "Spain Manufacturing"
    plants = [
            models.Plant(name="Aptar Annecy", description=france, address="19 Avenue 74000 Annecy,France", plantConfidence=75),
            models.Plant(name="Aptar Berazategui", description="Argentina Manufacturing", address="Colectora Autovía 2 El Pato, Argentina", plantConfidence=75),
            models.Plant(name="Aptar Brecey", description=france, address="Rue du Bocage 50370 Brécey, Normandie", plantConfidence=75),
            models.Plant(name="Aptar Cajamar", description="Colombia Manufacturing", address="2121 Avenida Doutor Antônio João Abdala, Colombia", plantConfidence=75),
            models.Plant(name="Aptar Cali", description="Colombia Manufacturing", address="6763537 Cantarrana, Valle del Cauca Colombia", plantConfidence=75),
            models.Plant(name="Aptar Camaçari", description="Brazil Manufacturing", address="13 2° Travessa Massaranduba, Brazil", plantConfidence=75),
            models.Plant(name="Aptar Cary", description=usa, address="1160 Silver Lake Road 60013 Cary, IL", plantConfidence=75),
            models.Plant(name="Aptar Charleval", description=france, address="27380 Charleval, Normandie France", plantConfidence=75),
            models.Plant(name="Aptar Chavanod - Reboul", description=france, address="74650 Chavanod, Auvergne-Rhône-Alpes France", plantConfidence=75),
            models.Plant(name="Aptar Chieti", description="Italy Manufacturing", address="66020 San Giovanni Teatino, Chieti, Italy", plantConfidence=75),
            models.Plant(name="Aptar Chonburi", description="Thailand Manufacturing", address="20160 Thailand", plantConfidence=75),
            models.Plant(name="Aptar Congers", description="NY Manufacturing", address="250 North Route 303 10920 Congers, NY", plantConfidence=75),
            models.Plant(name="Aptar Dortmund", description=germany, address="44319 Dortmund, NRW, Germany", plantConfidence=75),
            models.Plant(name="Aptar Eatontown", description=usa, address="611 Industrial Way West 07724 Eatontown, NJ", plantConfidence=75),
            models.Plant(name="Aptar Freyung", description=germany, address="1 Löfflerstraße 94078 Freyung, BY Germany", plantConfidence=75),
            models.Plant(name="Aptar Granville", description=france, address="50400 Granville, Normandie France", plantConfidence=75),
            models.Plant(name="Aptar Guangzhou", description=china, address="No.98 Fenghuang Guangdong 510700, China ", plantConfidence=75),
            models.Plant(name="Aptar Hyderabad", description="India Manufacturing", address="Aptar Pharma India Hyderabad, Telangana 501401", plantConfidence=75),
            models.Plant(name="Aptar Jundiai", description="Brazil Manufacturing", address="151 Rua Gil Teixeira Lino SP Brazil", plantConfidence=75),
            models.Plant(name="Aptar Le Neubourg", description=france, address="27110 Le Neubourg, Normandie France", plantConfidence=75),
            models.Plant(name="Aptar Le Vaudreuil", description=france, address="Route des Falaises 27100 Le Vaudreuil, Normandie France", plantConfidence=75),
            models.Plant(name="Aptar Leeds", description="United Kingdom Manufacturing", address="LS27 0SS Morley, England, United Kingdom", plantConfidence=75),
            models.Plant(name="Aptar Lincolton", description=usa, address="3300 Finger Mill Road 28092 Lincolnton, NC", plantConfidence=75),
            models.Plant(name="Aptar Madrid", description=spain, address="28806 Alcalá de Henares, MD, Spain", plantConfidence=75),
            models.Plant(name="Aptar Maringa", description=spain, address="87065-090 PR Brazil", plantConfidence=75),
            models.Plant(name="Aptar Aptar McHenry", description=usa, address="4900 Prime Parkway 60050 McHenry, IL", plantConfidence=75),
            models.Plant(name="Aptar Menden", description=germany, address="58706 Menden, NRW Germany", plantConfidence=75),
            models.Plant(name="Aptar Mezzovico", description="Switzerland Manufacturing", address="6805 Mezzovico-Vira, TI Switzerland", plantConfidence=75),
            models.Plant(name="Aptar Midland", description=usa, address="2202 Ridgewood Drive 48642 Midland, MI", plantConfidence=75),
            models.Plant(name="Aptar Mukwonago", description=usa, address="711 Fox Street 53149 Mukwonago, WI", plantConfidence=75),
            models.Plant(name="Aptar Oyonnax", description=france, address="01100 Oyonnax, Auvergne-Rhône-Alpes France", plantConfidence=75),
            models.Plant(name="Aptar Pescara", description="Italy Manufacturing", address="65024, Manoppello Scalo,Pescara, Italy", plantConfidence=75),
            models.Plant(name="Aptar Poincy", description=france, address="77470 Poincy, IDF France", plantConfidence=75),
            models.Plant(name="Aptar Querétaro", description="Mexico Manufacturing", address="76246 Santiago de Querétaro, Qro. Mexico", plantConfidence=75),
            models.Plant(name="Aptar Radolfzell", description=germany, address="78253 Eigeltingen, BW German", plantConfidence=75),
            models.Plant(name="Aptar Suzhou", description=china, address="Jiangsu, 215123, China", plantConfidence=75),
            models.Plant(name="Aptar Torello", description=spain, address="08570 TORELLO, Barcelona, Spain", plantConfidence=75),
            models.Plant(name="Aptar Tortuguitas", description="Argentina Manufacturing", address="3867 Venezuela C1211 AAW, CABA Argentina", plantConfidence=75),
            models.Plant(name="Aptar Val-de-Reuil", description=france, address="27100 Val-de-Reuil, Normandie France", plantConfidence=75),
            models.Plant(name="Aptar Villingen", description=germany, address="78052 Villingen-Schwenningen, BW Germany", plantConfidence=75),
            models.Plant(name="Aptar Vladimir", description="Russian federation Manufacturing", address="The Vladimir Area Russian Federation, 600033", plantConfidence=75),
            models.Plant(name="Aptar Weihai", description=china, address="Weihai, Shandong 264204, China", plantConfidence=75),
    ]
    for plant in plants:
        existing = db.query(models.Plant).filter_by(name=plant.name).first()

        if existing:
            existing.description = plant.description
            existing.address = plant.address
            existing.plantConfidence = plant.plantConfidence
            print(f"Updated plant: {plant.name}")
        else:
            db.add(plant)
            print(f"Inserted plant: {plant.name}")

    db.commit()
    print("Finished upserting plants.")

def prepopulate_detection_types(db: Session):
     
    detection_types = [
        models.DetectionType(name="PPE Detection", description="Detects PPE compliance", modelpath="./yolomodels/best_ppe.pt", task_name="app.ppetask.run_ppe_detection"),
        models.DetectionType(name="Pallet Detection", description="Detects pallets in the area", modelpath="./yolomodels/best_pallet.pt", task_name="app.palletstask.run_pallet_detection"),
        models.DetectionType(name="Proximity Detection", description="Detects proximity between forklift and person", modelpath="./yolomodels/forklift_best.pt", task_name="app.forklifttask.run_proximity_detection"),
    ]
    for detection_type in detection_types:
        existing = db.query(models.DetectionType).filter_by(name=detection_type.name).first()

        if existing:
            existing.description = detection_type.description
            existing.modelpath = detection_type.modelpath
            existing.task_name = detection_type.task_name
            print(f"Updated detection type: {detection_type.name}")
        else:
            db.add(detection_type)
            print(f"Inserted new detection type: {detection_type.name}")

    db.commit()
    print("Finished upserting detection types.")

def init_db(db: Session):
    prepopulate_detection_types(db)
    prepopulate_plants(db)
