from fastapi import APIRouter

router = APIRouter()

@router.get("/layers", tags=["layers"])
async def get_layers():
    return [{"text": "This is the layers path"}]

@router.get("/layers/{layer_id}", tags=["layers"])
async def get_layer(layer_id: str):
    return [{"text": f"This is the layer {layer_id} path"}]