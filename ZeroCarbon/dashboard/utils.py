def calculate_food_carbon(quantity_kg, emission_factor):
    return quantity_kg * emission_factor


def calculate_electricity_carbon(units):
    return units * 0.82

def calculate_travel_carbon(distance, mode):
    factors = {
        'car': 0.21,
        'bus': 0.05,
        'train': 0.03,
        'flight': 0.15
    }
    return distance * factors.get(mode, 0.1)

def calculate_waste_carbon(quantity):
    return quantity * 1.2
