import json
import os


class BD:
    def __init__(self, filename: str):
        """
        Inicializa la clase con el nombre del archivo JSON.
        Parámetro:
            filename (str): nombre del archivo donde se guardarán los datos.
        """
        self.filename = filename

    # ===============================
    # Métodos de manejo del archivo
    # ===============================

    def load_data(self):
        """Carga los datos desde el archivo JSON."""
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []

    def save_data(self, data):
        """Guarda los datos en el archivo JSON."""
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    # ===============================
    # Métodos del CRUD
    # ===============================

    def create_item(self):
        """Crea un nuevo registro."""
        data = self.load_data()
        nombre = input("Nombre: ")
        edad = input("Edad: ")
        ciudad = input("Ciudad: ")

        nuevo = {
            "id": len(data) + 1,
            "nombre": nombre,
            "edad": edad,
            "ciudad": ciudad
        }

        data.append(nuevo)
        self.save_data(data)
        print("✅ Registro agregado correctamente.")

    def read_items(self):
        """Muestra todos los registros."""
        data = self.load_data()
        if not data:
            print("⚠️ No hay registros.")
            return

        print("\n📋 Lista de registros:")
        for item in data:
            print(f"ID: {item['id']} | Nombre: {item['nombre']} | Edad: {item['edad']} | Ciudad: {item['ciudad']}")
        print()

    def update_item(self):
        """Actualiza un registro existente."""
        data = self.load_data()
        self.read_items()
        try:
            id_update = int(input("ID del registro a actualizar: "))
        except ValueError:
            print("⚠️ ID inválido.")
            return

        for item in data:
            if item["id"] == id_update:
                print("Deja vacío si no quieres cambiar el valor.")
                nuevo_nombre = input(f"Nuevo nombre ({item['nombre']}): ") or item['nombre']
                nueva_edad = input(f"Nueva edad ({item['edad']}): ") or item['edad']
                nueva_ciudad = input(f"Nueva ciudad ({item['ciudad']}): ") or item['ciudad']

                item["nombre"] = nuevo_nombre
                item["edad"] = nueva_edad
                item["ciudad"] = nueva_ciudad

                self.save_data(data)
                print("✅ Registro actualizado correctamente.")
                return

        print("⚠️ No se encontró el registro con ese ID.")

    def delete_item(self):
        """Elimina un registro."""
        data = self.load_data()
        self.read_items()
        try:
            id_delete = int(input("ID del registro a eliminar: "))
        except ValueError:
            print("⚠️ ID inválido.")
            return

        new_data = [item for item in data if item["id"] != id_delete]

        if len(new_data) == len(data):
            print("⚠️ No se encontró el registro.")
        else:
            self.save_data(new_data)
            print("🗑️ Registro eliminado correctamente.")

