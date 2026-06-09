import multiprocessing
multiprocessing.set_start_method("spawn", force=True)
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import json
import time
from datetime import datetime
from pathlib import Path

from config_manager import ConfigManager

from detector import *

BASE_DIR = Path.cwd()

INPUT_DIR = BASE_DIR / "data" / "input-images"
OUTPUT_DIR = BASE_DIR / "data" / "output"

def main():

    this_time = datetime.now()
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
    VALID_EXTENSIONS = (".jpg", ".jpeg", ".png")
    listfiles = [f for f in os.listdir(INPUT_DIR)
                 if f.lower().endswith(VALID_EXTENSIONS)]
    info_text = f"Обнаружено изображений: {len(listfiles)}"
    logger.info(info_text)
    #print(info_text)
    if not listfiles:
        info_text = "Файлы для обработки не найдены"
        logger.warning(info_text)
        #print(info_text)
        return
    config_manager = ConfigManager()
    try:
        config_manager.load()
        logger.info("Конфигурация загружена")
    except Exception as e:
        e_text = f"Ошибка загрузки конфигурации: {e}"
        logger.error(e_text)
        #print(e_text)
        return
    config_manager.print_info()
    time.sleep(0.5)
    print("Если хотите продолжить с текущими настройками, оставьте ввод пустым (Нажмите Enter)\nЕсли хотите изменить настройки, завершите приложение (Введите 0, нажмите Enter)")
    choice = input("Ввод: ")
    if choice.strip() == "0":
        return

    config = config_manager.get_config()
    is_saving_current_settings = config.is_saving_current_settings
    try:
        detector = Detector(config)
        detector.load()
        logger.info("Detector инициализирован.")
    except Exception as e:
        e_text = f"Ошибка инициализации Detector: {e}"
        logger.error(e_text)
        print(e_text)
        return
    try:
        output_data = detector.detecting_all(listfiles)
    except Exception as e:
        e_text = f"Ошибка обработки изображений: {e}"
        logger.error(e_text)
        print(e_text)
        return
    if not output_data:
        e_text = "Не удалось обработать ни одного изображения."
        logger.error(e_text)
        print(e_text)
        return

    config_data = config_manager.get_config_dict()
    try:
        save_output_data(output_data, this_time)
        logger.info("Сохранены данные обработки")
        if is_saving_current_settings:
            save_output_params(config_data, this_time)
            logger.info("Сохранены текущие данные конфигурации")
    except Exception as e:
        e_text = f"Ошибка сохранения данных обработки: {e}"
        logger.error(e_text)
        print(e_text)
        return

def save_output_data(output_data, this_time):
    # dt = date.today()
    # print(dt)
    # today = date.today()
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    filename = this_time.strftime("%d-%m-%Y %H-%M-%S.json")
    try:
        with open(os.path.join(OUTPUT_DIR,filename), "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4)
    except OSError as e:
        e_text = f"Ошибка сохранения файла: {e}"
        logger.error(e_text)
        print(e_text)
    print("Сохранение завершено")


def save_output_params(config_data, this_time):
    filename_config = this_time.strftime("%d-%m-%Y %H-%M-%S_settings.json")
    try:
        with open(os.path.join(OUTPUT_DIR,filename_config), "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
    except OSError as e:
        e_text = f"Ошибка сохранения файла: {e}"
        logger.error(e_text)
        print(e_text)
    print("Данные настроек сохранены")


if __name__ == '__main__':
    main()


