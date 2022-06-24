import os
from functools import lru_cache
from typing import List

from plantuml import PlantUML

from config import settings


def get_current_pipeline_version(dir_name: str):
    settings_version_attr = "CURRENT_" + dir_name.upper()
    return getattr(settings, settings_version_attr, "v1.0.0")


def get_pipeline_name(dir_name: str):
    return dir_name.replace("_", " ").upper()


def get_name_and_plantuml_link(absolute_paths: List[str]) -> dict:
    plantuml = PlantUML(url=settings.PLANTUML_SERVER_URL)

    name_link_map = dict()
    for path in absolute_paths:
        with open(path, "r") as file:
            plantuml_text = file.read()

        version_name = str(path).split("/")[-1].replace(".puml", "")

        name_link_map[version_name] = plantuml.get_url(plantuml_text)

    return name_link_map


def get_link_list_in_dir(dir_name: str):
    abs_path = os.path.join(settings.BASE_DIR.parent, "docs", dir_name)
    objects_in_docs_dir = sorted(os.listdir(abs_path))
    files_in_docs_dir = [
        os.path.join(abs_path, file) for file in objects_in_docs_dir if os.path.isfile(os.path.join(abs_path, file))
    ]

    name_link_map = get_name_and_plantuml_link(files_in_docs_dir)

    link_list = f"\n**{get_pipeline_name(dir_name)}**:\n\n"
    for name, link in name_link_map.items():
        element = f'<a href="{link}">{name}</a>'

        element += (
            " < 🟢 Current Pipeline version\n\n" if name.startswith(get_current_pipeline_version(dir_name)) else "\n\n"
        )

        link_list += element

    return link_list


@lru_cache
def construct_plantuml_link_list() -> str:
    path_to_docs = str(settings.BASE_DIR.parent) + "/docs"

    doc_dirs = [obj for obj in os.listdir(path_to_docs) if os.path.isdir(os.path.join(path_to_docs, obj))]

    result = str()

    for doc_dir in doc_dirs:
        result += get_link_list_in_dir(doc_dir)

    return result
