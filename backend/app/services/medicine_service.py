"""Medicine knowledge base: local seed data and search service.

The knowledge base contains educational summaries for common medicines.
Search first consults this local store; when nothing matches, the
Medicine Information Agent (via the Model Router) answers instead.
"""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models import Medicine

logger = get_logger("services.medicine")

_SEED_MEDICINES: list[dict] = [
    {
        "name": "Paracetamol",
        "generic_name": "Acetaminophen",
        "category": "Analgesic / Antipyretic",
        "purpose": "Relieves mild to moderate pain (headache, toothache, muscle pain) and reduces fever.",
        "uses": "Common cold, fever, headache, minor aches and pains.",
        "dosage": "Adults: 500–1000 mg every 4–6 hours as needed, max 4000 mg/day. Children: follow doctor guidance.",
        "warnings": "Do not exceed the maximum daily dose; liver damage risk with overdose or with alcohol.",
        "side_effects": "Usually well tolerated. Rare: rash, nausea, allergic reactions.",
        "interactions": "Alcohol, warfarin (increases bleeding risk with long-term use).",
        "storage": "Store below 25°C, away from moisture and direct light.",
        "notes": "Do not combine multiple products containing paracetamol.",
    },
    {
        "name": "Ibuprofen",
        "generic_name": "Ibuprofen",
        "category": "NSAID",
        "purpose": "Reduces pain, inflammation and fever.",
        "uses": "Inflammation, joint pain, headache, toothache, period pain, fever.",
        "dosage": "Adults: 200–400 mg every 6–8 hours with food, max 1200 mg/day without a doctor.",
        "warnings": "Avoid in stomach ulcers, kidney disease, asthma triggered by NSAIDs, pregnancy (3rd trimester).",
        "side_effects": "Stomach upset, heartburn, nausea; long-term use may affect kidneys.",
        "interactions": "Aspirin, blood thinners, other NSAIDs, corticosteroids, some blood pressure medicines.",
        "storage": "Store below 25°C in a dry place.",
        "notes": "Take with food or milk to reduce stomach irritation.",
    },
    {
        "name": "Amoxicillin",
        "generic_name": "Amoxicillin",
        "category": "Antibiotic (Penicillin)",
        "purpose": "Treats bacterial infections such as ear, throat, chest and urinary infections.",
        "uses": "Bacterial infections only; does not work for viral infections.",
        "dosage": "Usually 250–500 mg every 8 hours or as prescribed. Complete the full course.",
        "warnings": "Allergy risk in penicillin-sensitive patients; use only with a prescription.",
        "side_effects": "Diarrhea, nausea, rash; serious: severe allergic reaction, difficulty breathing.",
        "interactions": "Allopurinol, methotrexate, oral contraceptives may be less effective.",
        "storage": "Store below 25°C, protect from moisture.",
        "notes": "Antibiotics must always be prescribed by a healthcare professional.",
    },
    {
        "name": "Metformin",
        "generic_name": "Metformin Hydrochloride",
        "category": "Antidiabetic (Biguanide)",
        "purpose": "Controls blood sugar levels in type 2 diabetes.",
        "uses": "Type 2 diabetes management, often first-line therapy.",
        "dosage": "Typically 500 mg with meals, titrated by the doctor up to 2000 mg/day.",
        "warnings": "Risk of lactic acidosis in kidney/liver disease, dehydration, or heavy alcohol use.",
        "side_effects": "Nausea, diarrhea, metallic taste at start of treatment.",
        "interactions": "Alcohol, iodinated contrast agents, certain diuretics.",
        "storage": "Store below 25°C, away from moisture.",
        "notes": "Take with meals; monitor blood glucose as advised by your doctor.",
    },
    {
        "name": "Omeprazole",
        "generic_name": "Omeprazole",
        "category": "Proton Pump Inhibitor (PPI)",
        "purpose": "Reduces stomach acid; treats heartburn, acid reflux and stomach ulcers.",
        "uses": "GERD, reflux, gastritis, peptic ulcer, prevention of NSAID-related ulcers.",
        "dosage": "Adults: 20 mg once daily before breakfast, typically for 2–8 weeks.",
        "warnings": "Long-term use may affect vitamin B12 and magnesium levels; increased fracture risk.",
        "side_effects": "Headache, nausea, diarrhea, constipation, flatulence.",
        "interactions": "Clopidogrel (reduced effect), methotrexate, some antifungals, digoxin.",
        "storage": "Store below 25°C in the original packaging.",
        "notes": "Best taken 30–60 minutes before a meal.",
    },
    {
        "name": "Cetirizine",
        "generic_name": "Cetirizine Hydrochloride",
        "category": "Antihistamine",
        "purpose": "Relieves allergy symptoms: sneezing, runny nose, itchy or watery eyes.",
        "uses": "Hay fever, allergic rhinitis, hives.",
        "dosage": "Adults and children over 12: 10 mg once daily.",
        "warnings": "May cause drowsiness in some people; avoid alcohol.",
        "side_effects": "Drowsiness, dry mouth, headache, fatigue.",
        "interactions": "Alcohol, sedatives, other antihistamines.",
        "storage": "Store below 25°C in a dry place.",
        "notes": "Avoid driving if you feel drowsy after taking it.",
    },
    {
        "name": "Aspirin",
        "generic_name": "Acetylsalicylic Acid",
        "category": "NSAID / Antiplatelet",
        "purpose": "Relieves pain, fever and inflammation; low dose reduces clot risk.",
        "uses": "Pain, fever, inflammation; low-dose (75–100 mg) for cardiovascular protection under doctor supervision.",
        "dosage": "Pain: 300–900 mg every 4–6 hours; cardiac doses only as prescribed.",
        "warnings": "Do not give to children (Reye's syndrome risk); avoid with bleeding disorders, ulcers, pregnancy.",
        "side_effects": "Stomach irritation, bleeding, bruising, heartburn.",
        "interactions": "Blood thinners, ibuprofen (reduces aspirin's antiplatelet effect), corticosteroids.",
        "storage": "Store below 25°C, away from moisture.",
        "notes": "Low-dose aspirin for heart protection must be directed by a doctor.",
    },
    {
        "name": "Losartan",
        "generic_name": "Losartan Potassium",
        "category": "ARB (Blood Pressure)",
        "purpose": "Lowers blood pressure and protects the kidneys in diabetes.",
        "uses": "Hypertension, heart failure, diabetic kidney disease.",
        "dosage": "Typically 50 mg once daily, adjusted by the doctor.",
        "warnings": "Not recommended in pregnancy; caution with kidney disease and high potassium.",
        "side_effects": "Dizziness, fatigue, cough (less common than ACE inhibitors), hyperkalemia.",
        "interactions": "Potassium supplements, potassium-sparing diuretics, NSAIDs, lithium.",
        "storage": "Store below 25°C in a dry place.",
        "notes": "Do not stop suddenly without medical advice.",
    },
    {
        "name": "Salbutamol",
        "generic_name": "Albuterol",
        "category": "Bronchodilator",
        "purpose": "Relieves wheezing and breathlessness in asthma and COPD.",
        "uses": "Asthma attack relief, exercise-induced bronchospasm, COPD.",
        "dosage": "Inhaler: usually 1–2 puffs as needed; see doctor for regular use.",
        "warnings": "If relief lasts under 3 hours or symptoms worsen, seek medical help immediately.",
        "side_effects": "Tremor, palpitations, headache, throat irritation.",
        "interactions": "Beta-blockers, some diuretics and antidepressants.",
        "storage": "Store the inhaler upright below 30°C.",
        "notes": "Difficulty breathing that does not improve is an emergency - call for help.",
    },
    {
        "name": "Vitamin D3",
        "generic_name": "Cholecalciferol",
        "category": "Vitamin Supplement",
        "purpose": "Maintains healthy bones, teeth, muscles and immune function.",
        "uses": "Vitamin D deficiency, osteoporosis support, general wellness.",
        "dosage": "Maintenance: 400–1000 IU daily; deficiency doses per doctor (often 50,000 IU weekly short term).",
        "warnings": "Very high doses can cause calcium toxicity; check levels before high-dose use.",
        "side_effects": "Generally well tolerated; excess may cause nausea, constipation, kidney stones.",
        "interactions": "Some antacids, thiazide diuretics, corticosteroids.",
        "storage": "Store below 25°C, away from light and moisture.",
        "notes": "Best absorbed with a meal containing fat.",
    },
]

DISCLAIMER = (
    "This information is for educational purposes only and is not a substitute "
    "for professional medical advice, diagnosis, or treatment. Never start, stop, "
    "or change a medication without consulting a doctor or pharmacist."
)


def seed_medicines(db: Session) -> int:
    """Insert the knowledge base into the database if empty; returns rows added."""
    existing = db.query(Medicine).count()
    if existing > 0:
        return 0
    rows = [Medicine(**item) for item in _SEED_MEDICINES]
    db.add_all(rows)
    db.commit()
    logger.info("Seeded %d medicines into the knowledge base", len(rows))
    return len(rows)


def search_knowledge_base(db: Session, query: str, limit: int = 5) -> list[Medicine]:
    """Full-text-ish search over the medicine knowledge base."""
    term = f"%{query.strip().lower()}%"
    return (
        db.query(Medicine)
        .filter(
            or_(
                Medicine.name.ilike(term),
                Medicine.generic_name.ilike(term),
                Medicine.category.ilike(term),
                Medicine.uses.ilike(term),
            )
        )
        .limit(limit)
        .all()
    )
