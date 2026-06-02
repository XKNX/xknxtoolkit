"""Upload router: accept .knxprod file uploads and ingest them into the catalog."""

from fastapi import APIRouter, HTTPException, Request, UploadFile

from xknxmono.catalog.core.upload import upload_knxprod as _upload_knxprod
from xknxmono.product.errors import ArchiveError

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("")
async def upload_knxprod(file: UploadFile, request: Request):
    """Accept a .knxprod file upload and ingest it into the catalog database.

    Returns the stored filename. Duplicate uploads (same content) are ignored silently.
    """
    if not file.filename or not file.filename.endswith(".knxprod"):
        raise HTTPException(400, "File must be a .knxprod archive")
    content = await file.read()
    try:
        saved = _upload_knxprod(
            content, request.app.state.knxprod_dir, request.app.state.engine
        )
    except ArchiveError as e:
        raise HTTPException(422, str(e)) from e
    except Exception as e:
        raise HTTPException(500, str(e)) from e
    return {"filename": saved.name}
