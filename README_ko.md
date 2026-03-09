# API Document Collector 🤖

[English](README.md) | **한국어**

API 문서 웹사이트를 자동으로 크롤링하고, LLM을 사용해 사이트 구조를 분석하여 깔끔한 마크다운 콘텐츠로 추출하며, 원할 경우 에이전트 기반 파이프라인을 위한 로컬 RAG 벡터 데이터베이스까지 구축하는 범용 파이프라인입니다.

## ⭐ 주요 기능
1. **지능형 설정 자동 생성**: 시작 URL만 입력하면, LLM(로컬 Ollama 또는 원격 API)이 HTML을 분석하여 동적 CSS 셀렉터와 크롤링 설정을 스스로 생성합니다.
2. **강력한 스크래핑**: API 문서를 재귀적으로 탐색하며 복잡한 HTML 노드들을 깔끔하고 LLM 친화적인 마크다운 구문(`.md`)으로 변환합니다. 메타데이터 유지를 위해 YAML Frontmatter를 삽입합니다.
3. **품질 검증**: 생성된 마크다운 결과물을 무작위로 샘플링하여, 파라미터, 엔드포인트, 코드 샘플 등이 제대로 문서에 포함되었는지 LLM이 자동으로 검증합니다.
4. **즉시 사용 가능한 RAG 구축**: 마크다운 헤더를 기준으로 텍스트를 분할(Chunking)하고, HuggingFace 임베딩(`all-MiniLM-L6-v2`)을 사용하여 로컬 ChromaDB 벡터 저장소를 생성하는 모듈이 포함되어 있습니다.

## 📋 필수 조건
- Python 3.10+
- (선택 사항) 무료 LLM 연동을 위해 로컬에서 [Ollama](https://ollama.com/) 실행 환경

## 🚀 설치 방법
```bash
# 리포지토리 클론
git clone https://github.com/chcknnbn/api-doc-collector.git
cd api-doc-collector

# 의존성 설치
pip install -r requirements.txt
```

## 💻 사용 방법

대상 API 문서의 기본 URL을 제공하여 메인 파이프라인을 실행합니다.

### 1. 기본 실행 (마크다운만 수집)
이 명령어는 HTML을 수집하여 깔끔한 마크다운으로 추출한 뒤 `./docs` 폴더에 저장합니다.
```bash
python main.py https://docs.example.com/api
```

### 2. 로컬 LLM (Ollama) 사용
Llama 모델 등을 사용하여 크롤러 설정을 자동으로 생성하고 결과물을 검증합니다.
```bash
# 백그라운드에서 Ollama가 실행 중이어야 합니다.
export OLLAMA_HOST=localhost
python main.py https://docs.example.com/api --llm local:ollama/llama3.2
```

### 3. OpenAI 사용 & RAG 벡터 DB 구축
문서를 성공적으로 추출한 후 자동으로 `./rag_db` 경로에 벡터 데이터베이스를 구축합니다.
```bash
export OPENAI_API_KEY="sk-..."
python main.py https://docs.example.com/api --llm api:openai/gpt-4o --rag
```

### 4. Google Gemini 사용
```bash
export GEMINI_API_KEY="AIzaSy..."
python main.py https://docs.example.com/api --llm api:gemini/gemini-1.5-flash --rag
```

### 5. Anthropic Claude 사용
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py https://docs.example.com/api --llm api:anthropic/claude-3-haiku-20240307 --rag
```

## 📁 프로젝트 구조
```text
api-doc-collector/
├── configs/           # 자동 생성된 JSON 크롤러 설정 파일
├── docs/              # 추출된 마크다운 파일 (Git 무시됨)
├── rag_db/            # 생성된 Chroma Vector DB (Git 무시됨)
├── src/
│   ├── llm_config.py  # LLM 기반 HTML 분석기
│   ├── collector.py   # 재귀적 스크래퍼 및 마크다운 변환기
│   ├── validator.py   # LLM 품질 검증 게이트
│   └── rag_builder.py # LangChain RAG 파이프라인
├── requirements.txt
└── main.py            # CLI 엔트리포인트 모듈
```

## 🤝 기여하기
버그 리포트, 기능 제안 및 풀 리퀘스트는 언제든 환영합니다!
