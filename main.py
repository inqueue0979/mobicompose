from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import xml.etree.ElementTree as ET
import re

app = FastAPI()

# 허용할 도메인(Origin) 리스트
# 실제 사용 시 특정 도메인/포트로 제한하는 것이 보안에 좋습니다.
origins = [
    "http://localhost:5173",  # Vite dev server
    "https://mobicompose.vercel.app/",  # Vercel 도메인
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드를 허용
    allow_headers=["*"],  # 모든 헤더를 허용
)

@app.post("/convert")
async def convert_ms2mml_file(file: UploadFile = File(...)):
    """
    1) multipart/form-data로 업로드된 파일 받기
    2) 파일 내용 -> 문자열
    3) 문자열을 XML 파싱 + 치환
    4) 변환 결과 반환
    """
    # 1) 파일 내용 읽기
    file_content = await file.read()  # 비동기
    # 또는 file.file.read() (동기), 파일 크기 등이 클 경우 주의

    # 2) bytes -> 문자열 디코딩
    ms2mml_str = file_content.decode("utf-8", errors="replace")

    # 3) ms2mml 문자열을 파싱 및 변환
    converted_data = parse_and_convert_ms2mml(ms2mml_str)

    return {"converted": converted_data}


def parse_and_convert_ms2mml(xml_str: str) -> dict:
    """
    ms2mml XML 파싱 후, 기초적인 MML로 치환하는 예시
    (melody, chord 등)
    """
    result = {}

    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError as e:
        return {"error": f"XML Parse Error: {str(e)}"}

    # <melody> 태그
    melody_tag = root.find('melody')
    melody_text = melody_tag.text if (melody_tag is not None and melody_tag.text) else ""
    result["converted_melody"] = convert_cdata_to_mml(melody_text)

    # <chord> 태그들
    chord_tags = root.findall('chord')
    for chord_tag in chord_tags:
        idx = chord_tag.get('index', 'unknown')
        chord_text = chord_tag.text if chord_tag.text else ""
        result[f"converted_chord_{idx}"] = convert_cdata_to_mml(chord_text)

    return result


def convert_cdata_to_mml(text: str) -> str:
    # 개행(\n, \r) 제거
    text = text.replace('\n', '').replace('\r', '')
    
    # 필요 시 앞뒤 공백 제거
    data = text.strip()

    # 이후 필요한 파싱/치환 로직 수행
    # 예: data = re.sub(r'v(\d+)', r'V\1', data) 등

    return data