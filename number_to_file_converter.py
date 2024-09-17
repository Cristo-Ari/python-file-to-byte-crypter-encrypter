import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class FileDecryptor:
    def __init__(self, bit_sequence):
        self.bit_sequence = bit_sequence
        self.file_name = None

    def bits_to_file(self, output_folder_path):
        # Извлекаем длину имени файла (16 бит)
        file_name_length_bits = self.bit_sequence[:16]
        file_name_length = int(file_name_length_bits, 2) * 8  # длина в битах
        
        # Извлекаем имя файла
        file_name_bits = self.bit_sequence[16:16 + file_name_length]
        file_name_bytes = bytearray(int(file_name_bits[i:i+8], 2) for i in range(0, len(file_name_bits), 8))
        self.file_name = file_name_bytes.decode('utf-8')

        # Оставшиеся биты для данных и метаданных
        remaining_bits = self.bit_sequence[16 + file_name_length:]
        file_data_bits = remaining_bits[:-192]
        metadata_bits = remaining_bits[-192:]

        # Преобразуем битовую последовательность в байты
        file_data_bytes = bytearray(int(file_data_bits[i:i+8], 2) for i in range(0, len(file_data_bits), 8))

        # Сохраняем данные в файл
        output_file_path = os.path.join(output_folder_path, self.file_name)
        with open(output_file_path, 'wb') as file:
            file.write(file_data_bytes)

        # Восстанавливаем метаданные
        created_time, modified_time, access_time = (
            struct.unpack('!d', struct.pack('!Q', int(metadata_bits[i:i+64], 2)))[0]
            for i in range(0, 192, 64)
        )
        os.utime(output_file_path, (access_time, modified_time))
        if hasattr(os, 'setctime'):
            os.setctime(output_file_path, created_time)

def select_bit_file():
    file_path = filedialog.askopenfilename(title="Выберите файл с битами")
    if file_path:
        return file_path
    return None

def select_folder():
    folder_path = filedialog.askdirectory(title="Выберите папку для сохранения")
    if folder_path:
        return folder_path
    return None

def load_bit_sequence_from_file():
    file_path = select_bit_file()
    if not file_path:
        messagebox.showerror("Ошибка", "Файл с битами не выбран")
        return

    with open(file_path, 'r') as file:
        bit_sequence = file.read()

    folder_path = select_folder()
    if not folder_path:
        messagebox.showerror("Ошибка", "Папка для сохранения не выбрана")
        return

    decryptor = FileDecryptor(bit_sequence)
    decryptor.bits_to_file(folder_path)

    messagebox.showinfo("Успех", f"Файл успешно восстановлен в папке: {folder_path}")

def manual_input_bit_sequence(text_widget):
    bit_sequence = text_widget.get("1.0", tk.END).strip()

    if not bit_sequence:
        messagebox.showerror("Ошибка", "Последовательность битов не введена")
        return

    folder_path = select_folder()
    if not folder_path:
        messagebox.showerror("Ошибка", "Папка для сохранения не выбрана")
        return

    decryptor = FileDecryptor(bit_sequence)
    decryptor.bits_to_file(folder_path)

    messagebox.showinfo("Успех", f"Файл успешно восстановлен в папке: {folder_path}")

def show_manual_input():
    manual_window = tk.Toplevel(root)
    manual_window.title("Ввести последовательность битов вручную")
    
    text_widget = scrolledtext.ScrolledText(manual_window, wrap=tk.WORD, width=50, height=10)
    text_widget.pack(pady=10)

    convert_button = tk.Button(manual_window, text="Преобразовать в файл", command=lambda: manual_input_bit_sequence(text_widget))
    convert_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Расшифровка файла")

    load_button = tk.Button(root, text="Читать биты из файла", command=load_bit_sequence_from_file)
    load_button.pack(pady=10)

    manual_button = tk.Button(root, text="Ввести биты вручную", command=show_manual_input)
    manual_button.pack(pady=10)

    root.geometry("300x150")
    root.mainloop()
