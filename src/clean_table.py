def get_list_of_patient_test(patients):
    return patients[
        patients["lastname"].isin(["Test", "test", "Test ", "test "])
    ]


def get_list_of_nan_refraction(refraction, column_to_check):
    refraction_with_nan = []
    for index, row in refraction.iterrows():
        is_nan_series = (row[column_to_check] is None) or (
            row[column_to_check] == ""
        )
        if is_nan_series:
            refraction_with_nan.append(row["id"])
    return refraction_with_nan
