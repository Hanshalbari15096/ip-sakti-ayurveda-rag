"""Configuration for IP-SAKTI Ayurveda IPR Assistant.

Loads settings from environment variables (or .env file).
Falls back to demo mode when API keys are missing so the app stays runnable.
"""
import os
from pathlib import Path
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


@dataclass
class AppConfig:
    """Application configuration loaded from environment variables."""

    # External APIs (may be empty when running in demo mode)
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    sarvam_api_key: str = field(default_factory=lambda: os.getenv("SARVAM_API_KEY", ""))

    # Speech-to-Text model on Groq (whisper-large-v3 is the most accurate)
    groq_stt_model: str = field(
        default_factory=lambda: os.getenv("GROQ_STT_MODEL", "whisper-large-v3")
    )

    # Collections
    collection_name: str = field(
        default_factory=lambda: os.getenv("COLLECTION_NAME", "my_knowledge")
    )
    chunk_size: int = field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "500")))
    top_k: int = field(default_factory=lambda: int(os.getenv("TOP_K", "8")))
    data_file: str = "data/data.txt"

    # Hybrid retrieval (dense ANN + in-memory BM25 fused by RRF). Set to 0 to
    # disable and fall back to dense-only search (A/B comparison).
    hybrid_search: bool = field(
        default_factory=lambda: os.getenv("HYBRID_SEARCH", "1").lower()
        in ("1", "true", "yes", "on")
    )

    # Languages
    supported_languages: list = field(
        default_factory=lambda: ["en", "hi", "mr", "sa", "bn", "ta", "te", "kn", "gu"]
    )

    # Model
    model: str = field(
        default_factory=lambda: os.getenv("MODEL", "gemini-2.5-flash")
    )

    @property
    def demo_mode(self) -> bool:
        # Custom OpenAI-compatible endpoint counts as a real LLM
        if os.getenv("LLM_API_KEY") and os.getenv("LLM_BASE_URL"):
            return False
        if self.groq_configured:
            return False
        if not self.gemini_api_key and not self.groq_api_key:
            return True
        groq_placeholder = {"gsk_your_groq_api_key_here", "your-api-key", "your_key", ""}
        if self.groq_api_key and self.groq_api_key.lower().strip() not in groq_placeholder:
            return False
        # Gemini key validation: should start with "AQ." and be reasonably long
        if self.gemini_api_key and len(self.gemini_api_key) > 30 and self.gemini_api_key.startswith("AQ."):
            return False
        return True

    @property
    def sarvam_configured(self) -> bool:
        if not self.sarvam_api_key:
            return False
        placeholder_keys = {"your_sarvam_api_key_here", "your-api-key", "your_key", ""}
        return self.sarvam_api_key.lower().strip() not in placeholder_keys

    @property
    def groq_configured(self) -> bool:
        """Groq key valid for both LLM answers and Whisper STT."""
        if not self.groq_api_key:
            return False
        placeholder_keys = {"gsk_your_groq_api_key_here", "your-api-key", "your_key", ""}
        return self.groq_api_key.lower().strip() not in placeholder_keys

    def print_status(self) -> None:
        """Print the current configuration status at startup."""
        print("=" * 60)
        print("IP-SAKTI Ayurveda IPR Assistant - Configuration")
        print("=" * 60)
        print(f"  Collection name : {self.collection_name}")
        print(f"  Chunk size      : {self.chunk_size}")
        print(f"  Top-K results   : {self.top_k}")
        print(f"  Hybrid search   : {'ON (dense + BM25)' if self.hybrid_search else 'OFF (dense only)'}")
        print(f"  LLM model       : {self.model}")
        print(f"  Data file       : {self.data_file}")
        print(f"  Gemini API key  : {'SET' if self.gemini_api_key else 'MISSING'}")
        print(f"  Groq API key    : {'SET (LLM + STT)' if self.groq_configured else 'MISSING'}")
        print(f"  Sarvam API key  : {'SET' if self.sarvam_configured else 'MISSING'}")
        print(f"  STT provider    : {self.stt_provider}")
        if self.demo_mode:
            print("")
            print("  ! RUNNING IN DEMO MODE !")
            print("  Set GEMINI_API_KEY or GROQ_API_KEY in .env to enable LLM responses.")
            print("  The RAG retriever will still return source chunks.")
        if not self.sarvam_configured:
            print("")
            print("  ! Sarvam AI STT not configured !")
            print("  Set SARVAM_API_KEY in .env for high-quality Hindi STT.")
            print("  Falling back to Groq Whisper / Google Speech when unavailable.")
        print("=" * 60)

    @property
    def stt_provider(self) -> str:
        """Primary STT provider shown in the UI."""
        if self.sarvam_configured:
            return "Sarvam AI"
        if self.groq_configured:
            return "Groq Whisper"
        return "Google Speech"


config = AppConfig()
