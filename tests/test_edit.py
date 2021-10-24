import unittest
import videoedit.edit as edit
import numpy as np


class TestEdit(unittest.TestCase):
    def test_generate_mask(self):
        import importlib
        importlib.reload(edit)
        text_mask = edit.generate_mask(
            img_height=1080,
            img_width=1920,
            text="aaa",
            org=(1920 // 2, 1080 // 2),
            color=(0, 0, 0),
            pos="center"
        )
        
        text_img = np.ones((1080, 1920, 3), dtype="uint8") * 255
        text_img[text_mask == True, 0] = 255
        text_img[text_mask == True, 1] = 0
        text_img[text_mask == True, 2] = 0
        
        self.assertTrue(
            np.all(text_img[0, 0, :] == np.array([255, 255, 255]))
        )
        self.assertTrue(
            np.all(text_img[578, 977, :] == np.array([255, 0, 0]))
        )
        import cv2
        cv2.resize(np.repeat(np.expand_dims(text_mask, axis=-1), 3, axis=-1).astype("uint8"), dsize=(200, 100))


if __name__ == '__main__':
    unittest.main()