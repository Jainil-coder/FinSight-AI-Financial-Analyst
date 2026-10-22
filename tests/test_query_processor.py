from services.query_processor import QueryProcessor

processor = QueryProcessor()

tests = [

    "Analyze Apple",

    "Should I buy NVIDIA?",

    "Compare Apple and Microsoft",

    "Show Tesla chart",

    "Tesla earnings",

    "Latest AMD news"

]

for query in tests:

    print("=" * 50)

    print(query)

    print(processor.process(query))