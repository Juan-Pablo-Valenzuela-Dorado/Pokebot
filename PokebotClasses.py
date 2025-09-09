import random
import json
import uuid

# Load Pokémon database once
with open('kanto_pokedex.json', 'r', encoding='utf-8') as archivo:
    BaseStats = json.load(archivo)

# Natures
Natures = {
    "Adamant": ("att", "spatt"),
    "Bashful": (None, None),
    "Bold": ("defe", "att"),
    "Brave": ("att", "spe"),
    "Calm": ("spdef", "att"),
    "Careful": ("spdef", "spatt"),
    "Docile": (None, None),
    "Gentle": ("spdef", "defe"),
    "Hardy": (None, None),
    "Hasty": ("spe", "defe"),
    "Impish": ("defe", "spatt"),
    "Jolly": ("spe", "spatt"),
    "Lax": ("defe", "spdef"),
    "Lonely": ("att", "defe"),
    "Mild": ("spatt", "defe"),
    "Modest": ("spatt", "att"),
    "Naive": ("spe", "spdef"),
    "Naughty": ("att", "spdef"),
    "Quiet": ("spatt", "spe"),
    "Quirky": (None, None),
    "Rash": ("spatt", "spdef"),
    "Relaxed": ("defe", "spe"),
    "Sassy": ("spdef", "spe"),
    "Serious": (None, None),
    "Timid": ("spe", "att"),
}


# --- Helper classes ---
class EVs:
    def __init__(self):
        self.hp = 0
        self.att = 0
        self.spatt = 0
        self.defe = 0
        self.spdef = 0
        self.spe = 0

    def totalStats(self):
        return self.hp + self.att + self.spatt + self.defe + self.spdef + self.spe

    def addEV(self, EV, value):
        totalStats = self.totalStats()
        if totalStats + value > 510:
            value = 510 - totalStats
        setattr(self, EV, min(getattr(self, EV) + value, 252))

    def EVTrain(self, EV, band=False):
        if band:
            self.addEV(EV, 8)
        self.addEV(EV, 2)

    def checkStat(self, stat):
        return getattr(self, stat)


class IVs:
    def __init__(self):
        self.hp = random.randint(0, 31)
        self.att = random.randint(0, 31)
        self.spatt = random.randint(0, 31)
        self.defe = random.randint(0, 31)
        self.spdef = random.randint(0, 31)
        self.spe = random.randint(0, 31)

    def Hypertrain(self, stat):
        setattr(self, stat, 31)

    def checkStat(self, stat):
        return getattr(self, stat)


# --- Pokémon class ---
class Pokemon:
    BaseStats = BaseStats
    Natures = Natures

    def __init__(self, poke_id, name=None, level=1, friendLevel=50):
        self.id = str(poke_id).zfill(4)  # ensure padded ID
        if self.id not in Pokemon.BaseStats:
            raise ValueError(f"Pokemon ID {self.id} not found in BaseStats")

        data = Pokemon.BaseStats[self.id]
        self.name = name or data["name"]
        self.types = data["types"]
        self.base_stats = data["base_stats"]
        self.abilities = data["abilities"]
        self.moveset = data.get("moveset", {})

        self.level = level
        self.nature = random.choice(list(Pokemon.Natures.keys()))
        self.friendLevel = friendLevel
        self.isShiny = self.genShiny()

        self.EVs = EVs()
        self.IVs = IVs()

        # Stats calculation
        self.hp = self.checkStat("hp")
        self.att = self.checkStat("att")
        self.defe = self.checkStat("defe")
        self.spatt = self.checkStat("spatt")
        self.spdef = self.checkStat("spdef")
        self.spe = self.checkStat("spe")
        self.ability = random.choice(self.abilities)
        self.id = str(poke_id).zfill(4)  # species ID
        self.uid = str(uuid.uuid4())      # unique instance ID

    def genShiny(self):
        return random.randint(1, 4096) == 4096

    def nature_multiplier(self, stat):
        inc, dec = Pokemon.Natures[self.nature]
        if stat == inc:
            return 1.1
        elif stat == dec:
            return 0.9
        return 1.0

    def checkStat(self, stat):
        base = self.base_stats[stat]
        if stat == "hp":
            return ((2*base + self.IVs.checkStat("hp") + self.EVs.checkStat("hp")//4) * self.level)//100 + self.level + 10
        else:
            return int((((2*base + self.IVs.checkStat(stat) + self.EVs.checkStat(stat)//4) * self.level)//100 + 5) * self.nature_multiplier(stat))

    def __repr__(self):
        return f"<Pokemon {self.name} (Lvl {self.level}) | Nature={self.nature}, Shiny={self.isShiny}>"

    # Optional: save/load as dict for persistence
    def to_dict(self):
        return {
            "uid": self.uid,
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "nature": self.nature,
            "friendLevel": self.friendLevel,
            "isShiny": self.isShiny,
            "EVs": self.EVs.__dict__,
            "IVs": self.IVs.__dict__,
        }

    @classmethod
    def from_dict(cls, data):
        p = cls(data["id"], name=data.get("name"), level=data.get("level",1), friendLevel=data.get("friendLevel",50))
        p.uid = data.get("uid", str(uuid.uuid4()))
        p.nature = data.get("nature", p.nature)
        p.isShiny = data.get("isShiny", p.isShiny)
        p.EVs.__dict__.update(data.get("EVs", {}))
        p.IVs.__dict__.update(data.get("IVs", {}))
        return p



# --- Trainer class ---
class Trainer:
    def __init__(self, unique_id):
        self.UID = str(unique_id)
        self.slot1 = self.genRandomStarter()
        self.slot2 = None
        self.slot3 = None
        self.slot4 = None
        self.slot5 = None
        self.slot6 = None
        self.box = []

    @staticmethod
    def genRandomStarter():
        # List of starter Pokémon IDs (padded)
        starter_ids = ["0001", "0004", "0007"]
        return Pokemon(random.choice(starter_ids))

    def equipPokemon(self, slot, pokemon):
        setattr(self, slot, pokemon)

    # Persistence helpers
    def to_dict(self):
        return {
            "UID": self.UID,
            "slot1": self.slot1.to_dict() if self.slot1 else None,
            "slot2": self.slot2.to_dict() if self.slot2 else None,
            "slot3": self.slot3.to_dict() if self.slot3 else None,
            "slot4": self.slot4.to_dict() if self.slot4 else None,
            "slot5": self.slot5.to_dict() if self.slot5 else None,
            "slot6": self.slot6.to_dict() if self.slot6 else None,
            "box": [p.to_dict() for p in self.box],
        }

    @classmethod
    def from_dict(cls, data):
        t = cls(data["UID"])
        for i in range(1,7):
            slot_name = f"slot{i}"
            if data.get(slot_name):
                setattr(t, slot_name, Pokemon.from_dict(data[slot_name]))
        t.box = [Pokemon.from_dict(p) for p in data.get("box",[])]
        return t

    
    def slot_list(self):
        """Return a list of all Pokémon in slots 1-6 (ignores empty slots)."""
        return [getattr(self, f"slot{i}") for i in range(1, 7) if getattr(self, f"slot{i}")]

    def replace_pokemon(self, old_uid, new_pokemon):
        """Replace a Pokémon by UID in slots or box."""
        # Check slots
        for i in range(1, 7):
            slot = getattr(self, f"slot{i}")
            if slot and slot.uid == old_uid:
                setattr(self, f"slot{i}", new_pokemon)
                return
        # Check box
        for i, p in enumerate(self.box):
            if p.uid == old_uid:
                self.box[i] = new_pokemon
                return
