import cv2
import numpy as np

def show_img(img):
    cv2.imshow('img', img)
    cv2.waitKey()

image = cv2.imread('/home/tamnv/Downloads/picofme.png')

h, w, _ = image.shape

# Kích thước của viền và độ dịch chuyển của bóng
border_size = 50
shadow_offset = 10

# Màu nền và màu bóng
background_color = [255, 255, 255]  # Màu cam trong BGR
shadow_color = [128, 128, 128]    # Màu xám trong BGR

# Tạo ảnh nền màu cam lớn hơn
background = np.ones((h + 2*border_size + shadow_offset, w + 2*border_size + shadow_offset, 3), dtype=np.uint8) * background_color
background = background.astype(np.uint8)

# Tạo một ảnh cùng kích thước với ảnh nền để chứa bóng xám
shadow_layer = np.zeros_like(background)

# Vẽ hình ảnh bóng màu xám xung quanh
shadow_layer[border_size + shadow_offset:border_size + h + shadow_offset, border_size + shadow_offset:border_size + w + shadow_offset] = shadow_color
shadow_layer = shadow_layer.astype(np.uint8)

# Làm mờ bóng để tạo hiệu ứng mềm mại
shadow_layer = cv2.GaussianBlur(shadow_layer, (21, 21), 10)


background = cv2.addWeighted(background, 1, shadow_layer, 0.5, 0)

# Đặt ảnh gốc lên ảnh nền
background[border_size:border_size+h, border_size:border_size+w] = image
show_img(background)