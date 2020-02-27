from pymodelica import compile_fmu


def create_fmu(params):
    """

    :return:
    : see the following link on how to supply parameters when creating FMU
    : - https://stackoverflow.com/questions/35670621/jmodelica-changing-a-loop-iteration-variable-without-re-compiling
    """
    file_path = params.model.file_path
    fmu_dir = params.model.fmu_dir
    for model in params.model.available_models:
        model_name = params.model.package_name + "." + model.name
        # create fmu and load it
        compile_fmu(model_name, file_path, version='2.0', compile_to=fmu_dir,
                    compiler_log_level='warning', separate_process=False)

