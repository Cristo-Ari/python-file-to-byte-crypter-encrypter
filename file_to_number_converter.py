import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox

class FileEncryptor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_data = None
        self.file_metadata = None
        self.file_name = os.path.basename(file_path)

    def read_file(self):
        with open(self.file_path, 'rb') as file:
            self.file_data = file.read()

    def get_file_metadata(self):
        file_stats = os.stat(self.file_path)
        self.file_metadata = {
            'created_time': file_stats.st_ctime,
            'modified_time': file_stats.st_mtime,
            'access_time': file_stats.st_atime
        }

    def file_to_bits(self):
        return ''.join(format(byte, '08b') for byte in self.file_data)

    def metadata_to_bits(self):
        return ''.join(format(struct.unpack('!Q', struct.pack('!d', value))[0], '064b') 
                                for value in self.file_metadata.values())

    def name_to_bits(self):
        file_name_bytes = self.file_name.encode('utf-8')
        file_name_length = len(file_name_bytes)
        file_name_length_bits = format(file_name_length, '016b')  # 16 бит для длины имени
        file_name_bits = ''.join(format(byte, '08b') for byte in file_name_bytes)
        return file_name_length_bits + file_name_bits

    def convert_file_to_bit_sequence(self):
        self.read_file()
        self.get_file_metadata()
        file_data_bits = self.file_to_bits()
        metadata_bits = self.metadata_to_bits()
        file_name_bits = self.name_to_bits()
        return file_name_bits + file_data_bits + metadata_bits

    def save_bit_sequence(self, output_file_path, bit_sequence):
        with open(output_file_path, 'w') as file:
            file.write(bit_sequence)

def select_file():
    file_path = filedialog.askopenfilename(title="Выберите файл для шифрования")
    if file_path:
        return file_path
    return None

def select_folder():
    folder_path = filedialog.askdirectory(title="Выберите папку для сохранения")
    if folder_path:
        return folder_path
    return None

def encrypt_file():
    file_path = select_file()
    if not file_path:
        messagebox.showerror("Ошибка", "Файл не выбран")
        return

    folder_path = select_folder()
    if not folder_path:
        messagebox.showerror("Ошибка", "Папка не выбрана")
        return

    encryptor = FileEncryptor(file_path)
    bit_sequence = encryptor.convert_file_to_bit_sequence()
    
    file_name = os.path.splitext(os.path.basename(file_path))[0] + "_bits.txt"
    output_file_path = os.path.join(folder_path, file_name)
    
    encryptor.save_bit_sequence(output_file_path, bit_sequence)
    messagebox.showinfo("Успех", f"Файл успешно зашифрован и сохранен в {output_file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Шифрование файла")

    encrypt_button = tk.Button(root, text="Выбрать файл для шифрования", command=encrypt_file)
    encrypt_button.pack(pady=20)

    root.geometry("300x150")
    root.mainloop()
