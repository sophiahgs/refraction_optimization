from database import *
from clean_table import *
from dr_rules import apply_sph_rules
from dr_rules import apply_cyl_rules
from dr_rules import apply_axis_rules
from dr_rules import apply_all_rules
from analyse_data import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pingouin as pg

## Connect to the DB
connect = get_database()

### -------------- CLEAN DATA : Get the list of patient test & no complete data
print("Get Clean data...")
## Get the list of patient Test
patients = convert_table_in_list(
    get_table(connect, "patients"),
    get_table_column_names(connect, "patients"),
)
list_test_id = get_list_of_patient_test(patients)["uid"].tolist()
print(
    ".... {} Patient hase been used for test : {}".format(
        len(list_test_id), list_test_id
    )
)

## Get the list of Nan refraction
refraction = convert_table_in_list(
    get_table(connect, "refractions"),
    get_table_column_names(connect, "refractions"),
)
compvision = convert_table_in_list(
    get_table(connect, "complementaryvision"),
    get_table_column_names(connect, "complementaryvision"),
)
refraction_id_with_nan = get_list_of_nan_refraction(refraction, "l_sph")
print(
    ".... {} rows of refraction or approx {} exams  was removed because of NaN value on l_sph".format(
        len(refraction_id_with_nan), len(refraction_id_with_nan) / 4
    )
)

### -------------- Select refraction Value
print("Let's get refraction ....")
## Get the list of relevant name of column ID
exams = convert_table_in_list(
    get_table(connect, "exams"),
    get_table_column_names(connect, "exams"),
)
(
    list_of_final_exam,
    list_of_subj_exam,
    list_of_obj_exam,
    list_of_comp_exam,
    list_of_lm_exam,
    number_of_removed_exam,
) = ([], [], [], [], [], 0)
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
            list_of_lm_exam.append(exam["obj_id"])
            list_of_comp_exam.append(exam["compvision_id"])
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
print(
    "{} exams had been removed from the database since it was test patient".format(
        number_of_removed_exam
    )
)
## Get the list of subjective and final refraction
subjective = refraction[refraction["id"].isin(list_of_subj_exam)]
final = refraction[refraction["id"].isin(list_of_final_exam)]
objectif = refraction[refraction["id"].isin(list_of_obj_exam)]
lm = refraction[refraction["id"].isin(list_of_lm_exam)]
compvision = compvision[compvision["id"].isin(list_of_comp_exam)]


### Plot
print("Let's plot data")
comp_rx_generate_figure(subjective, "subjective", final, "final")
comp_rx_generate_figure(objectif, "objective", final, "final")
comp_rx_generate_figure(lm, "lensometer", final, "final")
comp_rx_generate_figure(objectif, "objective", subjective, "subjective")

close_connexion(connect)
dr_rules_final = apply_all_rules(lm, subjective, final, compvision)
print(dr_rules_final)
comp_rx_generate_figure(dr_rules_final, "dr_rules_final", final, "final")
# stat = pd.DataFrame()
