#  coding: utf-8

from path import Path


def new_file_name(input_path: Path, extension: str) -> Path:
    """Provide the path of a new file using the parent dir name.
    
    Arguments:
        input_path {Path} -- The path of a file contained in the targeted dir
        extension {str} -- The extension of the new file
    
    Returns:
        output_path {Path} -- The new path generated
    """
    if "." not in extension:
        raise SyntaxError("Missing '.' character in the extension name")
    output_path: Path = Path(
        Path.joinpath(*input_path.splitall()[:-1])
    ) / input_path.dirname().basename() + extension
    return output_path
