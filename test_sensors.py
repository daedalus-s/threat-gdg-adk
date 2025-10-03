from app.sensors.simulator import SensorSimulator

# Test normal scenario
sim = SensorSimulator("normal")
print("=== NORMAL SCENARIO ===")
print(sim.generate_batch())

# Test intrusion scenario
sim = SensorSimulator("intrusion")
print("\n=== INTRUSION SCENARIO ===")
print(sim.generate_batch())