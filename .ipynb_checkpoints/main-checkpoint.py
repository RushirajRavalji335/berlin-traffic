import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def prepare_ds(df:pd.DataFrame) -> pd.DataFrame:
    df["tag_date"] = pd.to_datetime(df["tag"], format="%d.%m.%Y")
    return df


def load_dataset(datapath:Path=Path("./data/csv")) -> pd.DataFrame:
    datapath = datapath.expanduser().absolute()
    files = sorted(datapath.glob("**.csv"))
    if len(files):
        print(f"Found {len(files)} '.csv' files")
        dataframes = []
        for file in files:
            df = pd.read_csv(file)
            dataframes.append(df)
        if len(dataframes):
            print(f"Loaded {len(dataframes)} '.csv' files successfull")
            df = pd.concat(dataframes)
            return prepare_ds(df)
    raise FileNotFoundError(f"Failed to load a single csv file from {datapath}!")



def create_basic_plots(df):
    df_per_day = df.groupby("tag_date")["q_pkw_mq_hr"].sum().reset_index()

    plt.figure(figsize=(10, 6))
    plt.plot(df_per_day["tag_date"], df_per_day["q_pkw_mq_hr"], marker="x", linestyle="")
    plt.title("Cars per day")
    plt.xlabel("Day")
    plt.ylabel("Sum")
    plt.grid(True)
    plt.tight_layout()
    outfile = Path("./out/cars_per_day.png")
    outfile.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outfile)
    plt.close()

    df_per_hour = df.groupby("stunde")["q_pkw_mq_hr"].sum().reset_index()

    plt.figure(figsize=(10, 6))
    plt.bar(df_per_hour["stunde"], df_per_hour["q_pkw_mq_hr"])
    plt.title("Cars per hour")
    plt.xlabel("Hour")
    plt.ylabel("Sum")
    plt.xticks(df_per_hour["stunde"])
    plt.grid(True)
    plt.tight_layout()
    outfile = Path("./out/cars_per_hour.png")
    outfile.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outfile)
    plt.close()


def main():
    df = load_dataset()
    print(df.columns)
    print(df.dtypes)
    print(df.head())
    create_basic_plots(df)


if __name__ == "__main__":
    main()
