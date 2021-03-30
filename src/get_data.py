from database import convert_table_in_list, get_table, get_table_column_names


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


def get_data(exams, refraction, connect, list_test_id, refraction_id_with_nan):
    (
        list_of_final_exam,
        list_of_subj_exam,
        list_of_obj_exam,
        list_of_comp_exam,
        list_of_intake_exam,
        list_of_lm_exam,
        number_of_removed_exam,
    ) = ([], [], [], [], [], [], 0)
    for some_id, exam in exams.iterrows():
        if exam["patient_uid"] not in list_test_id:
            if (
                (exam["subj_id"] not in refraction_id_with_nan)
                and (exam["final_id"] not in refraction_id_with_nan)
                and (exam["lm_id"] not in refraction_id_with_nan)
                and (exam["obj_id"] not in refraction_id_with_nan)
                and (exam["compvision_id"] is not None)
            ):

                list_of_final_exam.append(exam["final_id"])
                list_of_subj_exam.append(exam["subj_id"])
                list_of_obj_exam.append(exam["obj_id"])
                list_of_lm_exam.append(exam["lm_id"])
                list_of_comp_exam.append(exam["compvision_id"])
                list_of_intake_exam.append(exam["intake_id"])
            else:
                number_of_removed_exam += 1
                print(
                    " {} was removed because RX WAS NONE: Subj ID = {} ,Final ID = {}, Date = {}".format(
                        exam["uid"],
                        exam["subj_id"],
                        exam["final_id"],
                        exam["arrived_time"],
                    )
                )
        else:
            number_of_removed_exam += 1
            print(
                " {} was removed because TEST PATIENT : Subj ID = {} ,Final ID = {}, Date = {}".format(
                    exam["uid"],
                    exam["subj_id"],
                    exam["final_id"],
                    exam["arrived_time"],
                )
            )
    ## Get the relevant table
    compvision = convert_table_in_list(
        get_table(connect, "complementaryvision"),
        get_table_column_names(connect, "complementaryvision"),
    )
    intake = convert_table_in_list(
        get_table(connect, "patientintakes"),
        get_table_column_names(connect, "patientintakes"),
    )
    ## Get the list of subjective and final refraction
    subjective = refraction[refraction["id"].isin(list_of_subj_exam)]
    final = refraction[refraction["id"].isin(list_of_final_exam)]
    objective = refraction[refraction["id"].isin(list_of_obj_exam)]
    lm = refraction[refraction["id"].isin(list_of_lm_exam)]
    compvision = compvision[compvision["id"].isin(list_of_comp_exam)]
    intake = intake[intake["id"].isin(list_of_intake_exam)]
    return (
        lm,
        objective,
        subjective,
        final,
        compvision,
        intake,
        number_of_removed_exam,
    )
