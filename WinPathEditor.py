import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import winreg
import ctypes
import os
import json
import datetime

class PathEditor:
    def __init__(self, root):
        self.root = root
        root.title("Редактор PATH без ограничений")
        root.geometry("700x500")
        root.minsize(600, 400)
        
        # Проверяем права администратора
        if not self.is_admin():
            messagebox.warning("Предупреждение", "Программа запущена без прав администратора. "
                            "Некоторые изменения могут не сохраниться.")
        
        # Фрейм для выбора пользовательской/системной переменной
        selector_frame = ttk.Frame(root, padding="10")
        selector_frame.pack(fill=tk.X)
        
        ttk.Label(selector_frame, text="Выберите тип переменной PATH:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Радиокнопки для выбора типа переменной
        self.var_type = tk.StringVar(value="user")
        ttk.Radiobutton(selector_frame, text="Пользовательская", variable=self.var_type, 
                      value="user", command=self.load_path).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(selector_frame, text="Системная", variable=self.var_type, 
                      value="system", command=self.load_path).pack(side=tk.LEFT)
        
        # Основной фрейм со списком и кнопками
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Список путей
        path_frame = ttk.LabelFrame(main_frame, text="Пути переменной PATH", padding="10")
        path_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем фрейм со скроллбаром для списка
        list_frame = ttk.Frame(path_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Список путей
        self.path_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, font=("Consolas", 10))
        self.path_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Привязываем скроллбар к списку
        self.path_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.path_listbox.yview)
        
        # Кнопки
        button_frame = ttk.Frame(path_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Создать", command=self.add_path).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Редактировать", command=self.edit_path).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Удалить", command=self.delete_path).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Вверх", command=lambda: self.move_path(-1)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Вниз", command=lambda: self.move_path(1)).pack(side=tk.LEFT)
        
        # Кнопки для резервного копирования
        backup_frame = ttk.Frame(root, padding="10")
        backup_frame.pack(fill=tk.X)
        
        ttk.Button(backup_frame, text="Сохранить PATH в файл", command=self.export_path).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(backup_frame, text="Восстановить из файла", command=self.import_path).pack(side=tk.LEFT)
        
        # Кнопки Сохранить и Отмена
        bottom_frame = ttk.Frame(root, padding="10")
        bottom_frame.pack(fill=tk.X)
        
        ttk.Button(bottom_frame, text="Сохранить", command=self.save_path).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(bottom_frame, text="Отмена", command=root.destroy).pack(side=tk.RIGHT)
        
        # Загружаем текущую переменную PATH
        self.load_path()
    
    def is_admin(self):
        """Проверяет, запущена ли программа с правами администратора"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def load_path(self):
        """Загружает текущее значение переменной PATH"""
        self.path_listbox.delete(0, tk.END)
        
        try:
            if self.var_type.get() == "user":
                path_value = self.get_user_path()
            else:
                path_value = self.get_system_path()
            
            # Разделяем строку PATH на отдельные пути
            path_entries = [p for p in path_value.split(';') if p]
            
            # Добавляем пути в список
            for path in path_entries:
                self.path_listbox.insert(tk.END, path)
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить переменную PATH: {str(e)}")
    
    def get_user_path(self):
        """Получает значение пользовательской переменной PATH"""
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, "Path")
            return value
        except:
            return ""
        finally:
            winreg.CloseKey(key)
    
    def get_system_path(self):
        """Получает значение системной переменной PATH"""
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                         r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                         0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, "Path")
            return value
        except:
            return ""
        finally:
            winreg.CloseKey(key)
    
    def add_path(self):
        """Добавляет новый путь в переменную PATH"""
        # Открываем диалог выбора директории
        new_path = filedialog.askdirectory(title="Выберите директорию для добавления в PATH")
        
        if new_path:
            # Проверяем, существует ли уже такой путь
            path_exists = False
            for i in range(self.path_listbox.size()):
                if self.path_listbox.get(i) == new_path:
                    path_exists = True
                    break
            
            if path_exists:
                messagebox.showinfo("Информация", "Указанный путь уже добавлен в переменную PATH")
            else:
                self.path_listbox.insert(tk.END, new_path)
    
    def edit_path(self):
        """Редактирует выбранный путь"""
        selected = self.path_listbox.curselection()
        
        if not selected:
            messagebox.showinfo("Информация", "Выберите путь для редактирования")
            return
        
        current_path = self.path_listbox.get(selected[0])
        
        # Создаем диалоговое окно для редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактировать путь")
        edit_window.geometry("600x100")
        edit_window.resizable(True, False)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Добавляем поле ввода и кнопки
        ttk.Label(edit_window, text="Путь:").pack(side=tk.LEFT, padx=(10, 5), pady=10)
        
        path_var = tk.StringVar(value=current_path)
        path_entry = ttk.Entry(edit_window, width=50, textvariable=path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), pady=10)
        
        def browse_path():
            new_path = filedialog.askdirectory(title="Выберите директорию")
            if new_path:
                path_var.set(new_path)
        
        ttk.Button(edit_window, text="Обзор...", command=browse_path).pack(side=tk.LEFT, padx=(0, 10), pady=10)
        
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def save_edit():
            new_path = path_var.get()
            if new_path:
                self.path_listbox.delete(selected[0])
                self.path_listbox.insert(selected[0], new_path)
            edit_window.destroy()
        
        ttk.Button(button_frame, text="OK", command=save_edit).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Отмена", command=edit_window.destroy).pack(side=tk.RIGHT)
    
    def delete_path(self):
        """Удаляет выбранный путь"""
        selected = self.path_listbox.curselection()
        
        if not selected:
            messagebox.showinfo("Информация", "Выберите путь для удаления")
            return
        
        confirm = messagebox.askyesno("Подтверждение", 
                                   "Вы уверены, что хотите удалить выбранный путь?")
        
        if confirm:
            self.path_listbox.delete(selected[0])
    
    def move_path(self, direction):
        """Перемещает выбранный путь вверх или вниз"""
        selected = self.path_listbox.curselection()
        
        if not selected:
            messagebox.showinfo("Информация", "Выберите путь для перемещения")
            return
        
        index = selected[0]
        
        # Определяем новую позицию
        new_index = index + direction
        
        # Проверяем, не выходит ли новая позиция за границы списка
        if new_index < 0 or new_index >= self.path_listbox.size():
            return
        
        # Сохраняем текущий путь
        path = self.path_listbox.get(index)
        
        # Удаляем текущий путь и вставляем его на новую позицию
        self.path_listbox.delete(index)
        self.path_listbox.insert(new_index, path)
        
        # Выделяем путь на новой позиции
        self.path_listbox.selection_clear(0, tk.END)
        self.path_listbox.selection_set(new_index)
        self.path_listbox.see(new_index)
    
    def save_path(self):
        """Сохраняет изменения в переменной PATH"""
        paths = []
        for i in range(self.path_listbox.size()):
            paths.append(self.path_listbox.get(i))
        
        # Объединяем пути в одну строку
        path_value = ';'.join(paths)
        
        try:
            if self.var_type.get() == "user":
                self.set_user_path(path_value)
            else:
                self.set_system_path(path_value)
            
            # Обновляем переменную в текущей сессии
            self.broadcast_environment_change()
            
            messagebox.showinfo("Успех", "Переменная PATH успешно обновлена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить переменную PATH: {str(e)}")
    
    def set_user_path(self, path_value):
        """Устанавливает значение пользовательской переменной PATH"""
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, 
                         winreg.KEY_WRITE | winreg.KEY_READ)
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, path_value)
        winreg.CloseKey(key)
    
    def set_system_path(self, path_value):
        """Устанавливает значение системной переменной PATH"""
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                         r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                         0, winreg.KEY_WRITE | winreg.KEY_READ)
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, path_value)
        winreg.CloseKey(key)
    
    def broadcast_environment_change(self):
        """Оповещает систему об изменении переменных среды"""
        # Константы для отправки WM_SETTINGCHANGE
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        
        try:
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, 
                ctypes.create_unicode_buffer("Environment"), 
                SMTO_ABORTIFHUNG, 5000, ctypes.byref(ctypes.c_ulong())
            )
        except:
            pass
            
    def export_path(self):
        """Сохраняет текущее значение PATH в файл"""
        # Получаем текущую дату и время
        now = datetime.datetime.now()
        date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        
        # Определяем префикс в зависимости от типа переменной
        if self.var_type.get() == "user":
            # Получаем имя текущего пользователя
            username = os.environ.get('USERNAME', 'user')
            prefix = username
        else:
            prefix = "sys"
            
        # Формируем имя файла по умолчанию
        default_filename = f"PATH_backup_{prefix}_{date_time_str}.json"
        
        # Открываем диалог сохранения файла
        filepath = filedialog.asksaveasfilename(
            title="Сохранить PATH в файл",
            defaultextension=".json",
            initialfile=default_filename,
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if not filepath:
            return
            
        try:
            # Собираем пути из списка
            paths = []
            for i in range(self.path_listbox.size()):
                paths.append(self.path_listbox.get(i))
                
            # Создаем словарь с данными
            data = {
                "path_value": ';'.join(paths),
                "path_entries": paths,
                "backup_date": now.isoformat(),
                "path_type": self.var_type.get(),
                "version": "1.0"
            }
            
            # Сохраняем в JSON файл
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            messagebox.showinfo("Успех", f"Резервная копия PATH успешно сохранена в файл:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить PATH в файл: {str(e)}")
    
    def import_path(self):
        """Загружает значение PATH из файла"""
        # Открываем диалог выбора файла
        filepath = filedialog.askopenfilename(
            title="Загрузить PATH из файла",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if not filepath:
            return
            
        try:
            # Загружаем данные из файла
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Проверяем формат файла
            if "path_entries" not in data:
                raise ValueError("Некорректный формат файла резервной копии PATH")
                
            # Показываем информацию о резервной копии
            backup_date = datetime.datetime.fromisoformat(data["backup_date"]).strftime("%d.%m.%Y %H:%M:%S")
            path_type = "Пользовательская" if data.get("path_type") == "user" else "Системная"
            
            confirm_msg = f"Дата создания резервной копии: {backup_date}\nТип PATH: {path_type}\n\nВосстановить эту копию PATH?"
            confirm = messagebox.askyesno("Подтверждение восстановления", confirm_msg)
            
            if not confirm:
                return
                
            # Устанавливаем тип PATH
            if "path_type" in data:
                self.var_type.set(data["path_type"])
                
            # Очищаем текущий список
            self.path_listbox.delete(0, tk.END)
            
            # Добавляем пути из файла
            for path in data["path_entries"]:
                self.path_listbox.insert(tk.END, path)
                
            messagebox.showinfo("Успех", "Резервная копия PATH успешно загружена из файла")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить PATH из файла: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PathEditor(root)
    root.mainloop()
