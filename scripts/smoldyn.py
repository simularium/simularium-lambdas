import numpy as np
from simulariumio.smoldyn import SmoldynConverter, SmoldynData
from simulariumio import (
    UnitData,
    MetaData,
    DisplayData,
    DISPLAY_TYPE,
    ModelMetaData,
    InputFileData,
    JsonWriter,
    CameraData,
)


def lambda_handler(event, context):
    display_data = None
    camera_data = None
    box_size = None
    model_meta_data = None
    if "display_data" in event:
        display_data = dict()
        for index in event["display_data"]:
            agent_info = event["display_data"][index]
            for agent_name in agent_info:
                agent_data = agent_info[agent_name]
                display_data[agent_name] = DisplayData(
                    name=agent_data.get("name"),
                    radius=float(agent_data.get("radius", 1.0)),
                    display_type=agent_data.get("display_type", DISPLAY_TYPE.SPHERE),
                    url=agent_data.get("url"),
                    color=agent_data.get("color"),
                )
    if "meta_data" in event:
        metadata = event["meta_data"]
        if "box_size" in metadata and len(metadata["box_size"]) == 3:
            box_size = np.array(
                [
                    float(metadata["box_size"]["0"]),
                    float(metadata["box_size"]["1"]),
                    float(metadata["box_size"]["2"]),
                ]
            )

        if "camera_defaults" in metadata:
            camera_defaults = metadata["camera_defaults"]
            position = None
            up_vector = None
            look_at_position = None
            fov_degrees = None
            if "position" in camera_defaults and len(camera_defaults["position"]) == 3:
                position = np.array(
                    [
                        float(camera_defaults["position"]["0"]),
                        float(camera_defaults["position"]["1"]),
                        float(camera_defaults["position"]["2"]),
                    ]
                )
            if "up_vector" in camera_defaults and len(camera_defaults["up_vector"]) == 3:
                up_vector = np.array(
                    [
                        float(camera_defaults["up_vector"]["0"]),
                        float(camera_defaults["up_vector"]["1"]),
                        float(camera_defaults["up_vector"]["2"]),
                    ]
                )
            if "look_at_position" in camera_defaults and len(camera_defaults["look_at_position"]) == 3:
                look_at_position = np.array(
                    [
                        float(camera_defaults["look_at_position"]["0"]),
                        float(camera_defaults["look_at_position"]["1"]),
                        float(camera_defaults["look_at_position"]["2"]),
                    ]
                )
            if "fov_degrees" in camera_defaults:
                fov_degrees = float(camera_defaults["fov_degrees"])

            camera_data = CameraData(
                fov_degrees=fov_degrees,
                position=position,
                up_vector=up_vector,
                look_at_position=look_at_position,
            )

        if "model_meta_data" in metadata:
            model_data = metadata["model_meta_data"]
            model_meta_data = (
                ModelMetaData(
                    title=model_data.get("title"),
                    version=model_data.get("version", ""),
                    authors=model_data.get("author", ""),
                    description=model_data.get("description", ""),
                    doi=model_data.get("doi", ""),
                    source_code_url=model_data.get("source_code_url", ""),
                    source_code_license_url=model_data.get(
                        "source_code_license_url", ""
                    ),
                    input_data_url=model_data.get("input_data_url", ""),
                    raw_output_data_url=model_data.get("raw_output_data_url", ""),
                ),
            )

    # spatial units defaults to 1.0 meters
    spatial_units = UnitData(
        name=event["spatial_units"]["name"]
            if "spatial_units" in event and "name" in event["spatial_units"]
            else "meter",
        magnitude=float(event["spatial_units"]["magnitude"])
            if "spatial_units" in event and "magnitude" in event["spatial_units"]
            else 1.0,
    )

    # time units default to 1.0 seconds
    time_units = UnitData(
        name=event["time_units"]["name"]
            if "time_units" in event and "name" in event["time_units"]
            else "second",
        magnitude=float(event["time_units"]["magnitude"])
            if "time_units" in event and "magnitude" in event["time_units"]
            else 1.0,
    )

    data = SmoldynData(
        meta_data=MetaData(
            box_size=box_size,
            trajectory_title=event.get("trajectory_title", "No Title"),
            scale_factor=float(event.get("scale_factor", 1.0)),
            camera_defaults=camera_data,
            model_meta_data=model_meta_data,
        ),
        smoldyn_file=InputFileData(
            file_contents=event["file_contents"]["file_contents"],
        ),
        display_data=display_data,
        time_units=time_units,
        spatial_units=spatial_units,
    )

    return JsonWriter.format_trajectory_data(SmoldynConverter(data)._data)
