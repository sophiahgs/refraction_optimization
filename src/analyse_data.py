import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pingouin as pg
import os
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error

refraction_parameter = [
    "l_sph",
    "l_cyl",
    "l_axis",
    "r_sph",
    "r_cyl",
    "r_axis",
]


def comp_rx_generate_figure(
    refraction1, refraction1_name, refraction2, refraction2_name
):
    path = "graph/{}_vs_{}".format(refraction1_name, refraction2_name)
    os.makedirs(path, exist_ok=True)
    for refraction_attribute in refraction_parameter:
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.scatter(
            refraction1[refraction_attribute],
            refraction2[refraction_attribute],
        )
        lims = [
            np.min([ax1.get_xlim(), ax1.get_ylim()]),  # min of both axes
            np.max([ax1.get_xlim(), ax1.get_ylim()]),  # max of both axes
        ]

        # now plot both limits against eachother
        ax1.plot(lims, lims, "k-", alpha=0.75, zorder=0)
        ax1.set_aspect("equal")
        ax1.set_ylabel(refraction1_name)
        ax1.set_xlabel(refraction2_name)
        ax1.title.set_text(refraction_attribute)
        ax2 = pg.plot_blandaltman(
            refraction2[refraction_attribute],
            refraction1[refraction_attribute],
            ax=ax2,
        )
        ax2.title.set_text("Bland & Altman " + refraction_attribute)

        fig.savefig(
            path
            + "/{}_vs_{}_{}.png".format(
                refraction1_name, refraction2_name, refraction_attribute
            )
        )


def get_refraction_parameters(exams, refraction_id_with_nan, list_test_id):
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
    return (
        list_of_final_exam,
        list_of_subj_exam,
        list_of_obj_exam,
        list_of_comp_exam,
        list_of_lm_exam,
    )
