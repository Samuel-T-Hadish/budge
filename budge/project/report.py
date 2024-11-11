import tempfile
import os
import csv
import io
import zipfile
import pandas as pd
from budge.project import page1
from budge.project import page2


def generate_report(data):
    files = []
    with tempfile.TemporaryDirectory() as tempdir:
        # Create a temporary directory to store the files
        # Generate the report files

        # save project info as csv file in the tempdir
        meta_input = data.get("meta_input", {})
        meta_input_path = os.path.join(tempdir, "meta_input.csv")
        with open(meta_input_path, "w") as f:
            w = csv.DictWriter(f, meta_input.keys())
            w.writeheader()
            w.writerow(meta_input)

        # save page1_input as csv file in the tempdir
        page1_input = data.get("page1_input", {})
        page1_input_path = os.path.join(tempdir, "page1_input.csv")
        with open(page1_input_path, "w") as f:
            w = csv.DictWriter(f, page1_input.keys())
            w.writeheader()
            w.writerow(page1_input)

        # save page2_input as csv file in the tempdir
        page2_input = data.get("page2_input", {})
        page2_input_path = os.path.join(tempdir, "page2_input.csv")
        with open(page2_input_path, "w") as f:
            w = csv.DictWriter(f, page2_input.keys())
            w.writeheader()
            w.writerow(page2_input)

        # save page1_output as csv file in the tempdir
        page1_output = data.get("page1_output", {})
        page1_output_path = os.path.join(tempdir, "page1_output.csv")
        with open(page1_output_path, "w") as f:
            w = csv.DictWriter(f, page1_output.keys())
            w.writeheader()
            w.writerow(page1_output)

        # save page2_output as csv file in the tempdir
        page2_output = data.get("page2_output", {})
        table = page2_output.get("table", [])
        table_df = pd.DataFrame(table)
        table_df_path = os.path.join(tempdir, "table.csv")
        table_df.to_csv(table_df_path)

        fig = page2.plot_results(data)
        if fig:
            fig_path = os.path.join(tempdir, "plot_results.png")
            fig.write_image(fig_path)

        # After each file is saved, read it into memory and add it to the files list
        for root, dirs, file_names in os.walk(tempdir):
            for file_name in file_names:
                file_path = os.path.join(root, file_name)
                with open(file_path, "rb") as f:
                    data = f.read()
                files.append((file_name, data))

    in_memory_output = io.BytesIO()
    with zipfile.ZipFile(in_memory_output, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_name, data in files:
            data = data.encode() if isinstance(data, str) else data
            data = io.BytesIO(data)
            zf.writestr(file_name, data.getvalue())

    in_memory_output.seek(0)

    return in_memory_output
