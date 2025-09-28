from fastapi import APIRouter


router = APIRouter()


@router.post("/ninja/")
def create_nina():
    return None
