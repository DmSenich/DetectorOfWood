import os
from pathlib import Path
import cv2
import numpy as np

from logger import setup_logger
import math

BASE_DIR = Path.cwd()
logger = setup_logger()


class Detector:
    YOLO_CLASS = None
    def __init__(self, config):
        if Detector.YOLO_CLASS is None:
            from ultralytics import YOLO
            Detector.YOLO_CLASS = YOLO
        if config is None:
            e_text = "Config не может быть None."
            logger.error(e_text)
            raise ValueError(e_text)
        self.INPUT_DIR = BASE_DIR / "data" / "input-images"
        self.config = config

    def load(self):
        try:
            self._load_models()
        except Exception as e:
            e_text = f"Ошибка загрузки моделей: {e}"
            logger.error(e_text)
            raise RuntimeError(e_text)

    def _load_models(self):
        wood_path = BASE_DIR / f"models/{self.config.name_wood_model}"
        sign_path = BASE_DIR / f"models/{self.config.name_sign_model}"
        logger.info("Загрузка моделей")
        self.wood_model = self._load_model(wood_path, "wood")
        logger.info("Модель wood успешно загружена")
        self.sign_model = self._load_model(sign_path, "sign")
        logger.info("Модель sign успешно загружена")

    def _load_model(self, path, name):
        if not os.path.exists(path):
            e_text = f"Не найдена модель: {path}"
            logger.error(e_text)
            raise FileNotFoundError(e_text)
        try:
            model = self.YOLO_CLASS(path)
            dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
            model.predict(
                source=dummy_img,
                save=False,
                verbose=False
            )
            info_text = f"Модель {name} успешно проверена: {path}"
            logger.info(info_text)
            print(info_text)
            return model
        except Exception as e:
            e_text = f"Ошибка загрузки модели {name}: {e}"
            logger.error(e_text)
            raise RuntimeError(e_text)


    # def get_model(self):
    #     print(model)

    def detecting_all(self, list_img):
        data = []
        if not list_img:
            return []
        if not isinstance(list_img, list):
            e_text = "list_img должен быть списком"
            logger.error(e_text)
            raise ValueError(e_text)

        for file in list_img:
            try:
                full_path = os.path.join(self.INPUT_DIR, file)
                distance = self._sign_detecting(full_path)
                diametrs = self._wood_detecting(full_path)
                if not distance:
                    if self.config.avg_distance > 0:
                        info_text = "Не удалось вычислить масштаб, используется среднее значение из конфигурации"
                        logger.warning(info_text)
                        distance = self.config.avg_distance
                    else:
                        info_text = "Не удалось вычислить масштаб"
                        logger.warning(info_text)
                        data.append({self.config.name_photo: file, self.config.name_volume: 0,self.config.name_count: 0})
                        continue
                if not diametrs:
                    e_text = f"Бревна не обнаружены на изображении {file}"
                    logger.warning(e_text)
                    print(e_text)
                    data.append({self.config.name_photo: file, self.config.name_volume: 0,
                                 self.config.name_count: 0})
                    continue
                # len_pix = _detecting(file)
                #print("Полученные длины и масштаб", distance, diametrs)
                volume, count_circle = self.calculating(distance, diametrs)
                if volume is None or volume < 0:
                    volume = 0
                data.append({self.config.name_photo: file, self.config.name_volume: volume, self.config.name_count: count_circle})
            except Exception as e:
                e_text = f"Ошибка обработки {file}: {e}"
                logger.error(e_text)
                print(e_text)
                continue
        # print(data)
        return data

    def _wood_detecting(self, img_path):
        result_woods = self.wood_model.predict(
            source=img_path,
            conf=self.config.wood_coef,
            save=False,
            verbose=False
        )
        diametrs = []
        for r in result_woods:
            boxes = r.boxes
            for box in boxes:
                x1,y1,x2,y2 = box.xyxy[0].tolist()
                diametr = int((x2-x1 + y2 - y1) / 2)
                diametrs.append(diametr)
        if self.config.is_saving_result_detecting:
            annotated_img = result_woods[0].plot(labels=False)
            os.makedirs(BASE_DIR/"data/output-images", exist_ok=True)
            filename = os.path.splitext(os.path.basename(img_path))[0]
            output_path = BASE_DIR / f"data/output-images/{filename}_woods.png"
            cv2.imwrite(output_path, annotated_img)
        return diametrs

    def _sign_detecting(self, img_path):
        results = self.sign_model.predict(
            source=img_path,
            conf=self.config.sign_coef,
            save=False,
            verbose=False
        )
        centers = []
        distance = None
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1,y1,x2,y2 = box.xyxy[0].tolist()
                x1 = int(x1)
                x2 = int(x2)
                y1 = int(y1)
                y2 = int(y2)
                center_x = int((x1 + x2) / 2)
                center_y = int((y1+y2)/2)
                centers.append((center_x, center_y))
        centers.sort()
        if len(centers) == 2:
            x1,y1 = centers[0]
            x2,y2 = centers[1]
            distance = int(math.sqrt(
                (x2 - x1)**2 + (y2-y1)**2
            ))
        if distance is None or distance <= 0:
            return None
        if self.config.is_saving_result_detecting:
            annotated_img = results[0].plot(labels=False)
            os.makedirs(BASE_DIR / "data"/"output-images", exist_ok=True)
            filename = os.path.splitext(os.path.basename(img_path))[0]
            output_path = BASE_DIR / f"data/output-images/{filename}_signs.png"
            cv2.imwrite(output_path,annotated_img)
        return distance

    def calculating(self, distance, diametrs):
        scale = 1.0 / distance
        diams = [pix * scale for pix in diametrs]
        sum_square = sum([d*d for d in diams])/4 * math.pi
        length = self.config.length
        if length <= 0:
            return 0,0
        volume = sum_square * length
        count_circle = len(diametrs)
        return volume, count_circle