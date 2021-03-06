"""
Export forces to sto
"""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import yaml
from pyosim import Conf
from pyosim import Analogs3dOsim

aws_conf = yaml.safe_load(open("../conf.yml"))
local_or_distant = "distant" if aws_conf["distant_id"]["enable"] else "local"

conf = Conf(project_path=aws_conf["path"]["project"][local_or_distant])
participants = conf.get_participants_to_process()

calibration_matrix = np.genfromtxt(
    conf.project_path / "forces_calibration_matrix.csv", delimiter=","
)
params = {
    "low_pass_cutoff": 30,
    "order": 4,
    "forces_labels": conf.get_conf_field(
        participant=participants[0], field=["analogs", "targets"]
    ),
}

for i, iparticipant in enumerate(participants[:]):
    print(f"\nparticipant #{i}: {iparticipant}")
    directories = conf.get_conf_field(
        participant=iparticipant, field=["analogs", "data"]
    )
    assigned = conf.get_conf_field(
        participant=iparticipant, field=["analogs", "assigned"]
    )

    for itrial in Path(directories[0]).glob("*.c3d"):
        # try participant's channel assignment
        for iassign in assigned:
            # get index where assignment are empty
            nan_idx = [i for i, v in enumerate(iassign) if not v]
            if nan_idx:
                iassign_without_nans = [i for i in iassign if i]
            else:
                iassign_without_nans = iassign

            try:
                forces = Analogs3dOsim.from_c3d(
                    itrial, names=iassign_without_nans, prefix=":"
                )
                # Analogs3dOsim.from_c3d(itrial).get_labels
                if nan_idx:
                    forces.get_nan_idx = np.array(nan_idx)
                    # if there is any empty assignment, fill the dimension with nan
                    for i in nan_idx:
                        forces = np.insert(forces, i, np.nan, axis=1)
                    print(f"\t{itrial.stem} (NaNs: {nan_idx})")
                else:
                    print(f"\t{itrial.stem}")

                # check if dimensions are ok
                if not forces.shape[1] == len(iassign):
                    raise ValueError("Wrong dimensions")
                break
            except ValueError:
                forces = []

        # check if there is empty frames
        nan_rows = np.isnan(forces).any(axis=1).ravel()
        print(
            f"\t\tremoving {nan_rows.sum()} nan frames (indices: {np.argwhere(nan_rows)})"
        )
        forces = forces[..., ~nan_rows]

        # processing (offset during the first second, calibration, low pass)
        forces = (
            forces.center(
                mu=np.nanmedian(forces[..., 10 : int(forces.get_rate)], axis=-1),
                axis=-1,
            )
            .squeeze()
            .T.matmul(calibration_matrix.T)
            .low_pass(
                freq=forces.get_rate,
                order=params["order"],
                cutoff=params["low_pass_cutoff"],
            )
            .dot(-1)
        )

        norm = Analogs3dOsim(forces[0, :3, :].norm(axis=0).reshape(1, 1, -1))
        idx = norm[0, 0, :].detect_onset(
            threshold=5, above=int(forces.get_rate) / 2, below=1000  # 5 Newtons
        )

        # Special cases
        if itrial.stem == "MarSF12H4_1":
            idx[0][1] = 11983
        if itrial.stem == "MarSF6H4_1":
            idx[0][1] = 10672
        if itrial.stem == "GatBH18H4_2":
            idx[0][1] = 17122
        if itrial.stem == "GatBH18H4_2":
            idx[0][1] = 17122
        if itrial.stem == "GatBH18H4_3":
            idx = np.array([[5271, 15965]])
        if itrial.stem == "CamBF12H5_3":
            continue
        if itrial.stem == "EveDF12H1_2":
            idx = np.array([[1229, 5549]])
        if itrial.stem == "SamNF12H5_2":
            idx = np.array([[3483, 14498]])
        if itrial.stem == "SamNF6H3_1":
            idx = np.array([[3698, 12314]])
        if itrial.stem == "AimQF12H3_1":
            idx = np.array([[4041, 10328]])
        if itrial.stem == "AleBH18H6_3":
            idx = np.array([[2279, 11058]])
        if itrial.stem == "AmiAF12H6_3":
            idx = np.array([[6146, 16873]])
        if itrial.stem == "CarBF12H6_3":
            idx = np.array([[1649, 10415]])
        if itrial.stem == "AnnSF6H2_3":
            continue
        if itrial.stem == "SteBF6H2_2":
            continue
        if itrial.stem == "SteBF6H3_1":
            idx = np.array([[2591, 8100]])
        if itrial.stem == "RoxDF6H6_1":
            idx = np.array([[2883, 9514]])
        if itrial.stem == "RoxDF6H6_2":
            idx = np.array([[2883, 9514]])
        if itrial.stem == "GeoAH12H1_2":
            idx = np.array([[1110, 7764]])
        if itrial.stem == "GeoAH12H2_1":
            idx = np.array([[1136, 9211]])
        if itrial.stem == "GeoAH18H1_2":
            continue
        if itrial.stem == "GeoAH18H2_3":
            continue
        if itrial.stem == "GeoAH6H1_2":
            continue
        if itrial.stem == "YoaBH12H2_3":
            idx = np.array([[1500, 7137]])
        if itrial.stem == "YoaBH12H3_1":
            idx = np.array([[1395, 7000]])
        if itrial.stem == "NemKH12H1_2":
            continue
        if itrial.stem == "NemKH12H1_3":
            continue
        if itrial.stem == "NemKH12H2_2":
            continue
        if itrial.stem == "NemKH18H2_3":
            continue
        if itrial.stem == "NemKH6H1_1":
            continue
        if itrial.stem == "NemKH6H1_2":
            continue
        if itrial.stem == "NemKH6H1_3":
            continue
        if itrial.stem == "NemKH6H2_3":
            continue
        if itrial.stem == "MatRH18H1_2":
            idx = np.array([[1259, 7000]])
        if itrial.stem == "MatRH6H1_2":
            idx = np.array([[1000, 6000]])
        if itrial.stem == "JawRH12H1_3":
            continue
        if itrial.stem == "JawRH12H2_1":
            continue
        if itrial.stem == "JawRH12H3_2":
            continue
        if itrial.stem == "JawRH12H3_3":
            continue
        if itrial.stem == "JawRH12H4_1":
            continue
        if itrial.stem == "JawRH18H4_3":
            idx = np.array([[1259, 6965]])
        if itrial.stem == "JawRH18H4_3":
            idx = np.array([[1000, 7150]])
        if itrial.stem == "JawRH18H4_3":
            idx = np.array([[1000, 7150]])
        if itrial.stem == "JawRH6H2_3":
            idx = np.array([[1000, 7150]])
        if itrial.stem == "PhiIH18H4_3":
            idx = np.array([[1825, 7550]])

        if idx.shape[0] > 1:
            raise ValueError("more than one onset")

        ten_percents = int(forces.shape[-1] * 0.08)
        if idx[0][0] < ten_percents and itrial.stem not in [
            "AmiAF12H2_1",
            "GeoAH18H4_2",
            "NemKH18H1_3",
            "NemKH18H2_1",
        ]:
            raise ValueError(
                f"onset is less than 8% of the trial ({idx[0][0] / forces.shape[-1] * 100:2f}%)"
            )

        ninety_percents = int(forces.shape[-1] * 0.97)
        if idx[0][1] > ninety_percents and itrial.stem not in [
            "FabDH12H5_2",
            "DamGH18H6_2",
            "PhiIH18H1_1",
            "PhiIH18H4_2",
            "PhiIH18H4_3",
        ]:
            raise ValueError(
                f"onset is less than 97% of the trial ({idx[0][1] / forces.shape[-1] * 100:.2f}%)"
            )

        _, ax = plt.subplots(nrows=1, ncols=1)
        norm.plot(ax=ax)
        for (inf, sup) in idx:
            ax.axvline(x=inf, color="g", lw=2, ls="--")
            ax.axvline(x=sup, color="r", lw=2, ls="--")
        plt.title(itrial.stem)
        plt.show()

        forces.get_labels = params["forces_labels"]
        sto_filename = (
            f"{conf.project_path / iparticipant / '0_forces' / itrial.stem}.sto"
        )

        forces.to_sto(filename=sto_filename)

        # add onset & offset in configuration
        onset = idx[0][0] / forces.get_rate
        offset = idx[0][1] / forces.get_rate
        conf.add_conf_field({iparticipant: {"onset": {itrial.stem: [onset, offset]}}})
