from dataclasses import dataclass
@dataclass(frozen=True)
class Settings:
    app_env: str = "production"
    minimax_base_url: str = "https://api.minimax.io/v1"
    minimax_model: str = "MiniMax-M2.7"
    session_ttl_seconds: int = 43200
    admin_session_ttl_seconds: int = 3600
