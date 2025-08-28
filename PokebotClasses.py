import random
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
    "395": [(84, 86, 88, 111, 101, 60), ["Torrent", "Defiant"], ["Water", "Steel"]],
    "1713": [(66, 75, 90, 120, 85, 105), ["Sniper", "Guts"] ,["Grass","Fire"]]

    }
    #395 es empoleon y el 1713 está inventado jajaja

    def __init__(self, name, level, id, nature, marksOwned, isShiny, friendLevel, EVs, IVs):
        self.name = name
        self.level = level
        self.id = id
        self.nature = nature
        self.marksOwned = marksOwned
        self.isShiny = isShiny
        self.friendLevel = friendLevel
        self.EVs = EVs
        self.IVs = IVs
        self.hp = self.checkStat(id, level, "hp")
        self.att = self.checkStat(id, level, "att")
        self.defe = self.checkStat(id, level, "defe")
        self.spatt = self.checkStat(id, level, "spatt")
        self.spdef = self.checkStat(id, level, "spdef")
        self.spe = self.checkStat(id, level, "spe")
        self.ability = Pokemon.BaseStats[id][1][random.randint(0,1)]
        self.stats = self.checkStats(id,level)
    def bathe(self):
        self.friendLevel += 10
    def changeNature(self, nature):
        self.nature = nature
    def EVTrain(self, EV, band):
        self.EVs.EVTrain(EV, band)
    def Hypertrain(self, stat):
        if stat == "gold":
            self.IVs.Hypertrain("hp")
            self.IVs.Hypertrain("att")
            self.IVs.Hypertrain("spatt")
            self.IVs.Hypertrain("defe")
            self.IVs.Hypertrain("spdef")
            self.IVs.Hypertrain("spe")
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
        hp = self.checkStat(ID, level, "hp")
        att = self.checkStat(ID, level,"att")
        defe = self.checkStat(ID, level,"defe")
        spatt = self.checkStat(ID, level,"spatt")
        spdef = self.checkStat(ID, level,"spdef")
        spe = self.checkStat(ID, level,"spe")

        return {
        "hp": int(hp),
        "att": int(att),
        "defe": int(defe),
        "spatt": int(spatt),
        "spdef": int(spdef),
        "spe": int(spe),
    }
    def checkStat(self, ID, level, stat):
        if stat == "hp":
            bhp = Pokemon.BaseStats[ID][0][0]
            return ((2*bhp + self.IVs.checkStat("hp") + self.EVs.checkStat("hp")//4)* level)//100 + level + 10
        elif stat == "att":
            batt = Pokemon.BaseStats[ID][0][1]
            return (((2*batt + self.IVs.checkStat("att") + self.EVs.checkStat("att")//4)* level)//100 + 5) * self.nature_multiplier("att")
        elif stat == "defe":
            bdefe = Pokemon.BaseStats[ID][0][2]
            return (((2*bdefe + self.IVs.checkStat("defe") + self.EVs.checkStat("defe")//4)* level)//100 + 5) * self.nature_multiplier("defe")
        elif stat == "spatt":
            bspatt = Pokemon.BaseStats[ID][0][3]
            return (((2*bspatt + self.IVs.checkStat("spatt") + self.EVs.checkStat("spatt")//4)* level)//100 + 5) * self.nature_multiplier("spatt")
        elif stat == "spdef":
            bspdef = Pokemon.BaseStats[ID][0][4]
            return (((2*bspdef + self.IVs.checkStat("spdef") + self.EVs.checkStat("spdef")//4)* level)//100 + 5) * self.nature_multiplier("spdef")
        elif stat == "spe":
            bspe = Pokemon.BaseStats[ID][0][5]
            return (((2*bspe + self.IVs.checkStat("spe") + self.EVs.checkStat("spe")//4)* level)//100 + 5) * self.nature_multiplier("spe")
        else:
            print("Algo salió mal :(")

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
        setattr(self, EV, getattr(self,EV) + value)
        if getattr(self,EV) > 252:
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

""""NO ACABADAS UWU"""
class Move:
    def __init__(self, name, pp, type, pow, attType, hrate, effects, effrate):
        self.name = name
        self.pp = pp
        self.type = type
        self.pow = pow
        self.attType = attType
        self.hrate = hrate #percentage
        self.effects = effects #1 or more
        self.effrate = effrate #percentage
    
class Marks:
    def __init__(self, champion, gourmet, friend, small):
        self.champion = champion
        self.gourmet = gourmet
        self.friend = friend
        self.small = small