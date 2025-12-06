from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# In-memory "database"
items_db = {}
# Simple in-memory ID counter
counter_id = 1


class CreatureCreate(BaseModel):
    name: str
    mythology: str
    creature_type: str
    danger_level: int


class CreatureRead(BaseModel):
    id: int
    name: str
    mythology: str
    creature_type: str
    danger_level: int


# --- Service / business-logic functions ---


def create_creature(creature: CreatureCreate) -> CreatureRead:
    global counter_id
    creature_id = counter_id
    counter_id += 1

    creature_dict = {
        "id": creature_id,
        "name": creature.name,
        "mythology": creature.mythology,
        "creature_type": creature.creature_type,
        "danger_level": creature.danger_level,
    }
    items_db[creature_id] = creature_dict
    return CreatureRead(**creature_dict)


def list_creatures() -> list[CreatureRead]:
    return [CreatureRead(**creature_dict) for creature_dict in items_db.values()]


def update_creature(creature_id: int, creature: CreatureCreate) -> CreatureRead:
    if creature_id not in items_db:
        raise HTTPException(status_code=404, detail="Creature not found")

    creature_dict = {
        "id": creature_id,
        "name": creature.name,
        "mythology": creature.mythology,
        "creature_type": creature.creature_type,
        "danger_level": creature.danger_level,
    }
    items_db[creature_id] = creature_dict
    return CreatureRead(**creature_dict)


def delete_creature(creature_id: int) -> None:
    if creature_id not in items_db:
        raise HTTPException(status_code=404, detail="creature not found")

    del items_db[creature_id]


# --- API Endpoints ---


@app.post("/creatures/", response_model=CreatureRead)
def create_creature_endpoint(creature: CreatureCreate) -> CreatureRead:
    return create_creature(creature)


@app.get("/creatures/", response_model=list[CreatureRead])
def get_creatures_endpoint() -> list[CreatureRead]:
    return list_creatures()


@app.put("/creatures/{creature_id}", response_model=CreatureRead)
def update_creature_endpoint(
    creature_id: int, creature: CreatureCreate
) -> CreatureRead:
    return update_creature(creature_id, creature)


@app.delete("/creatures/{creature_id}")
def delete_creature_endpoint(creature_id: int) -> dict:
    delete_creature(creature_id)
    return {"detail": "creature deleted successfully"}
