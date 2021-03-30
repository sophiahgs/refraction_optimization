from database import *
from get_data import *
from dr_rules import apply_sph_rules
from dr_rules import apply_cyl_rules
from dr_rules import apply_axis_rules
from dr_rules import apply_all_rules
from dr_rules import multivariate_model
from analyse_data import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pingouin as pg

## Connect to the DB
connect = get_database()

### -------------- CLEAN DATA : Get the list of patient test & no complete data
print("--- Get Clean data...")
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
refraction_id_with_nan = get_list_of_nan_refraction(refraction, "l_sph")
print(
    ".... {} rows of refraction or approx {} exams  was removed because of NaN value on l_sph".format(
        len(refraction_id_with_nan), len(refraction_id_with_nan) / 4
    )
)

### -------------- Select refraction Value
print("--- Let's get data")
## Get the list of relevant name of column ID
exams = convert_table_in_list(
    get_table(connect, "exams"),
    get_table_column_names(connect, "exams"),
)
(
    lm,
    objective,
    subjective,
    final,
    compvision,
    intake,
    number_of_removed_exam,
) = get_data(exams, refraction, connect, list_test_id, refraction_id_with_nan)
print(
    "... {} exams had been removed from the database since it was test patient".format(
        number_of_removed_exam
    )
)
close_connexion(connect)
## Add MSE j0 and J45 to refraction
subjective = add_mse_j0_j45(subjective)
final = add_mse_j0_j45(final)
objective = add_mse_j0_j45(objective)
lm = add_mse_j0_j45(lm)
print("... Add MSE j0 and J45 to refraction")

### -------------- View data
print("--- Analyze data")
print("... Plot refraction Data")
comp_rx_generate_figure(subjective, "subjective", final, "final")
comp_rx_generate_figure(objective, "objective", final, "final")
comp_rx_generate_figure(lm, "lensometer", final, "final")
comp_rx_generate_figure(objective, "objective", subjective, "subjective")
## View subjective and final colored with VA
# comp_rx_generate_figure(
#     subjective,
#     "subjective",
#     final,
#     "final",
#     [element for element in compvision["both_dva_out"].tolist()],
#     "va",
# )
## View subjective and final colored with VA & has glasses
# intake["has_glasses"] = intake["has_glasses"].replace(True, 1)
# intake["has_glasses"] = intake["has_glasses"].replace(False, -1)
# comp_rx_generate_figure(
#     subjective,
#     "subjective",
#     final,
#     "final",
#     [
#         a * b
#         for a, b in zip(
#             intake["has_glasses"].tolist(), compvision["both_dva_out"].tolist()
#         )
#     ],
#     "has glasses & va ?",
# )
print("... Compute Dr rules")
dr_rules_final = apply_all_rules(lm, subjective, final, compvision)
dr_rules_final = add_mse_j0_j45(dr_rules_final)
comp_rx_generate_figure(dr_rules_final, "dr_rules_final", final, "final")

print("... Try multivariate model rules")
Model = pd.DataFrame()
subjective = subjective.reset_index(drop=True)
intake = intake.reset_index(drop=True)
intake["has_glasses"] = intake["has_glasses"].replace(True, 0.5)
intake["has_glasses"] = intake["has_glasses"].replace(False, -0.5)
Model["subj_r_sph"] = subjective["r_sph"]
Model["subj_l_sph"] = subjective["l_sph"]
Model["has_glasses"] = intake["has_glasses"]
Model["va"] = compvision["both_dva_out"]
multivariate_model(
    final["r_sph"].reset_index(drop=True),
    Model.reset_index(drop=True),
    "r_sph",
)
