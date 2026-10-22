from services.analysis_router import AnalysisRouter

router = AnalysisRouter()

queries = [

    "Analyze Apple",

    "Should I buy Tesla?",

    "Microsoft earnings",

    "AMD",

    "Analyze Netflix"

]

for query in queries:

    print("=" * 80)
    print(query)
    print("=" * 80)

    result = router.process(query)

    print(result)