import os
import random
import json
import datetime
import asyncio
import piexif
from PIL import Image, ImageOps, ImageEnhance

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

class iPhoneImageProcessorApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.name, size=(380, 620))
        
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=25))

        # --- En-tête ---
        title_label = toga.Label(
            '✨ Randomizer & EXIF Pro', 
            style=Pack(padding=(0, 0, 5, 0), font_weight='bold', font_size=18)
        )
        subtitle_label = toga.Label(
            'Recadrage, Jitter & EXIF iPhone natifs', 
            style=Pack(padding=(0, 0, 20, 0), color='#666666', font_size=12)
        )

        # --- Section 1 : Sélection du dossier ---
        self.btn_input = toga.Button(
            '📁 Choisir le dossier source', 
            on_press=self.select_input_folder,
            style=Pack(padding=(0, 0, 5, 0), height=40)
        )
        self.label_input = toga.Label(
            'Aucun dossier sélectionné', 
            style=Pack(padding=(0, 0, 15, 0), color='#888888', font_size=11)
        )

        # --- Section 2 : Configuration ---
        config_box = toga.Box(style=Pack(direction=ROW, padding=(0, 0, 20, 0), alignment=CENTER))
        lbl_folders = toga.Label('Nombre de dossiers :', style=Pack(flex=1))
        
        self.num_folders_input = toga.NumberInput(
            value=10, 
            step=1, 
            min=1, 
            max=50,
            style=Pack(width=80)
        )
        config_box.add(lbl_folders)
        config_box.add(self.num_folders_input)

        # --- Section 3 : Bouton d'action ---
        self.btn_run = toga.Button(
            '🚀 Lancer le traitement', 
            on_press=self.start_processing_thread,
            style=Pack(padding=(0, 0, 15, 0), height=45),
            enabled=False
        )

        # --- Section 4 : Progression ---
        self.progress_bar = toga.ProgressBar(
            max=100, 
            value=0, 
            style=Pack(padding=(0, 0, 10, 0))
        )
        self.status_label = toga.Label(
            'En attente...', 
            style=Pack(padding=(0, 0, 10, 0), font_size=12, alignment=CENTER)
        )

        main_box.add(title_label)
        main_box.add(subtitle_label)
        main_box.add(self.btn_input)
        main_box.add(self.label_input)
        main_box.add(config_box)
        main_box.add(self.btn_run)
        main_box.add(self.progress_bar)
        main_box.add(self.status_label)

        self.main_window.content = main_box
        self.main_window.show()

    async def select_input_folder(self, widget):
        try:
            folder_path = await self.main_window.select_folder_dialog(
                title="Sélectionner le dossier de photos"
            )
            if folder_path:
                self.input_folder = str(folder_path)
                folder_name = folder_path.name if hasattr(folder_path, 'name') else str(folder_path).split('/')[-1]
                self.label_input.text = f"Source : .../{folder_name}"
                self.btn_run.enabled = True
        except Exception as e:
            self.label_input.text = f"Erreur de sélection"

    # --- LOGIQUE MÉTIER & ANTI-SPAM ---
    IPHONE_MODELS = [
        {"make": "Apple", "model": "iPhone 11", "software": "16.5", "focal": (26, 1), "fnum": (18, 10)},
        {"make": "Apple", "model": "iPhone 12", "software": "17.1.1", "focal": (26, 1), "fnum": (16, 10)},
        {"make": "Apple", "model": "iPhone 13", "software": "17.4", "focal": (26, 1), "fnum": (16, 10)},
        {"make": "Apple", "model": "iPhone 14", "software": "17.5.1", "focal": (26, 1), "fnum": (15, 10)},
        {"make": "Apple", "model": "iPhone 15", "software": "17.6", "focal": (24, 1), "fnum": (16, 10)},
    ]

    def get_history_path(self):
        return os.path.join(self.paths.app_data, "used_file_names.json")

    def load_history(self):
        history_file = self.get_history_path()
        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as f:
                    return set(json.load(f))
            except Exception:
                return set()
        return set()

    def save_history(self, history_set):
        history_file = self.get_history_path()
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        with open(history_file, "w") as f:
            json.dump(list(history_set), f)

    def generate_unique_filename(self, used_numbers_set):
        while True:
            rand_num = random.randint(1000, 9999)
            if rand_num not in used_numbers_set:
                used_numbers_set.add(rand_num)
                return f"IMG_{rand_num}.jpg"

    def generate_iphone_exif(self):
        device = random.choice(self.IPHONE_MODELS)
        now = datetime.datetime.now()
        random_days = random.randint(1, 30)
        random_seconds = random.randint(0, 86400)
        photo_date = now - datetime.timedelta(days=random_days, seconds=random_seconds)
        date_str = photo_date.strftime("%Y:%m:%d %H:%M:%S")

        zeroth_ifd = {
            piexif.ImageIFD.Make: device["make"].encode('utf-8'),
            piexif.ImageIFD.Model: device["model"].encode('utf-8'),
            piexif.ImageIFD.Software: f"iOS {device['software']}".encode('utf-8'),
            piexif.ImageIFD.Orientation: 1,
            piexif.ImageIFD.XResolution: (72, 1),
            piexif.ImageIFD.YResolution: (72, 1),
            piexif.ImageIFD.ResolutionUnit: 2,
            piexif.ImageIFD.DateTime: date_str.encode('utf-8'),
        }

        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: date_str.encode('utf-8'),
            piexif.ExifIFD.DateTimeDigitized: date_str.encode('utf-8'),
            piexif.ExifIFD.OffsetTimeOriginal: b"+03:00",
            piexif.ExifIFD.ColorSpace: 1,
            piexif.ExifIFD.ExifVersion: b"0232",
            piexif.ExifIFD.ComponentsConfiguration: b"\x01\x02\x03\x00",
            piexif.ExifIFD.FocalLength: device["focal"],
            piexif.ExifIFD.FNumber: device["fnum"],
            piexif.ExifIFD.ISOSpeedRatings: random.choice([50, 64, 80, 100, 125, 160]),
            piexif.ExifIFD.LensModel: f"{device['model']} back camera 5.96mm f/{device['fnum'][0]/10}".encode('utf-8'),
        }

        exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "1st": {}, "GPS": {}, "Interop": {}}
        return piexif.dump(exif_dict)

    def dynamic_crop_to_ratio(self, img, target_ratio=(3, 4)):
        orig_w, orig_h = img.size
        target_aspect = target_ratio[0] / target_ratio[1]
        orig_aspect = orig_w / orig_h

        if orig_aspect > target_aspect:
            new_w = int(orig_h * target_aspect)
            new_h = orig_h
            max_offset = orig_w - new_w
            left = random.randint(0, max_offset) if max_offset > 0 else 0
            top = 0
        else:
            new_w = orig_w
            new_h = int(orig_w / target_aspect)
            max_offset = orig_h - new_h
            left = 0
            top = random.randint(0, max_offset) if max_offset > 0 else 0

        return img.crop((left, top, left + new_w, top + new_h))

    def process_single_image(self, img, output_path, target_width=1080):
        # 1. Micro-Flip optionel (15% de chance)
        if random.random() < 0.15:
            img = ImageOps.mirror(img)

        # 2. Recadrage dynamique au format 3:4 (pour atteindre 1080x1440)
        img_cropped = self.dynamic_crop_to_ratio(img, target_ratio=(3, 4))
        target_height = int(target_width * (4 / 3))
        img_resized = img_cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # 3. Micro-rotation anti-pHash (-0.5° à +0.5°)
        angle = random.uniform(-0.5, 0.5)
        img_rotated = img_resized.rotate(angle, resample=Image.BICUBIC, expand=False)

        # 4. Légères variations colorimétriques invisibles pour casser la signature binaire
        img_rotated = ImageEnhance.Brightness(img_rotated).enhance(random.uniform(0.97, 1.03))
        img_rotated = ImageEnhance.Contrast(img_rotated).enhance(random.uniform(0.97, 1.03))
        img_rotated = ImageEnhance.Color(img_rotated).enhance(random.uniform(0.98, 1.02))

        # 5. Sauvegarde en JPEG avec qualité variable (génère des tailles de fichiers uniques en Ko)
        # et injection directe des métadonnées EXIF iPhone
        exif_bytes = self.generate_iphone_exif()
        
        img_rotated.save(
            output_path,
            format="JPEG",
            quality=random.randint(92, 96),
            optimize=True,
            exif=exif_bytes
        )

    async def start_processing_thread(self, widget):
        self.btn_run.enabled = False
        self.btn_input.enabled = False
        
        num_folders = int(self.num_folders_input.value)
        output_base_folder = os.path.join(str(self.paths.documents), "photos_traitees")
        
        await asyncio.to_thread(self.run_processing_logic, self.input_folder, output_base_folder, num_folders)
        
        self.btn_run.enabled = True
        self.btn_input.enabled = True

    def run_processing_logic(self, input_folder, output_base_folder, num_folders):
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
        input_files = [f for f in os.listdir(input_folder) if f.lower().endswith(valid_extensions)]
        
        if not input_files:
            self.status_label.text = "[-] Aucune image trouvée."
            return

        used_numbers_set = self.load_history()
        total_steps = num_folders * len(input_files)
        current_step = 0

        for folder_idx in range(1, num_folders + 1):
            subfolder_name = f"dossier_{folder_idx}"
            subfolder_path = os.path.join(output_base_folder, subfolder_name)
            os.makedirs(subfolder_path, exist_ok=True)

            for filename in input_files:
                in_path = os.path.join(input_folder, filename)
                out_filename = self.generate_unique_filename(used_numbers_set)
                out_path = os.path.join(subfolder_path, out_filename)

                try:
                    with Image.open(in_path) as img:
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        img = ImageOps.exif_transpose(img)
                        self.process_single_image(img, out_path)
                except Exception as e:
                    print(f"Erreur sur {filename} : {e}")

                current_step += 1
                progress = int((current_step / total_steps) * 100)
                self.progress_bar.value = progress
                self.status_label.text = f"Traitement : {current_step}/{total_steps} images"

        self.save_history(used_numbers_set)
        self.status_label.text = "✓ Traitement terminé avec succès !"

def main():
    return iPhoneImageProcessorApp('Randomizer CAMARA', 'org.example.randomizer')

if __name__ == '__main__':
    main().main_loop()
