from dataclasses import dataclass

@dataclass
class AppConfig:
    name_wood_model: str
    name_sign_model: str
    name_photo: str
    name_volume: str
    name_count: str
    wood_coef: float
    sign_coef: float
    length: float
    avg_distance: int
    is_saving_current_settings: bool
    is_saving_result_detecting: bool
