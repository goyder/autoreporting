import pandas as pd
from jinja2 import FileSystemLoader, Environment

# Allow for very wide columns - otherwise columns are spaced and ellipse'd
pd.set_option("display.max_colwidth", 200)


def csv_to_html(filepath):
    """
    Open a .csv file and return it in HTML format.
    :param filepath: Filepath to a .csv file to be read.
    :return: String of HTML to be published.
    """
    df = pd.read_csv(filepath, index_col=0)
    html = df.to_html()
    return html


# Configure Jinja and ready the loader
env = Environment(
    loader=FileSystemLoader(searchpath="templates")
)

# Assemble the templates we'll use
base_template = env.get_template("report.html")
table_section_template = env.get_template("table_section.html")

# Content to be published
title = "Model Report"
sections = list()
sections.append(table_section_template.render(
    model="VGG19",
    dataset="VGG19_results.csv",
    table=csv_to_html("datasets/VGG19_results.csv")
))
sections.append(table_section_template.render(
    model="MobileNet",
    dataset="MobileNet_results.csv",
    table=csv_to_html("datasets/MobileNet_results.csv")
))


def main():
    """
    Entry point for the script.
    Render a template and write it to file.
    :return:
    """
    with open("outputs/report.html", "w") as f:
        f.write(base_template.render(
            title=title,
            sections=sections
        ))


if __name__ == "__main__":
    main()
