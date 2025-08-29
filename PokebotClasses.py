import random
from counterFile import get_new_id

class Pokemon:

    Natures = {
        "Adamant": ("att", "spatt"),
        "Bashful": (None, None),   # Neutral
        "Bold": ("defe", "att"),
        "Brave": ("att", "spe"),
        "Calm": ("spdef", "att"),
        "Careful": ("spdef", "spatt"),
        "Docile": (None, None),    # Neutral
        "Gentle": ("spdef", "defe"),
        "Hardy": (None, None),     # Neutral
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
        "Quirky": (None, None),    # Neutral
        "Rash": ("spatt", "spdef"),
        "Relaxed": ("defe", "spe"),
        "Sassy": ("spdef", "spe"),
        "Serious": (None, None),   # Neutral
        "Timid": ("spe", "att"),
    }
    
    BaseStats = {
        "1": [(45, 49, 49, 65, 65, 45), ["Overgrow", "Chlorophyll"], ["Grass","Poison"], ["Bulbasaur"]],
        "4": [(39, 52, 43, 60, 50, 65), ["Blaze","Solar Power"], ["Fire"], ["Charmander"]],
        "7": [(44, 48, 65, 50, 64, 43), ["Torrent", "Rain Dish"], ["Water"], ["Squirtle"]],
        "395": [(84, 86, 88, 111, 101, 60), ["Torrent", "Defiant"], ["Water", "Steel"], ["Empoleon"]],
        "1713": [(66, 75, 90, 120, 85, 105), ["Sniper", "Guts"] ,["Grass","Fire"], ["Chuyinator"]]
    }
    #395 es empoleon y el 1713 está inventado jajaja

    def __init__(self, id, name=None, level=1, marksOwned=None, friendLevel=50):
        self.id = str(id)
        self.name = name if name else Pokemon.BaseStats[self.id][3][0]
        self.level = level
        self.nature = random.choice(list(Pokemon.Natures.keys()))
        self.marksOwned = marksOwned
        self.isShiny = Pokemon.genShiny()
        self.friendLevel = friendLevel
        self.EVs = EVs()
        self.IVs = IVs()
        self.hp = self.checkStat(self.id, level, "hp")
        self.att = self.checkStat(self.id, level, "att")
        self.defe = self.checkStat(self.id, level, "defe")
        self.spatt = self.checkStat(self.id, level, "spatt")
        self.spdef = self.checkStat(self.id, level, "spdef")
        self.spe = self.checkStat(self.id, level, "spe")
        self.ability = random.choice(Pokemon.BaseStats[self.id][1])
        self.stats = self.checkStats(self.id, level)

    def bathe(self):
        self.friendLevel += 10 
    
    @staticmethod
    def genShiny():
        return random.randint(1, 4096) == 4096

    def changeNature(self, nature):
        self.nature = nature

    def EVTrain(self, EV, band):
        self.EVs.EVTrain(EV, band)

    def Hypertrain(self, stat):
        if stat == "gold":
            for s in ["hp","att","spatt","defe","spdef","spe"]:
                self.IVs.Hypertrain(s)
        else:
            self.IVs.Hypertrain(stat)

    def nature_multiplier(self, stat):
        inc, dec = Pokemon.Natures[self.nature]
        if stat == inc:
            return 1.1
        elif stat == dec:
            return 0.9
        return 1.0

    def changeAbility(self, ability):
        self.ability = ability

    def checkStats(self, ID, level):
        return {
            "hp": int(self.checkStat(ID, level, "hp")),
            "att": int(self.checkStat(ID, level,"att")),
            "defe": int(self.checkStat(ID, level,"defe")),
            "spatt": int(self.checkStat(ID, level,"spatt")),
            "spdef": int(self.checkStat(ID, level,"spdef")),
            "spe": int(self.checkStat(ID, level,"spe")),
        }

    def checkStat(self, ID, level, stat):
        base = Pokemon.BaseStats[ID][0]
        if stat == "hp":
            bhp = base[0]
            return ((2*bhp + self.IVs.checkStat("hp") + self.EVs.checkStat("hp")//4) * level)//100 + level + 10
        elif stat == "att":
            batt = base[1]
            return int((((2*batt + self.IVs.checkStat("att") + self.EVs.checkStat("att")//4) * level)//100 + 5) * self.nature_multiplier("att"))
        elif stat == "defe":
            bdefe = base[2]
            return int((((2*bdefe + self.IVs.checkStat("defe") + self.EVs.checkStat("defe")//4) * level)//100 + 5) * self.nature_multiplier("defe"))
        elif stat == "spatt":
            bspatt = base[3]
            return int((((2*bspatt + self.IVs.checkStat("spatt") + self.EVs.checkStat("spatt")//4) * level)//100 + 5) * self.nature_multiplier("spatt"))
        elif stat == "spdef":
            bspdef = base[4]
            return int((((2*bspdef + self.IVs.checkStat("spdef") + self.EVs.checkStat("spdef")//4) * level)//100 + 5) * self.nature_multiplier("spdef"))
        elif stat == "spe":
            bspe = base[5]
            return int((((2*bspe + self.IVs.checkStat("spe") + self.EVs.checkStat("spe")//4) * level)//100 + 5) * self.nature_multiplier("spe"))
        else:
            raise ValueError("Invalid stat name")

    def __repr__(self):
        return f"<Pokemon {self.name} (Lvl {self.level}) | Nature={self.nature}, Shiny={self.isShiny}>"

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
        setattr(self, EV, getattr(self, EV) + value)
        if getattr(self, EV) > 252:
            setattr(self, EV, 252)
    
    def EVTrain(self, EV, band):
        if band:
            self.addEV(EV, 8)
        self.addEV(EV, 2)

    def checkStat(self, EV):
        return getattr(self, EV)

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

class Move:
    def __init__(self, name, pp, type, pow, attType, hrate, effects, effrate):
        self.name = name
        self.pp = pp
        self.type = type
        self.pow = pow
        self.attType = attType
        self.hrate = hrate # percentage
        self.effects = effects # list
        self.effrate = effrate # percentage

class Marks:
    def __init__(self, champion, gourmet, friend, small):
        self.champion = champion
        self.gourmet = gourmet
        self.friend = friend
        self.small = small

class Trainer:
    def __init__(self):
        self.UID = get_new_id()
        self.slot1 = Trainer.genRandomStarter()
        self.slot2 = None
        self.slot3 = None
        self.slot4 = None
        self.slot5 = None
        self.slot6 = None
        self.box = []

    @staticmethod
    def genRandomStarter():
        return Pokemon(str(1 + random.randint(0,2)*3))
            
    def equipPokemon(self, slot, pokemon):
        setattr(self, slot, pokemon)
