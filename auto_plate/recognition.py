import cv2
import easyocr
import numpy as np
from moviepy.editor import VideoFileClip

import datetime
import os
from datetime import timedelta
from turtle import shape
from typing import Any, Dict, Tuple, Union

from .constants import *
from .regions import regions
from .work_with_database import find_by_plate_number


def format_timedelta(td: Any) -> str:
    """
    Преобразует дату в нужный формат.
    Utility function to format timedelta objects in a cool way (e.g 00:00:20.05)
    omitting microseconds and retaining milliseconds.
    """
    result = str(td)
    try:
        result, ms = result.split('.')
    except ValueError:
        return result + '.00'.replace(':', '-')
    ms = int(ms)
    ms = round(ms / 1e4)
    return f'{result}.{ms:02}'.replace(':', '-')


def extract_frames_from_video(video_file: str) -> str:
    """
    Извлекает кадры из видео.

    :param video_file: путь к видео для разбивания на кадры.
    :return: путь к папке с полученными изображениями.
    """

    video_clip = VideoFileClip(video_file)
    file_name, _ = os.path.splitext(video_file)
    now = datetime.datetime.now().strftime('%d.%m.%Y %H %M')
    file_name += f' {now}'
    if not os.path.isdir(file_name):
        os.mkdir(file_name)

    saving_frames_per_second = min(video_clip.fps, SAVING_FRAMES_PER_SECOND)
    step = 1 / video_clip.fps if saving_frames_per_second == 0 else 1 / saving_frames_per_second
    for current_duration in np.arange(0, video_clip.duration, step):
        frame_duration_formatted = format_timedelta(timedelta(seconds=current_duration)).replace(':', '-')
        frame_file_name = os.path.join(file_name, f'frame{frame_duration_formatted}.jpg')
        video_clip.save_frame(frame_file_name, current_duration)
    return file_name


def recognition(image: {shape}) -> Tuple:
    """
    Распознавание автомобильного номера на фотографии.

    :param image: изображение для распознавания.
    :return: результат распознавания.
    """

    height, width, _ = image.shape
    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    cascade_classifier = cv2.CascadeClassifier(
        f'{cv2.data.haarcascades}haarcascade_russian_plate_number.xml')
    detected_plate = cascade_classifier.detectMultiScale(image_grey, minSize=(50, 50))
    x, y, w, h = detected_plate[0][0], detected_plate[0][1], detected_plate[0][2], detected_plate[0][3],
    image_for_detected = image[y:y + h, x:x + w]
    reader = easyocr.Reader(['en'])
    result_after_recognition = reader.readtext(image_for_detected)

    best_result_recognition = best_result(result_after_recognition)
    flag_exist_vertical_line = True if VERTICAL_LINE in best_result_recognition[INDEX_STRING_RESULT_RECOGNITION] else False
    if flag_exist_vertical_line:
        best_result_recognition = (
            best_result_recognition[0],
            best_result_recognition[INDEX_STRING_RESULT_RECOGNITION].replace(VERTICAL_LINE, ''),
            best_result_recognition[2],
        )

    return best_result_recognition


def best_result(result_and_exact) -> Tuple:
    """
    Определяет лучшую точность и соответствующий ей результат.

    :param result_and_exact: список кортежей с результатом и его точностью.
    :return: лучший по точности результат.
    """

    max_accuracy = 0
    max_result = ''
    for result in result_and_exact:
        if result[2] > max_accuracy:
            max_accuracy = result[2]
            max_result = result
    return max_result


def best_plate_number(result_and_exact) -> str:
    """
    Определяет лучшую точность и соответствующий ей результат.

    :param result_and_exact: список кортежей с результатом и его точностью.
    :return: лучший по точности результат.
    """

    max_accuracy = 0
    max_result = ''
    for result in result_and_exact:
        if result[2] > max_accuracy:
            max_accuracy = result[2]
            max_result = result[1]
    return max_result


def best_plate_number_and_accuracy(result_and_exact) -> Tuple:
    """
    Определяет лучшую точность и соответствующий ей результат.

    :param result_and_exact: список кортежей с результатом и его точностью.
    :return: лучший по точности результат.
    """

    max_accuracy = 0
    max_result = ''
    for result in result_and_exact:
        if result[2] > max_accuracy:
            max_accuracy = result[2]
            max_result = result[1]
    return (max_result, max_accuracy)


def get_region(plate_number: str) -> Dict:
    """
    Функция, возвращающая название региона для автомобильного номера.

    :param plate_number: автомобильный номер.
    :return: словарь с данными и ошибками.
    """

    context = {}
    if len(plate_number) > 6:
        code_region = plate_number[6:]
        region = regions.get(code_region)
        context['data'] = region
    else:
        context['error'] = ERROR_NUMBER_DOESNT_HAVE_REGION

    return context


def main_recognition(file: str) -> Union[Union[Tuple[Any, ...], tuple], Any]:
    """
    Основная функция.
    Определяет, поступивший файл - это картинка или изорбражение,
     и вызывает необходимую функцию для распознавания данного файла.

    :param file: путь к файлу.
    :return: номер автомобиля из файла.
    """

    _, file_extension = os.path.splitext(file)

    if file_extension in ALLOWED_EXTENSION_FOR_IMAGE:
        image = cv2.imread(file)
        return recognition(image)[INDEX_STRING_RESULT_RECOGNITION]

    if file_extension in ALLOWED_EXTENSION_FOR_VIDEO:
        directory_name = extract_frames_from_video(video_file=file)
        result_and_exact = []
        for file_name in os.listdir(directory_name):
            image = cv2.imread(os.path.join(directory_name, file_name))
            result_and_exact.append(recognition(image))
        return best_plate_number_and_accuracy(result_and_exact)
