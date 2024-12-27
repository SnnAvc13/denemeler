import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QFileDialog, QLabel, QSlider, QHBoxLayout,
                            QFrame, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont
from PyQt5.QtCore import Qt
import cv2
import numpy as np
import os

class PixelArtConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Pixel Art Dönüştürücü')
        self.setGeometry(100, 100, 800, 500)  # Daha küçük pencere boyutu
        self.setMinimumSize(700, 450)  # Daha küçük minimum boyut
        
        # Modern ve soft renkler
        self.colors = {
            'bg': '#1a1b1e',
            'card': '#252731',
            'primary': '#6366f1',
            'secondary': '#22d3ee',
            'text': '#e2e8f0',
            'text_secondary': '#94a3b8'
        }
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['bg']};
            }}
            QLabel {{
                color: {self.colors['text']};
                font-size: 13px;
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['secondary']};
            }}
            QSlider::groove:horizontal {{
                border: none;
                height: 4px;
                background: #4a4a4a;
                margin: 0px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {self.colors['secondary']};
                border: none;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
        """)
        
        self.init_ui()
        
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.create_control_panel()
        self.create_image_container()
        
        self.image_path = None
        self.pixel_size = 12

    def create_control_panel(self):
        control_panel = QWidget()
        control_panel.setFixedHeight(70)
        control_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['card']};
                border-radius: 8px;
            }}
        """)
        
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 10, 15, 10)
        control_layout.setSpacing(20)
        
        # Resim Seç butonu
        self.select_button = QPushButton('Resim Seç')
        self.select_button.setFixedWidth(100)
        self.select_button.setCursor(Qt.PointingHandCursor)
        self.select_button.clicked.connect(self.select_image)
        
        # Slider grubu
        slider_widget = QWidget()
        slider_layout = QVBoxLayout(slider_widget)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        
        slider_header = QHBoxLayout()
        slider_label = QLabel('Pixel Boyutu')
        self.size_value_label = QLabel('12')
        self.size_value_label.setStyleSheet(f"color: {self.colors['secondary']};")
        slider_header.addWidget(slider_label)
        slider_header.addWidget(self.size_value_label)
        
        self.pixel_slider = QSlider(Qt.Horizontal)
        self.pixel_slider.setFixedWidth(200)
        self.pixel_slider.setMinimum(2)
        self.pixel_slider.setMaximum(32)
        self.pixel_slider.setValue(12)
        self.pixel_slider.valueChanged.connect(self.update_size_label)
        self.pixel_slider.valueChanged.connect(self.update_pixel_art)
        
        slider_layout.addLayout(slider_header)
        slider_layout.addWidget(self.pixel_slider)
        
        # Kaydet butonu
        self.save_button = QPushButton('Kaydet')
        self.save_button.setFixedWidth(100)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self.save_image)
        
        control_layout.addWidget(self.select_button)
        control_layout.addWidget(slider_widget)
        control_layout.addWidget(self.save_button)
        
        self.main_layout.addWidget(control_panel)

    def create_image_container(self):
        image_container = QWidget()
        image_layout = QHBoxLayout(image_container)
        image_layout.setSpacing(10)  # Boşluk azaltıldı
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        # Orijinal görüntü frame'i
        original_frame = QFrame()
        original_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['card']};
                border-radius: 8px;
                padding: 8px;
                min-width: 250px;  # Daha küçük minimum genişlik
                min-height: 250px;  # Daha küçük minimum yükseklik
                max-width: 300px;  # Maksimum genişlik eklendi
                max-height: 300px;  # Maksimum yükseklik eklendi
            }}
        """)
        original_layout = QVBoxLayout(original_frame)
        original_layout.setAlignment(Qt.AlignCenter)
        original_layout.setContentsMargins(5, 5, 5, 5)  # Kenar boşlukları azaltıldı
        original_title = QLabel('Orijinal Görüntü')
        original_title.setAlignment(Qt.AlignCenter)
        self.original_label = QLabel()
        self.original_label.setAlignment(Qt.AlignCenter)
        original_layout.addWidget(original_title)
        original_layout.addWidget(self.original_label)
        
        # Pixel art görüntü frame'i
        pixelated_frame = QFrame()
        pixelated_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['card']};
                border-radius: 8px;
                padding: 8px;
                min-width: 250px;  # Daha küçük minimum genişlik
                min-height: 250px;  # Daha küçük minimum yükseklik
                max-width: 300px;  # Maksimum genişlik eklendi
                max-height: 300px;  # Maksimum yükseklik eklendi
            }}
        """)
        pixelated_layout = QVBoxLayout(pixelated_frame)
        pixelated_layout.setAlignment(Qt.AlignCenter)
        pixelated_layout.setContentsMargins(5, 5, 5, 5)  # Kenar boşlukları azaltıldı
        pixelated_title = QLabel('Pixel Art')
        pixelated_title.setAlignment(Qt.AlignCenter)
        self.pixelated_label = QLabel()
        self.pixelated_label.setAlignment(Qt.AlignCenter)
        pixelated_layout.addWidget(pixelated_title)
        pixelated_layout.addWidget(self.pixelated_label)
        
        image_layout.addWidget(original_frame)
        image_layout.addWidget(pixelated_frame)
        self.main_layout.addWidget(image_container)

    def update_size_label(self, value):
        self.size_value_label.setText(str(value))
        self.pixel_size = value
        self.update_pixel_art()

    def select_image(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, 
                "Resim Seç", 
                "", 
                "Image Files (*.png *.jpg *.jpeg *.bmp)"
            )
            if file_name:
                # Dosya yolunu normalize et
                self.image_path = os.path.normpath(file_name)
                self.show_images()
        except Exception as e:
            print(f"Dosya seçme hatası: {e}")

    def pixelate_image(self, image, pixel_size):
        try:
            h, w = image.shape[:2]
            # Çok küçük değerler için kontrol
            if w // pixel_size == 0 or h // pixel_size == 0:
                return image
                
            small = cv2.resize(
                image, 
                (max(1, w // pixel_size), max(1, h // pixel_size)), 
                interpolation=cv2.INTER_LINEAR
            )
            output = cv2.resize(
                small, 
                (w, h), 
                interpolation=cv2.INTER_NEAREST
            )
            return output
        except Exception as e:
            print(f"Pixelate hatası: {e}")
            return image

    def show_images(self):
        try:
            if self.image_path:
                # NumPy array olarak dosyayı oku
                img_array = np.fromfile(self.image_path, dtype=np.uint8)
                # OpenCV ile decode et
                original = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                if original is None:
                    print(f"Görüntü yüklenemedi: {self.image_path}")
                    return
                    
                original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
                pixelated = self.pixelate_image(original, self.pixel_size)
                
                # Görüntü boyutlarını ayarla
                max_size = 250
                h, w = original.shape[:2]
                scale = min(max_size / h, max_size / w)
                new_size = (int(w * scale), int(h * scale))
                
                # Orijinal görüntü
                original_qt = QImage(original.data, w, h, 3 * w, QImage.Format_RGB888)
                original_pixmap = QPixmap.fromImage(original_qt).scaled(
                    *new_size, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.original_label.setPixmap(original_pixmap)
                
                # Pixel art görüntü
                pixelated_qt = QImage(pixelated.data, w, h, 3 * w, QImage.Format_RGB888)
                pixelated_pixmap = QPixmap.fromImage(pixelated_qt).scaled(
                    *new_size, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.pixelated_label.setPixmap(pixelated_pixmap)
                
                # Başarılı yükleme mesajı
                print(f"Görüntü başarıyla yüklendi: {self.image_path}")
                
        except Exception as e:
            print(f"Görüntü işleme hatası: {e}")
            import traceback
            traceback.print_exc()  # Detaylı hata mesajı

    def update_pixel_art(self):
        self.pixel_size = self.pixel_slider.value()
        self.show_images()

    def save_image(self):
        if not hasattr(self, 'image_path') or not self.image_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir resim seçin!")
            return

        try:
            # Varsayılan dosya adını hazırla
            original_name = os.path.splitext(os.path.basename(self.image_path))[0]
            default_name = f"{original_name}_pixel_art.png"
            
            # Kaydetme dialogunu aç
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Pixel Art'ı Kaydet",
                default_name,
                "PNG (*.png);;JPEG (*.jpg)"
            )
            
            if file_name:
                # Orijinal görüntüyü yükle
                img_array = np.fromfile(self.image_path, dtype=np.uint8)
                original = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                if original is None:
                    raise Exception("Orijinal görüntü yüklenemedi")
                
                # Pixel art dönüşümünü yap
                pixelated = self.pixelate_image(original, self.pixel_size)
                
                # Dosya uzantısını kontrol et ve gerekirse ekle
                if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_name += '.png'
                
                # Görüntüyü kaydet
                is_success = False
                if file_name.lower().endswith(('.jpg', '.jpeg')):
                    # JPEG olarak kaydet
                    is_success, buf = cv2.imencode('.jpg', pixelated, [cv2.IMWRITE_JPEG_QUALITY, 95])
                else:
                    # PNG olarak kaydet
                    is_success, buf = cv2.imencode('.png', pixelated)
                
                if is_success:
                    with open(file_name, 'wb') as f:
                        buf.tofile(f)
                    
                    # Dosyanın başarıyla oluşturulduğunu kontrol et
                    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
                        QMessageBox.information(
                            self,
                            "Başarılı",
                            f"Görüntü başarıyla kaydedildi:\n{file_name}",
                            QMessageBox.Ok
                        )
                    else:
                        raise Exception("Dosya oluşturulamadı")
                else:
                    raise Exception("Görüntü kodlama hatası")
                
        except Exception as e:
            error_msg = str(e)
            print(f"Kaydetme hatası: {error_msg}")
            QMessageBox.critical(
                self,
                "Hata",
                f"Görüntü kaydedilirken bir hata oluştu:\n{error_msg}",
                QMessageBox.Ok
            )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern görünüm için Fusion stilini kullan
    converter = PixelArtConverter()
    converter.show()
    sys.exit(app.exec_())
