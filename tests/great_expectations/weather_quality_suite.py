import great_expectations as gx

context = gx.get_context()

suite = context.create_expectation_suite("weather_quality")

#Expectation 1: Temperature is in valid range
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="temperature_c",
        min_value=-60,
        max_value=60
    )
)

#Expectation 2: No null cities
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="city"
    )
)

#Expectation 3: Exactly 3 cities in the dataset
suite.add_expectation(
    gx.expectations.ExpectColumnDistinctValuesToEqualSet(
        column="city",
        value_set={"Singapore", "Tokyo", "New York"}
    )
)

#Expectation 4: Daily record count (720 hours × 3 cities = 2160)
suite.add_expectation(
    gx.expectations.ExpectTableRowCountToEqual(
        value=2160
    )
)

#Expectation 5: No duplicate timestamps per city
suite.add_expectation(
    gx.expectations.ExpectCompoundColumnsToBeUnique(
        column_list=["city", "timestamp"]
    )
)