import pandas as pd


def normal_round(n: float):
    if n % 0.25 != 0:
        if n > 0:
            return ((n // 0.25) + 1) * 0.25
        if n < 0:
            return ((n // 0.25)) * 0.25
    return n


def apply_sph_rules(lm_sph: float, sub_sph: float, va: int):
    # Button Sph  Adaptation
    # Compute ΔVA ex (VA:20/25 => ΔVA=5;20/30 => ΔVA=10 etc
    # If ΔVA !=0 then n=ΔVA/5 and final_sph = (1/n)*lm_sph + (1-1/n)*sub_sph
    # Around to |superior| mod(0.25)
    if va is None:
        return sub_sph
    delta_va = va - 20
    if delta_va != 0:
        print("delta_va != 0:")
        n = delta_va / 5 + 1
        return normal_round((1 / n) * lm_sph + (1 - (1 / n)) * sub_sph)
    return sub_sph


def apply_cyl_rules(lm_cyl: float, sub_cyl: float, final_sph: float):
    # Button Cyl Adaptation
    # 1. 	If lm_cyl + |lm_cyl-sub_cyl|/2<-0.75
    # then modified_cyl = lm_cyl+0.5 & round %0.25
    # else modified_cyl = lm_cyl+(abs(lm_cyl-D7)/2)) & round %0.25
    # 2. 	If |lm_cyl-sub_cyl|>=0.75
    #   then modified_sph = final_sph - 0.25
    #   else  modified_sph = final_sph
    # Rules N°1
    if sub_cyl != 0:
        if lm_cyl + abs(lm_cyl - sub_cyl) / 2 < -0.75:
            modified_cyl = normal_round(lm_cyl - 0.5)
        else:
            modified_cyl = normal_round(lm_cyl - abs(lm_cyl - sub_cyl) / 2)
        # Rules N°2
        if abs(lm_cyl - sub_cyl) >= 0.75:
            modified_sph = final_sph - 0.25
        else:
            modified_sph = final_sph
        return modified_sph, modified_cyl
    return final_sph, sub_cyl


def apply_axis_rules(lm_cyl: float, lm_axis: float, sub_axis: float):
    # Button Axis Adaptation
    # If lm_cyl  = 0 	then final_axis  = sub_axis
    # If lm_cyl [-0.25;-1.00[then final_axis = lm_axis*0.5 + sub_axis*0.5
    # If lm_cyl [-1.00;-2.00[then final_axis = lm_axis*0.33 + sub_axis*0.66
    # If lm_cyl     < -2.00  then final_axis = lm_axis*0.25 + sub_axis*0.75
    if lm_cyl == 0:
        return sub_axis
    if -0.25 <= lm_cyl < -1:
        return lm_axis * 1 / 2 + sub_axis * 1 / 2
    if -1.0 <= lm_cyl < -2.0:
        return round(lm_axis * 1 / 3 + sub_axis * 2 / 3)
    else:
        return round(lm_axis * 1 / 4 + sub_axis * 3 / 4)


def apply_all_rules(lm, subjective, final, compvision):
    dr_rules_final = pd.DataFrame()
    dr_rules_final_l_sph = []
    dr_rules_final_r_sph = []
    dr_rules_final_l_cyl = []
    dr_rules_final_r_cyl = []
    dr_rules_final_r_axis = []
    dr_rules_final_l_axis = []
    for i in range(0, len(lm.index)):
        ## SPHERICAL
        dr_rules_final_l_sph.append(
            apply_sph_rules(
                lm["l_sph"].tolist()[i],
                subjective["l_sph"].tolist()[i],
                compvision["both_dva_out"].tolist()[i],
            )
        )
        dr_rules_final_r_sph.append(
            apply_sph_rules(
                lm["r_sph"].tolist()[i],
                subjective["r_sph"].tolist()[i],
                compvision["both_dva_out"].tolist()[i],
            )
        )
        ## CYL
        l_sph, l_cyl = apply_cyl_rules(
            lm["l_cyl"].tolist()[i],
            subjective["l_cyl"].tolist()[i],
            dr_rules_final_l_sph[i],
        )
        dr_rules_final_l_cyl.append(l_cyl)
        dr_rules_final_l_sph[i] = l_sph
        r_sph, r_cyl = apply_cyl_rules(
            lm["r_cyl"].tolist()[i],
            subjective["r_cyl"].tolist()[i],
            dr_rules_final_r_sph[i],
        )
        dr_rules_final_r_cyl.append(r_cyl)
        dr_rules_final_r_sph[i] = r_sph
        ## AXIS
        dr_rules_final_l_axis.append(
            apply_axis_rules(
                lm["l_cyl"].tolist()[i],
                lm["l_axis"].tolist()[i],
                subjective["l_axis"].tolist()[i],
            )
        )
        dr_rules_final_r_axis.append(
            apply_axis_rules(
                lm["r_cyl"].tolist()[i],
                lm["r_axis"].tolist()[i],
                subjective["r_axis"].tolist()[i],
            )
        )
    dr_rules_final["l_sph"] = dr_rules_final_l_sph
    dr_rules_final["r_sph"] = dr_rules_final_r_sph
    dr_rules_final["l_cyl"] = dr_rules_final_l_cyl
    dr_rules_final["r_cyl"] = dr_rules_final_r_cyl
    dr_rules_final["l_axis"] = dr_rules_final_l_axis
    dr_rules_final["r_axis"] = dr_rules_final_r_axis

    return dr_rules_final
