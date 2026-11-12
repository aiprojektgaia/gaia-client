from PyQt5.QtGui import QValidator


class BboxValidator(QValidator):
    def validate(self, text:str, pos:int) -> tuple[int, str, int]:
        # Check if the text is empty
        if not text:
            return QValidator.Invalid, text, pos

        # Check if it is a bounding box

        bbox_text = text.strip()
        if len(bbox_text) == 0:
            return QValidator.Invalid, text, pos
        try:
            bbox = [float(coord) for coord in bbox_text.split(",")]
            if len(bbox) != 4:
                return QValidator.Invalid, text, pos
            else :
                min_x, max_y, max_x, min_y = bbox
                if min_x >= max_x or min_y >= max_y:
                    return QValidator.Invalid, text, pos
            return QValidator.Acceptable, text, pos
        except ValueError:
            return QValidator.Invalid, text, pos
