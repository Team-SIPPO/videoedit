import unittest
import videoedit.edit as edit
import numpy as np
import importlib
importlib.reload(edit)


class TestEdit(unittest.TestCase):
    def test_generate_mask(self):
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
    
    def test_scale_and_crop_mask(self):
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
        text_img = edit.fill_color_with_mask(text_img, text_mask, color=(255, 0, 0))
        # import matplotlib.pyplot as plt
        # plt.imshow(text_img)
        # plt.show()

        mask = text_mask.copy()
        scaled_mask = edit.scale_and_crop_mask(
            mask,
            scale_ratio=1.0,
            mask_center_x=None,
            mask_center_y=None
        )
        
        text_img = np.ones((1080, 1920, 3), dtype="uint8") * 255
        text_img = edit.fill_color_with_mask(text_img, text_mask, color=(255, 0, 0))
        # plt.imshow(text_img)
        # plt.show()

if __name__ == '__main__':
    unittest.main()