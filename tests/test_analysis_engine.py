from services.analysis_engine import AnalysisEngine

engine = AnalysisEngine()

result = engine.analyze("AAPL")

print("\n")
print("=" * 80)
print("COMPANY")
print("=" * 80)
print(result["company"])

print("\n")
print("=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print(result["recommendation"])

print("\n")
print("=" * 80)
print("FUNDAMENTAL")
print("=" * 80)
print(result["fundamental"])

print("\n")
print("=" * 80)
print("TECHNICAL")
print("=" * 80)
print(result["technical"])