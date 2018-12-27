import pandas as pd
import os
from jinja2 import FileSystemLoader, Environment

# Allow for very wide columns - otherwise columns are spaced and ellipse'd
pd.set_option("display.max_colwidth", 200)


class ModelResults:
    """
    Class to store the results of a model run and associated data.
    """

    def __init__(self, model_name, filepath):
        """
        :param model_name: Name of model.
        :param filepath: Filepath to results .csv.
        """
        self.model_name = model_name
        self.filepath = filepath

        self.dataset = os.path.split(filepath)[-1]
        self.df_results = csv_to_df(filepath)  # Filesystem access

        self.number_of_images = len(self.df_results)

        self.accuracy = self._calculate_accuracy()

        self.misidentified_images = self._get_misidentified_images()
        self.number_misidentified = len(self.misidentified_images)

    def _calculate_accuracy(self):
        """
        Return the accuracy for the dataset.
        :return: Float of dataset accuracy [0..1].
        """
        number_correct = len(self.df_results[self.df_results["correct"] == True])
        number_total = len(self.df_results)
        return number_correct / number_total

    def _get_misidentified_images(self):
        """
        Return the names misidentified images.
        :return: List of strings of misidentified image filenames.
        """
        df_misidentified = self.df_results[self.df_results["correct"] == False]
        misidentified_images = df_misidentified.index.tolist()
        return misidentified_images

    def get_results_df_as_html(self):
        """
        Return the results DataFrame as an HTML object.
        :return: String of HTML.
        """
        html = self.df_results.to_html(table_id=self.model_name)
        return html


def csv_to_df(filepath):
    """
    Open a .csv file and return it in DataFrame format.
    :param filepath: Filepath to a .csv file to be read.
    :return: .csv file in DataFrame format.
    """
    df = pd.read_csv(filepath, index_col=0)
    return df


def common_misidentified_images(list_model_results):
    """
    For a collection of ModelResults objects, return a list of images names that were misidentified by all.
    :param list_model_results: List of ModelResults objects.
    :return: List of common misidentified image names.
    """
    misidentified_images_sets = [set(model_results.misidentified_images) for model_results in list_model_results]
    common_images = set.intersection(*misidentified_images_sets)
    return common_images


# Configure Jinja and ready the loader
env = Environment(
    loader=FileSystemLoader(searchpath="templates")
)

# Assemble the templates we'll use
base_template = env.get_template("report.html")
summary_section_template = env.get_template("summary_section.html")
table_section_template = env.get_template("table_section.html")


def main():
    """
    Entry point for the script.
    Render a template and write it to file.
    :return:
    """
    # Content to be published
    title = "Model Report"
    vgg19_results = ModelResults("VGG19", "datasets/VGG19_results.csv")
    mobilenet_results = ModelResults("MobileNet", "datasets/MobileNet_results.csv")
    number_misidentified = len(set(vgg19_results.misidentified_images) & set(mobilenet_results.misidentified_images))

    # Produce our section blocks
    sections = list()
    sections.append(summary_section_template.render(
        model_results_list=[vgg19_results, mobilenet_results],
        number_misidentified=number_misidentified
    ))
    sections.append(table_section_template.render(
        model=vgg19_results.model_name,
        dataset=vgg19_results.dataset,
        table=vgg19_results.get_results_df_as_html())
    )
    sections.append(table_section_template.render(
        model=mobilenet_results.model_name,
        dataset=mobilenet_results.dataset,
        table=mobilenet_results.get_results_df_as_html())
    )

    # Produce and write the report to file
    with open("outputs/report.html", "w") as f:
        f.write(base_template.render(
            title=title,
            sections=sections
        ))


if __name__ == "__main__":
    main()
