import json
import os

from src.loading import load_model_configuration
from src.sampling import sample

MODEL_CONFIGURATION_DIR = "model_configurations"
RESULTS_DIR = os.path.join("results", "runs")


def main():
    config_files = [
        os.path.join(MODEL_CONFIGURATION_DIR, f)
        for f in os.listdir(MODEL_CONFIGURATION_DIR)
        if f.endswith(".toml")
    ]
    for config_file in sorted(config_files):
        mc = load_model_configuration(config_file)
        with open(os.path.join(mc.data_dir, "coords.json"), "r") as f:
            coords = json.load(f)
        with open(os.path.join(mc.data_dir, "dims.json"), "r") as f:
            dims = json.load(f)

        if not mc.do_not_run:
            run_dir = os.path.join(RESULTS_DIR, mc.name)
            suffs = []
            if os.path.exists(
                os.path.join(mc.data_dir, "stan_input_fake.json")
            ):
                suffs += ["fake"]
            for suff in suffs:
                input_json = os.path.join(
                    mc.data_dir, f"stan_input_{suff}.json"
                )
                output_dir = os.path.join(run_dir, suff)
                print(f"\n***Fitting model {mc.name} in {suff} mode...***\n")
                _, _ = sample(
                    stan_file=mc.stan_file,
                    input_json=input_json,
                    output_dir=output_dir,
                    coords=coords,
                    dims=dims,
                    sample_kwargs=mc.sample_kwargs,
                    print_mode=True,
                )
            if mc.run_cross_validation:
                splits_dir = os.path.join(mc.data_dir, "splits")
                if mc.sample_kwargs_cross_validation is None:
                    sample_kwargs = mc.sample_kwargs
                else:
                    sample_kwargs = {
                        **mc.sample_kwargs,
                        **mc.sample_kwargs_cross_validation,
                    }

                for f in os.listdir(splits_dir):
                    output_dir = os.path.join(
                        run_dir, "splits", f.split(".")[0]
                    )
                    input_json = os.path.join(splits_dir, f)
                    _, _ = sample(
                        stan_file=mc.stan_file,
                        input_json=input_json,
                        output_dir=output_dir,
                        coords=coords,
                        dims=dims,
                        sample_kwargs=sample_kwargs,
                        print_mode=False,
                    )


if __name__ == "__main__":
    main()
