import random


first = ["Extreme", "Automated", "Beta", "Quarantined", "Prohibited", "Essential", "Radical", "Dynamic", "Temporary",
         "Prime", "Mechanized", "Secondary", "Sentient", "Exceptional", "Sapient", "Reactionary", "Bionic",
         "Self-Regulating", "Sensitive", "Adept", "Expert", "Universal", "Highpowered"]

second = ["Medical", "Encoding", "Useless", "Engineering", "Emergency", "Planetary Surveillance", "Construction",
          "Emulation", "Probe", "Surveying", "War", "Peace Keeping", "Exploration", "Life Breather", "Recording",
          "Protector Of Humanity", "War Domination", "Planetary Annihilation", "Data Collection"]

last = ["Automaton", "Droid", "Algorithm", "Device", "Robot", "Bot", "Technology", "Golem", "Life Form", "Technician",
        "Juggernaut", "Program", "Application", "Machine"]

def newName():
    """
    return randomly generated name
    :return: String.
    """
    name = ""
    name += random.choice(first) + " "
    name += random.choice(second) + " "
    name += random.choice(last)
    return name