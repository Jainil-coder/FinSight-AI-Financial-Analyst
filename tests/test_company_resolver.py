from services.company_resolver import CompanyResolver



resolver = CompanyResolver()



tests = [

    "Analyze Apple",

    "Should I buy NVIDIA?",

    "Tesla earnings",

    "Microsoft stock performance",

    "AAPL"

]


for test in tests:


    result = resolver.resolve(test)


    print("\nINPUT:")

    print(test)


    print("RESULT:")

    print(result)