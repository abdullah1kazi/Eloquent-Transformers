"""Audio API endpoints."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from ...application.commands.transcribe_audio_command import (
    TranscribeAudioCommand,
    TranscribeAudioCommandHandler,
)
from ...application.commands.upload_audio_command import (
    UploadAudioCommand,
    UploadAudioCommandHandler,
)
from ...application.queries.audio_queries import (
    GetAudioQuery,
    GetAudioQueryHandler,
    ListUserAudiosQuery,
    ListUserAudiosQueryHandler,
    SearchAudioQuery,
    SearchAudioQueryHandler,
)
from ...domain.exceptions import AudioNotFoundException, UnauthorizedException
from ..dependencies import (
    get_audio_query_handler,
    get_list_audios_handler,
    get_search_handler,
    get_transcribe_audio_handler,
    get_upload_audio_handler,
)
from ..schemas import (
    AudioDetailResponse,
    AudioUploadResponse,
    ErrorResponse,
    SearchRequest,
    SearchResponse,
    TranscriptionResponse,
)

router = APIRouter(prefix="/audio", tags=["audio"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/upload",
    response_model=AudioUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload audio file",
    description="Upload an audio file for transcription and analysis",
    responses={
        201: {"description": "Audio uploaded successfully"},
        400: {"model": ErrorResponse, "description": "Invalid file format"},
        413: {"model": ErrorResponse, "description": "File too large"},
    },
)
async def upload_audio(
    file: UploadFile = File(
        ..., description="Audio file (mp3, wav, flac, m4a, ogg, opus)"
    ),
    handler: UploadAudioCommandHandler = Depends(get_upload_audio_handler),
) -> AudioUploadResponse:
    """
    Upload an audio file.

    Demonstrates:
    - File upload handling
    - Command pattern usage
    - Validation
    - Error handling
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Must be an audio file.",
        )

    # TODO: Get user ID from authentication token
    user_id = "00000000-0000-0000-0000-000000000000"  # Placeholder

    try:
        command = UploadAudioCommand(
            user_id=user_id,
            filename=file.filename or "unknown.mp3",
            file=file.file,
            content_type=file.content_type,
        )

        result = await handler.handle(command)
        return AudioUploadResponse(**result.__dict__)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.post(
    "/{audio_id}/transcribe",
    response_model=TranscriptionResponse,
    summary="Transcribe audio",
    description="Transcribe audio to text using Whisper",
    responses={
        200: {"description": "Transcription completed"},
        404: {"model": ErrorResponse, "description": "Audio not found"},
        500: {"model": ErrorResponse, "description": "Transcription failed"},
    },
)
async def transcribe_audio(
    audio_id: str,
    handler: TranscribeAudioCommandHandler = Depends(get_transcribe_audio_handler),
) -> TranscriptionResponse:
    """
    Transcribe audio to text.

    This endpoint:
    - Transcribes audio using Whisper
    - Generates semantic embeddings
    - Returns transcription with segments
    """
    try:
        command = TranscribeAudioCommand(audio_id=audio_id)
        result = await handler.handle(command)
        return TranscriptionResponse(**result.__dict__)

    except AudioNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.get(
    "/{audio_id}",
    response_model=AudioDetailResponse,
    summary="Get audio details",
    description="Get detailed information about an audio file",
    responses={
        200: {"description": "Audio details"},
        404: {"model": ErrorResponse, "description": "Audio not found"},
        403: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def get_audio(
    audio_id: str,
    handler: GetAudioQueryHandler = Depends(get_audio_query_handler),
) -> AudioDetailResponse:
    """Get audio details by ID."""
    # TODO: Get user ID from authentication token
    user_id = "00000000-0000-0000-0000-000000000000"  # Placeholder

    try:
        query = GetAudioQuery(audio_id=audio_id, user_id=user_id)
        result = await handler.handle(query)
        return AudioDetailResponse(**result.__dict__)

    except AudioNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e


@router.get(
    "/",
    response_model=list[AudioDetailResponse],
    summary="List user's audio files",
    description="Get list of audio files uploaded by the user",
)
async def list_audios(
    limit: int = 100,
    offset: int = 0,
    handler: ListUserAudiosQueryHandler = Depends(get_list_audios_handler),
) -> list[AudioDetailResponse]:
    """List user's audio files."""
    # TODO: Get user ID from authentication token
    user_id = "00000000-0000-0000-0000-000000000000"  # Placeholder

    query = ListUserAudiosQuery(user_id=user_id, limit=limit, offset=offset)
    results = await handler.handle(query)
    return [AudioDetailResponse(**r.__dict__) for r in results]


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Semantic audio search",
    description="Search audio files by semantic meaning using vector similarity",
    responses={
        200: {"description": "Search results"},
        400: {"model": ErrorResponse, "description": "Invalid query"},
    },
)
@limiter.limit("30/minute")  # Rate limit semantic search
async def search_audio(
    request: SearchRequest,
    handler: SearchAudioQueryHandler = Depends(get_search_handler),
) -> SearchResponse:
    """
    Semantic audio search.

    Demonstrates:
    - Query pattern
    - Vector similarity search
    - Rate limiting on expensive operations
    """
    # TODO: Get user ID from authentication token
    user_id = "00000000-0000-0000-0000-000000000000"  # Placeholder

    query = SearchAudioQuery(query_text=request.query, user_id=user_id, limit=request.limit)

    results = await handler.handle(query)

    return SearchResponse(
        results=[
            {
                "audio": r.audio.__dict__,
                "similarity_score": r.similarity_score,
                "matched_segment": r.matched_segment,
            }
            for r in results
        ],
        query=request.query,
        total=len(results),
    )
