from enum import StrEnum


class MimeType(StrEnum):
    CSV = "text/csv"
    PDF = "application/pdf"
    JSON = "application/json"
    TXT = "text/plain"
    MD = "text/markdown"
    PNG = "image/png"
    JPEG = "image/jpeg"
    GIF = "image/gif"
    MP4 = "video/mp4"
    MOV = "video/quicktime"
    AVI = "video/x-msvideo"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    DOC = "application/msword"
