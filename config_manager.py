import json
import os
from dataclasses import asdict
from pathlib import Path

from app_config import AppConfig
from logger import setup_logger

label_wood_model = "name_wood_model"
label_sign_model = "name_sign_model"
label_photo = "label_photo"
label_volume = "label_volume"
label_count_circle = "label_count_circle"
label_length = "avg_length"
label_wood_coef = "wood_detect_coef"
label_sign_coef = "sign_detect_coef"

label_avg_distance = "avg_distance"
label_saving_cur_settings ="is_saving_current_settings"
label_saving_detecting = "is_saving_result_detecting"

required_keys = [
    label_wood_model,
    label_sign_model,
    label_photo,
    label_volume,
    label_count_circle,
    label_length,
    label_wood_coef,
    label_sign_coef,
    label_avg_distance,
    label_saving_cur_settings,
    label_saving_detecting
]
BASE_DIR = Path.cwd()
logger = setup_logger()
class ConfigManager:
    def __init__(self,
                 config_path=BASE_DIR / "config" / "user-config.json",
                 default_path=BASE_DIR / "config" / "default-config.json"):
        self.config_path = config_path
        self.default_path = default_path
        self.config = None
        self.warnings = []

    def load(self):
        logger.info("Загрузка конфигурации")
        user_config = self._read_json(self.config_path)
        default_config = self._read_json(self.default_path)
        if not isinstance(user_config, dict):
            e_text = f"Некорректный формат конфигурации: {self.config_path}"
            logger.error(e_text)
            raise ValueError(e_text)
        if not isinstance(default_config, dict):
            e_text = f"Некорректный формат конфигурации: {self.default_path}"
            logger.error(e_text)
            raise ValueError(e_text)
        if len(default_config) == 0:
            e_text = "Файл default-config.json не содержит настроек."
            logger.error(e_text)
            raise ValueError(e_text)
        merged = {}
        for key in user_config:
            if key not in default_config:
                info_text =  f"[WARNING] Неизвестный параметр '{key}' будет проигнорирован."
                logger.warning(info_text)
                self.warnings.append(info_text)
        for key, default_value in default_config.items():
            if key not in user_config:
                info_text = f"[WARNING] Параметр '{key}' не найден. " + f"Используется значение по умолчанию: {default_value}"
                logger.warning(info_text)
                self.warnings.append(info_text)
                merged[key] = default_value
            else:
                merged[key] = user_config[key]
        for key in required_keys:
            if key not in merged:
                e_text = f"Отсутствует обязательный параметр '{key}'"
                logger.error(e_text)
                raise ValueError(e_text)
        if not isinstance(merged[label_saving_cur_settings], bool):
            e_text = f"{label_saving_cur_settings} должен быть буллевым значением."
            logger.error(e_text)
            raise ValueError(e_text)
        if not isinstance(merged[label_saving_detecting], bool):
            e_text = f"{label_saving_detecting} должен быть буллевым значением."
            logger.error(e_text)
            raise ValueError(e_text)
        if not isinstance(merged[label_avg_distance], int):
            e_text = f"{label_avg_distance} должен быть целым числом."
            logger.error(e_text)
        if not isinstance(merged[label_wood_coef], (float, int)):
            e_text = f"{label_wood_coef} должен быть числом."
            logger.error(e_text)
            raise ValueError(e_text)
        if not isinstance(merged[label_sign_coef], (float, int)):
            e_text = f"{label_sign_coef} должен быть числом."
            logger.error(e_text)
            raise ValueError(e_text)
        if not isinstance(merged[label_length], (float, int)):
            e_text = f"{label_length} должен быть числом."
            logger.error(e_text)
            raise ValueError(e_text)
        if merged[label_avg_distance] < 0:
            e_text = f"{label_avg_distance} должен быть неотрицательным"
            logger.error(e_text)
            raise ValueError(e_text)
        if not (0 <= merged[label_wood_coef] <= 1):
            e_text = f"{label_wood_coef} должен находиться в диапазоне [0, 1]"
            logger.error(e_text)
            raise ValueError(e_text)
        if not (0 <= merged[label_sign_coef] <= 1):
            e_text = f"{label_sign_coef} должен находиться в диапазоне [0, 1]"
            logger.error(e_text)
            raise ValueError(e_text)
        if not merged[label_wood_model].strip():
            e_text = "Имя модели древесины не может быть пустым."
            logger.error(e_text)
            raise ValueError(e_text)
        if not merged[label_sign_model].strip():
            e_text = "Имя модели меток не может быть пустым."
            logger.error(e_text)
            raise ValueError(e_text)
        if not merged:
            e_text = "Не удалось сформировать конфигурацию."
            logger.error(e_text)
            raise ValueError(e_text)
        self.config = AppConfig(
            name_wood_model=merged[label_wood_model],
            name_sign_model=merged[label_sign_model],
            name_photo=merged[label_photo],
            name_volume=merged[label_volume],
            name_count=merged[label_count_circle],
            wood_coef=merged[label_wood_coef],
            sign_coef=merged[label_sign_coef],
            length=merged[label_length],
            avg_distance=merged[label_avg_distance],
            is_saving_current_settings=merged[label_saving_cur_settings],
            is_saving_result_detecting=merged[label_saving_detecting]
        )
    def _read_json(self, path):
        if not os.path.exists(path):
            e_text = f"Файл не найден: {path}"
            logger.error(e_text)
            raise FileNotFoundError(e_text)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            e_text = f"Ошибка формата JSON в файле {path}: {e}"
            logger.error(e_text)
            raise ValueError(e_text)
        except PermissionError:
            e_text = f"Нет доступа к файлу {path}"
            logger.error(e_text)
            raise PermissionError(e_text)

        except UnicodeDecodeError:
            e_text = f"Неверная кодировка файла {path}"
            logger.error(e_text)
            raise ValueError(e_text)
        if not isinstance(data, dict):
            e_text = f"Файл {path} должен содержать JSON-объект."
            logger.error(e_text)
            raise ValueError(e_text)
        return data


    def print_info(self):
        print("\n === ТЕКУЩИЕ НАСТРОЙКИ ===")
        if self.config is None:
            print("\nКонфигурация не загружена.")
            return
        #print(self.config)
        for key, value in asdict(self.config).items():
            print(f"{key}: {value}")
        if self.warnings:
            print("\n === ПРЕДУПРЕЖДЕНИЯ ===")
            for warning in self.warnings:
                print(warning)
        else:
            print("\nПредупреждений нет.")

    def get_config_dict(self):
        if self.config is None:
            e_text = "Конфигурация не загружена."
            logger.error(e_text)
            raise RuntimeError(e_text)
        return asdict(self.config)

    def get_config(self):
        if self.config is None:
            e_text = "Конфигурация не загружена."
            logger.error(e_text)
            raise RuntimeError(e_text)
        return self.config

