import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from functools import partial
class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        self.records = []
        self.json_file = "weather_data.json"
        self.setup_input_frame()
        self.setup_filter_frame()
        self.setup_records_table()
        self.setup_button_frame()
        self.load_from_json()
        self.refresh_table()
    def setup_input_frame(self):
        input_frame = ttk.LabelFrame(self.root, text="Добавление записи", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(input_frame, text="Описание погоды:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_entry = ttk.Entry(input_frame, width=50)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W)
        self.precip_var = tk.BooleanVar()
        self.precip_check = ttk.Checkbutton(input_frame, text="Есть осадки", variable=self.precip_var)
        self.precip_check.grid(row=0, column=4, padx=20, pady=5)
    def setup_filter_frame(self):
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация записей", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.filter_date_entry.insert(0, "")
        ttk.Label(filter_frame, text="Температура выше (°C):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=4, padx=10, pady=5)
        ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=5, padx=5, pady=5)
    def setup_records_table(self):
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        self.tree.column("date", width=120)
        self.tree.column("temperature", width=120)
        self.tree.column("description", width=400)
        self.tree.column("precipitation", width=100)
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    def setup_button_frame(self):
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="Добавить запись", command=self.add_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить выбранное", command=self.delete_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_to_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_from_json).pack(side=tk.LEFT, padx=5)
    def validate_date(self, date_string):
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    def validate_temperature(self, temp_string):
        try:
            temp = float(temp_string)
            return True, temp
        except ValueError:
            return False, None
    def add_record(self):
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()
        if not date:
            messagebox.showerror("Ошибка", "Дата не может быть пустой!")
            return
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД (например, 2024-12-25)")
            return
        if not temp_str:
            messagebox.showerror("Ошибка", "Температура не может быть пустой!")
            return
        is_valid_temp, temperature = self.validate_temperature(temp_str)
        if not is_valid_temp:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return
        if not description:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым!")
            return
        record = {
            "date": date,
            "temperature": temperature,
            "description": description,
            "precipitation": "Да" if precipitation else "Нет"
        }
        self.records.append(record)
        self.refresh_table()
        self.clear_input_fields()
        messagebox.showinfo("Успех", "Запись успешно добавлена!")
    def delete_record(self):
        """Delete selected record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            for item in selected:
                item_text = self.tree.item(item, "values")
                for i, record in enumerate(self.records):
                    if (record["date"] == item_text[0] and 
                        record["temperature"] == float(item_text[1]) and
                        record["description"] == item_text[2]):
                        self.records.pop(i)
                        break
            self.refresh_table()
            messagebox.showinfo("Успех", "Запись удалена!")
    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()
        filtered_records = self.records.copy()
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты в фильтре!")
                return
            filtered_records = [r for r in filtered_records if r["date"] == filter_date]
        if filter_temp_str:
            is_valid, temp_threshold = self.validate_temperature(filter_temp_str)
            if not is_valid:
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом!")
                return
            filtered_records = [r for r in filtered_records if r["temperature"] > temp_threshold]
        self.display_records(filtered_records)
    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_table()
    def display_records(self, records):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for record in records:
            self.tree.insert("", tk.END, values=(
                record["date"],
                record["temperature"],
                record["description"],
                record["precipitation"]
            ))
    def refresh_table(self):
        self.display_records(self.records)
    def clear_input_fields(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)
    def save_to_json(self):
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в файл {self.json_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    def load_from_json(self):
        if not os.path.exists(self.json_file):
            return
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.records = json.load(f)
            self.refresh_table()
            messagebox.showinfo("Успех", f"Загружено {len(self.records)} записей")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл поврежден или имеет неверный формат!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
def main():
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
if __name__ == "__main__":
    main()