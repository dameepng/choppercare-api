from fastapi import APIRouter

router = APIRouter()


@router.get("/alert/latest")
async def get_latest_alerts():
    """Placeholder — bisa connect ke BMKG API nanti."""
    return {
        "alerts": [],
        "source": "BNPB/BMKG",
        "note": "Integrasi BMKG API coming soon",
    }