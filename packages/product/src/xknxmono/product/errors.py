class ArchiveError(Exception):
    """Raised when a knxprod archive is invalid or cannot be read."""


class VersionError(Exception):
    """Raised when a KNX version cannot be detected or is unsupported."""


class ParseError(Exception):
    """Raised when XML parsing fails."""


class EncodingError(Exception):
    """Raised when a parameter/union write cannot be resolved or encoded.

    Covers every point where the static model, a module instance's arguments, or a
    stored override value fails to produce a well-formed write - an unresolvable
    base offset, a dangling reference, an unknown code segment/parameter type, or a
    value that doesn't parse against its declared type. All of these indicate the
    product or project data is internally inconsistent; encoding continues on good
    faith that real device data is well-formed, so this is raised rather than
    silently producing a partial or wrong memory/property image.

    Note: a union with neither an active override nor a default member is *not*
    covered here - real product data ships unions like that on purpose, meaning
    nothing should be written for them, so that case is a legitimate skip.
    """
