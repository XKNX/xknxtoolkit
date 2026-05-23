from fastapi import APIRouter, HTTPException, UploadFile
from xknxmono.product.errors import ArchiveError

from xknxmono.catalog.db import get_knxprod_dir
from xknxmono.catalog.ingest import ingest_file

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("")
async def upload_knxprod(file: UploadFile):
    if not file.filename or not file.filename.endswith(".knxprod"):
        raise HTTPException(400, "File must be a .knxprod archive")
    content = await file.read()
    try:
        saved = ingest_file(content, get_knxprod_dir())
    except ArchiveError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"filename": saved.name}
