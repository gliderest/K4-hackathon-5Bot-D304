def artifact_version_dict(artifact_version):
    """
    Convert an artifact version object to a dictionary.
    """
    if hasattr(artifact_version, '__dict__'):
        return artifact_version.__dict__
    elif isinstance(artifact_version, dict):
        return artifact_version
    else:
        # Fallback: treat as a string and return a dict with a version key
        return {"artifact_version": str(artifact_version)}


def build_artifact_version(version_label, system_prompt_path, tools_path):
    """
    Build an artifact version object from the given inputs.
    For now, we return a simple object with a version string.
    """
    class ArtifactVersion:
        def __init__(self, version):
            self.artifact_version = version

    # We ignore the actual content of the files for now, just use the label
    return ArtifactVersion(version_label)