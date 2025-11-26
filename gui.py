import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from PIL import Image, ImageTk
import os
from datetime import datetime

class PodologiaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Podología - Fichas de Pacientes")
        self.root.geometry("1000x700")
        
        # Inicializar base de datos
        self.db = Database()
        
        # Variables
        self.paciente_actual = None
        self.foto_actual = None
        
        self.crear_interfaz()
        self.actualizar_lista_pacientes()
        
        # CARGAR INMEDIATAMENTE el primer paciente si existe
        self.cargar_primer_paciente()
    
    def cargar_primer_paciente(self):
        """Cargar automáticamente el primer paciente al iniciar"""
        pacientes = self.db.obtener_pacientes()
        if pacientes:
            # Seleccionar el primer paciente de la lista
            self.lista_pacientes.selection_set(0)
            self.lista_pacientes.see(0)
            # Forzar la selección
            self.seleccionar_paciente(None)

    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # --- LEFT FRAME: Lista de pacientes y búsqueda ---
        left_frame = ttk.LabelFrame(main_frame, text="Pacientes", padding="5")
        left_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Búsqueda
        ttk.Label(left_frame, text="Buscar:").grid(row=0, column=0, sticky=tk.W)
        self.buscar_entry = ttk.Entry(left_frame, width=20)
        self.buscar_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.buscar_entry.bind('<KeyRelease>', self.buscar_pacientes)
        
        # Lista de pacientes
        self.lista_pacientes = tk.Listbox(left_frame, width=30, height=20)
        self.lista_pacientes.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.lista_pacientes.bind('<<ListboxSelect>>', self.seleccionar_paciente)
        
        # Scrollbar para lista
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.lista_pacientes.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.lista_pacientes.configure(yscrollcommand=scrollbar.set)
        
        # Botones de pacientes
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(btn_frame, text="Nuevo Paciente", command=self.nuevo_paciente).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_paciente).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Configurar grid left frame
        left_frame.columnconfigure(1, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # --- RIGHT FRAME: Información del paciente ---
        self.right_frame = ttk.LabelFrame(main_frame, text="Información del Paciente", padding="10")
        self.right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.right_frame.columnconfigure(1, weight=1)
        
        # Información básica
        ttk.Label(self.right_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.nombre_var = tk.StringVar()
        ttk.Entry(self.right_frame, textvariable=self.nombre_var, state='readonly').grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(self.right_frame, text="Teléfono:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.telefono_var = tk.StringVar()
        ttk.Entry(self.right_frame, textvariable=self.telefono_var, state='readonly').grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(self.right_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.email_var = tk.StringVar()
        ttk.Entry(self.right_frame, textvariable=self.email_var, state='readonly').grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Etiquetas
        ttk.Label(self.right_frame, text="Etiquetas:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.etiquetas_frame = ttk.Frame(self.right_frame)
        self.etiquetas_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # --- NOTEBOOK para pestañas ---
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Pestaña de Citas
        self.citas_frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.citas_frame, text="Citas")
        self.crear_pestana_citas()
        
        # Pestaña de Fotos
        self.fotos_frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.fotos_frame, text="Fotos")
        self.crear_pestana_fotos()
        
        # Pestaña de Búsqueda con IA
        self.ia_frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.ia_frame, text="Asistente IA")
        self.crear_pestana_ia()
    
    def crear_pestana_citas(self):
        """Crear interfaz para gestión de citas"""
        # Frame para agregar nueva cita
        nueva_cita_frame = ttk.LabelFrame(self.citas_frame, text="Nueva Cita", padding="5")
        nueva_cita_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        nueva_cita_frame.columnconfigure(1, weight=1)
        
        ttk.Label(nueva_cita_frame, text="Fecha:").grid(row=0, column=0, sticky=tk.W)
        self.fecha_cita = ttk.Entry(nueva_cita_frame)
        self.fecha_cita.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        self.fecha_cita.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        ttk.Label(nueva_cita_frame, text="Tratamiento:").grid(row=1, column=0, sticky=tk.W)
        self.tratamiento_var = tk.StringVar()
        ttk.Entry(nueva_cita_frame, textvariable=self.tratamiento_var).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Label(nueva_cita_frame, text="Notas:").grid(row=2, column=0, sticky=tk.W)
        self.notas_cita = tk.Text(nueva_cita_frame, height=3, width=40)
        self.notas_cita.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Button(nueva_cita_frame, text="Agregar Cita", command=self.agregar_cita).grid(row=3, column=1, sticky=tk.E, pady=5)
        
        # Lista de citas
        citas_list_frame = ttk.LabelFrame(self.citas_frame, text="Citas Anteriores", padding="5")
        citas_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        citas_list_frame.columnconfigure(0, weight=1)
        citas_list_frame.rowconfigure(0, weight=1)
        
        self.citas_tree = ttk.Treeview(citas_list_frame, columns=('fecha', 'tratamiento', 'notas'), show='headings', height=8)
        self.citas_tree.heading('fecha', text='Fecha')
        self.citas_tree.heading('tratamiento', text='Tratamiento')
        self.citas_tree.heading('notas', text='Notas')
        
        self.citas_tree.column('fecha', width=120)
        self.citas_tree.column('tratamiento', width=150)
        self.citas_tree.column('notas', width=200)
        
        self.citas_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(citas_list_frame, orient=tk.VERTICAL, command=self.citas_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.citas_tree.configure(yscrollcommand=scrollbar.set)
        
        self.citas_frame.columnconfigure(0, weight=1)
        self.citas_frame.rowconfigure(1, weight=1)

                # Botones de pacientes
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(btn_frame, text="Nuevo Paciente", command=self.nuevo_paciente).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="Editar", command=self.editar_paciente).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_paciente).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
    def crear_pestana_fotos(self):
        """Crear interfaz para gestión de fotos"""
        # Frame para subir foto
        subir_frame = ttk.LabelFrame(self.fotos_frame, text="Subir Nueva Foto", padding="5")
        subir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        subir_frame.columnconfigure(1, weight=1)
        
        ttk.Button(subir_frame, text="Seleccionar Foto", command=self.seleccionar_foto).grid(row=0, column=0, pady=5)
        
        ttk.Label(subir_frame, text="Descripción:").grid(row=1, column=0, sticky=tk.W)
        self.descripcion_foto = ttk.Entry(subir_frame)
        self.descripcion_foto.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(subir_frame, text="Subir Foto", command=self.subir_foto).grid(row=2, column=1, sticky=tk.E, pady=5)
        
        # Visualización de fotos
        fotos_view_frame = ttk.LabelFrame(self.fotos_frame, text="Fotos del Paciente", padding="5")
        fotos_view_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        fotos_view_frame.columnconfigure(0, weight=1)
        fotos_view_frame.rowconfigure(0, weight=1)
        
        self.fotos_canvas = tk.Canvas(fotos_view_frame, bg='white')
        self.fotos_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(fotos_view_frame, orient=tk.VERTICAL, command=self.fotos_canvas.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.fotos_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.fotos_inner_frame = ttk.Frame(self.fotos_canvas)
        self.fotos_canvas.create_window((0, 0), window=self.fotos_inner_frame, anchor="nw")
        
        self.fotos_frame.columnconfigure(0, weight=1)
        self.fotos_frame.rowconfigure(1, weight=1)
    
    def crear_pestana_ia(self):
        """Crear interfaz para el asistente de IA"""
        ttk.Label(self.ia_frame, text="Haz preguntas sobre tus pacientes:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.pregunta_ia = tk.Text(self.ia_frame, height=3, width=60)
        self.pregunta_ia.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.pregunta_ia.insert('1.0', "Ej: ¿Cuántos pacientes tuve la semana pasada?")
        
        ttk.Button(self.ia_frame, text="Preguntar", command=self.procesar_pregunta_ia).grid(row=2, column=0, sticky=tk.E)
        
        self.respuesta_ia = tk.Text(self.ia_frame, height=10, width=60, state=tk.DISABLED)
        self.respuesta_ia.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.ia_frame.columnconfigure(0, weight=1)
        self.ia_frame.rowconfigure(3, weight=1)
    
    # --- MÉTODOS PRINCIPALES ---
    
    def actualizar_lista_pacientes(self):
        """Actualizar lista de pacientes"""
        self.lista_pacientes.delete(0, tk.END)
        pacientes = self.db.obtener_pacientes()
        for paciente in pacientes:
            self.lista_pacientes.insert(tk.END, f"{paciente[0]} - {paciente[1]}")
    
    def buscar_pacientes(self, event=None):
        """Buscar pacientes por nombre"""
        busqueda = self.buscar_entry.get()
        if busqueda:
            pacientes = self.db.buscar_paciente(busqueda)
            self.lista_pacientes.delete(0, tk.END)
            for paciente in pacientes:
                self.lista_pacientes.insert(tk.END, f"{paciente[0]} - {paciente[1]}")
        else:
            self.actualizar_lista_pacientes()
    
    def seleccionar_paciente(self, event):
        """Cuando se selecciona un paciente de la lista"""
        selection = self.lista_pacientes.curselection()
        if selection:
            index = selection[0]
            paciente_str = self.lista_pacientes.get(index)
            paciente_id = int(paciente_str.split(' - ')[0])
            
            # Obtener datos del paciente
            pacientes = self.db.obtener_pacientes()
            for paciente in pacientes:
                if paciente[0] == paciente_id:
                    self.paciente_actual = paciente
                    self.mostrar_info_paciente(paciente)
                    break
    
    def mostrar_info_paciente(self, paciente):
        """Mostrar información del paciente seleccionado"""
        self.nombre_var.set(paciente[1])
        self.telefono_var.set(paciente[2] or "")
        self.email_var.set(paciente[3] or "")
        
        # Mostrar etiquetas
        for widget in self.etiquetas_frame.winfo_children():
            widget.destroy()
        
        etiquetas = self.db.obtener_etiquetas_paciente(paciente[0])
        for i, etiqueta in enumerate(etiquetas):
            ttk.Label(self.etiquetas_frame, text=etiqueta, 
                     background='lightblue', padding="2 0").grid(row=0, column=i, padx=2)
        
        # Actualizar citas
        self.actualizar_citas_paciente(paciente[0])
        
        # Actualizar fotos
        self.actualizar_fotos_paciente(paciente[0])
    
    def actualizar_citas_paciente(self, paciente_id):
        """Actualizar lista de citas del paciente"""
        # Limpiar treeview
        for item in self.citas_tree.get_children():
            self.citas_tree.delete(item)
        
        citas = self.db.obtener_citas_paciente(paciente_id)
        for cita in citas:
            self.citas_tree.insert('', tk.END, values=(cita[2], cita[4], cita[3]))
    
    def actualizar_fotos_paciente(self, paciente_id):
        """Actualizar visualización de fotos del paciente"""
        # Limpiar frame de fotos
        for widget in self.fotos_inner_frame.winfo_children():
            widget.destroy()
        
        fotos = self.db.obtener_fotos_paciente(paciente_id)
        
        for i, foto in enumerate(fotos):
            foto_frame = ttk.Frame(self.fotos_inner_frame, relief='solid', borderwidth=1)
            foto_frame.grid(row=i//3, column=i%3, padx=5, pady=5, sticky=(tk.W, tk.E))
            
            try:
                # Cargar y mostrar imagen reducida
                image = Image.open(foto[3])
                image.thumbnail((150, 150))
                photo = ImageTk.PhotoImage(image)
                
                # Hacer la imagen clickeable
                label = ttk.Label(foto_frame, image=photo, cursor="hand2")
                label.image = photo  # Guardar referencia
                label.grid(row=0, column=0, padx=5, pady=5)
                
                # Hacer la imagen clickeable para ampliar
                label.bind('<Button-1>', lambda e, ruta=foto[3], fotos_lista=fotos: self.mostrar_foto_ampliada(ruta, fotos_lista))
                
                ttk.Label(foto_frame, text=foto[2].split()[0]).grid(row=1, column=0)
                desc_label = ttk.Label(foto_frame, text=foto[4] or "Sin descripción", 
                                     wraplength=140)
                desc_label.grid(row=2, column=0)
                
            except Exception as e:
                error_label = ttk.Label(foto_frame, text=f"Error: {e}")
                error_label.grid(row=0, column=0)
        
        # Actualizar scrollregion
        self.fotos_inner_frame.update_idletasks()
        self.fotos_canvas.configure(scrollregion=self.fotos_canvas.bbox("all"))
    
    def nuevo_paciente(self):
        """Ventana para agregar nuevo paciente"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Paciente")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Nombre:*").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        nombre_entry = ttk.Entry(dialog, width=30)
        nombre_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Teléfono:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        telefono_entry = ttk.Entry(dialog, width=30)
        telefono_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(dialog, text="Email:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # NUEVO: Selección de etiquetas disponibles
        ttk.Label(dialog, text="Etiquetas:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Frame para etiquetas disponibles
        etiquetas_frame = ttk.Frame(dialog)
        etiquetas_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Obtener etiquetas disponibles
        etiquetas_disponibles = self.db.obtener_etiquetas_disponibles()
        
        # Variables para checkboxes
        self.etiquetas_seleccionadas = {}
        
        # Crear checkboxes en 2 columnas
        for i, etiqueta in enumerate(etiquetas_disponibles):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(etiquetas_frame, text=etiqueta, variable=var)
            row = i // 2
            col = i % 2
            cb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            self.etiquetas_seleccionadas[etiqueta] = var
        
        # Campo para nueva etiqueta
        ttk.Label(dialog, text="Nueva etiqueta:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        nueva_etiqueta_entry = ttk.Entry(dialog, width=20)
        nueva_etiqueta_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        def guardar_paciente():
            nombre = nombre_entry.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            
            paciente_id = self.db.agregar_paciente(
                nombre,
                telefono_entry.get(),
                email_entry.get()
            )
            
            # Agregar etiquetas seleccionadas
            for etiqueta, var in self.etiquetas_seleccionadas.items():
                if var.get():
                    self.db.agregar_etiqueta_paciente(paciente_id, etiqueta)
            
            # Agregar nueva etiqueta si se especificó
            nueva_etiqueta = nueva_etiqueta_entry.get().strip()
            if nueva_etiqueta:
                self.db.agregar_etiqueta_paciente(paciente_id, nueva_etiqueta)
            
            self.actualizar_lista_pacientes()
            dialog.destroy()
            messagebox.showinfo("Éxito", "Paciente agregado correctamente")
        
        ttk.Button(dialog, text="Guardar", command=guardar_paciente).grid(row=5, column=1, sticky=tk.E, padx=5, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def eliminar_paciente(self):

        if not self.paciente_actual:
            messagebox.showwarning("Advertencia", "Selecciona un paciente primero")
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Estás seguro de eliminar al paciente {self.paciente_actual[1]}?\n\nEsta acción eliminará también sus citas, fotos y etiquetas."
        )
        
        if respuesta:
            try:
                # Primero eliminar las fotos físicas
                fotos = self.db.obtener_fotos_paciente(self.paciente_actual[0])
                for foto in fotos:
                    try:
                        if os.path.exists(foto[3]):  # ruta_archivo
                            os.remove(foto[3])
                    except:
                        pass
                
                # Luego eliminar de la base de datos
                if self.eliminar_paciente_db(self.paciente_actual[0]):
                    messagebox.showinfo("Éxito", "Paciente eliminado correctamente")
                    self.actualizar_lista_pacientes()
                    self.paciente_actual = None
                    self.mostrar_info_paciente(("", "", "", ""))  # Limpiar interfaz
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el paciente")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar paciente: {e}")
    def agregar_cita(self):
        """Agregar nueva cita"""
        if not self.paciente_actual:
            messagebox.showwarning("Advertencia", "Selecciona un paciente primero")
            return
        
        self.db.agregar_cita(
            self.paciente_actual[0],
            self.fecha_cita.get(),
            self.notas_cita.get('1.0', tk.END).strip(),
            self.tratamiento_var.get()
        )
        
        self.actualizar_citas_paciente(self.paciente_actual[0])
        self.notas_cita.delete('1.0', tk.END)
        self.tratamiento_var.set("")
        
        messagebox.showinfo("Éxito", "Cita agregada correctamente")
    
    def seleccionar_foto(self):
        """Seleccionar archivo de foto"""
        filename = filedialog.askopenfilename(
            title="Seleccionar foto",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if filename:
            self.foto_actual = filename
    
    def subir_foto(self):
        """Subir foto seleccionada"""
        if not self.paciente_actual:
            messagebox.showwarning("Advertencia", "Selecciona un paciente primero")
            return
        
        if not self.foto_actual:
            messagebox.showwarning("Advertencia", "Selecciona una foto primero")
            return
        
        # Copiar foto a carpeta data/fotos
        import shutil
        filename = os.path.basename(self.foto_actual)
        nuevo_path = f"data/fotos/{self.paciente_actual[0]}_{filename}"
        
        try:
            shutil.copy2(self.foto_actual, nuevo_path)
            
            # Guardar en base de datos
            self.db.agregar_foto(
                self.paciente_actual[0],
                nuevo_path,
                self.descripcion_foto.get()
            )
            
            self.actualizar_fotos_paciente(self.paciente_actual[0])
            self.descripcion_foto.delete(0, tk.END)
            self.foto_actual = None
            
            messagebox.showinfo("Éxito", "Foto subida correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo subir la foto: {e}")
    
    def procesar_pregunta_ia(self):
        """Procesar pregunta del asistente IA"""
        pregunta = self.pregunta_ia.get('1.0', tk.END).strip()
        
        if not pregunta:
            messagebox.showwarning("Advertencia", "Escribe una pregunta")
            return
        
        # Aquí integras el asistente de IA
        try:
            from asistente_ia import AsistenteIA
            asistente = AsistenteIA()
            respuesta = asistente.procesar_pregunta(pregunta)
        except ImportError:
            # Si no existe el módulo, mostrar respuesta básica
            respuesta = f"Pregunta: {pregunta}\n\n(El asistente IA avanzado estará disponible pronto. Por ahora puedo ayudarte con búsquedas básicas en los pacientes)"
        
        self.respuesta_ia.config(state=tk.NORMAL)
        self.respuesta_ia.delete('1.0', tk.END)
        self.respuesta_ia.insert('1.0', respuesta)
        self.respuesta_ia.config(state=tk.DISABLED)

    # --- VISOR DE FOTOS AMPLIADAS ---
    
    def crear_visor_fotos(self):
        """Crear ventana para visor de fotos"""
        self.visor = tk.Toplevel(self.root)
        self.visor.title("Visor de Fotos")
        self.visor.geometry("800x600")
        self.visor.transient(self.root)
        self.visor.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self.visor, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Imagen ampliada
        self.imagen_ampliada_label = ttk.Label(main_frame)
        self.imagen_ampliada_label.pack(fill=tk.BOTH, expand=True)
        
        # Controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(controls_frame, text="← Anterior", 
                  command=self.foto_anterior).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Cerrar", 
                  command=self.visor.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(controls_frame, text="Siguiente →", 
                  command=self.foto_siguiente).pack(side=tk.RIGHT, padx=5)
        
        # Variables para navegación
        self.fotos_visor = []
        self.indice_foto_actual = 0
        
        # Configurar teclado
        self.configurar_teclado_visor()
    
    def configurar_teclado_visor(self):
        """Configurar atajos de teclado para el visor"""
        if hasattr(self, 'visor') and self.visor.winfo_exists():
            self.visor.bind('<Left>', lambda e: self.foto_anterior())
            self.visor.bind('<Right>', lambda e: self.foto_siguiente())
            self.visor.bind('<Escape>', lambda e: self.visor.destroy())

    def editar_paciente(self):
        if not self.paciente_actual:
            messagebox.showwarning("Advertencia", "Selecciona un paciente primero")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Paciente")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Campos de edición
        ttk.Label(dialog, text="Nombre:*").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        nombre_entry = ttk.Entry(dialog, width=30)
        nombre_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        nombre_entry.insert(0, self.paciente_actual[1])
        
        ttk.Label(dialog, text="Teléfono:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        telefono_entry = ttk.Entry(dialog, width=30)
        telefono_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        telefono_entry.insert(0, self.paciente_actual[2] or "")
        
        ttk.Label(dialog, text="Email:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        email_entry.insert(0, self.paciente_actual[3] or "")
        
        # Etiquetas actuales del paciente
        etiquetas_actuales = self.db.obtener_etiquetas_paciente(self.paciente_actual[0])
        
        ttk.Label(dialog, text="Etiquetas:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Frame para etiquetas disponibles
        etiquetas_frame = ttk.Frame(dialog)
        etiquetas_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Obtener etiquetas disponibles
        etiquetas_disponibles = self.db.obtener_etiquetas_disponibles()
        
        # Variables para checkboxes
        etiquetas_seleccionadas = {}
    
    # Crear checkboxes en 2 columnas
    for i, etiqueta in enumerate(etiquetas_disponibles):
        var = tk.BooleanVar()
        # Marcar si el paciente ya tiene esta etiqueta
        if etiqueta in etiquetas_actuales:
            var.set(True)
        cb = ttk.Checkbutton(etiquetas_frame, text=etiqueta, variable=var)
        row = i // 2
        col = i % 2
        cb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
        etiquetas_seleccionadas[etiqueta] = var
    
    # Campo para nueva etiqueta
    ttk.Label(dialog, text="Nueva etiqueta:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
    nueva_etiqueta_entry = ttk.Entry(dialog, width=20)
    nueva_etiqueta_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
    
    def guardar_cambios():
        nombre = nombre_entry.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        # Actualizar datos básicos del paciente
        self.actualizar_paciente(
            self.paciente_actual[0],
            nombre,
            telefono_entry.get(),
            email_entry.get()
        )
        
        # Actualizar etiquetas
        etiquetas_a_mantener = []
        
        # Agregar etiquetas seleccionadas
        for etiqueta, var in etiquetas_seleccionadas.items():
            if var.get():
                etiquetas_a_mantener.append(etiqueta)
                if etiqueta not in etiquetas_actuales:
                    self.db.agregar_etiqueta_paciente(self.paciente_actual[0], etiqueta)
        
        # Remover etiquetas no seleccionadas
        for etiqueta in etiquetas_actuales:
            if etiqueta not in etiquetas_a_mantener:
                self.db.eliminar_etiqueta_paciente(self.paciente_actual[0], etiqueta)
        
        # Agregar nueva etiqueta si se especificó
        nueva_etiqueta = nueva_etiqueta_entry.get().strip()
        if nueva_etiqueta:
            self.db.agregar_etiqueta_paciente(self.paciente_actual[0], nueva_etiqueta)
        
        # Actualizar interfaz
        self.actualizar_lista_pacientes()
        self.mostrar_info_paciente(self.paciente_actual)
        dialog.destroy()
        messagebox.showinfo("Éxito", "Paciente actualizado correctamente")
    
        ttk.Button(dialog, text="Guardar Cambios", command=guardar_cambios).grid(row=5, column=1, sticky=tk.E, padx=5, pady=10)
        
        dialog.columnconfigure(1, weight=1)
    
    def mostrar_foto_ampliada(self, ruta_foto, fotos_lista=None):
        """Mostrar foto en visor ampliado"""
        if not hasattr(self, 'visor') or not self.visor.winfo_exists():
            self.crear_visor_fotos()
        
        # Guardar lista de fotos para navegación
        if fotos_lista:
            self.fotos_visor = fotos_lista
            # Encontrar el índice de la foto actual
            for i, foto in enumerate(fotos_lista):
                if foto[3] == ruta_foto:  # ruta_archivo está en índice 3
                    self.indice_foto_actual = i
                    break
        
        try:
            # Cargar y mostrar imagen
            image = Image.open(ruta_foto)
            
            # Calcular tamaño máximo para la ventana
            max_width = 750
            max_height = 500
            
            # Redimensionar manteniendo aspecto
            ratio = min(max_width/image.width, max_height/image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image_resized = image.resize(new_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image_resized)
            self.imagen_ampliada_label.configure(image=photo)
            self.imagen_ampliada_label.image = photo  # Guardar referencia
            
            # Actualizar título con información de la foto
            if self.fotos_visor:
                foto_actual = self.fotos_visor[self.indice_foto_actual]
                self.visor.title(f"Visor de Fotos ({self.indice_foto_actual + 1}/{len(self.fotos_visor)}) - {foto_actual[4] or 'Sin descripción'}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
    
    def foto_anterior(self):
        """Mostrar foto anterior"""
        if not self.fotos_visor or self.indice_foto_actual <= 0:
            return
        
        self.indice_foto_actual -= 1
        ruta_foto = self.fotos_visor[self.indice_foto_actual][3]  # ruta_archivo
        self.mostrar_foto_ampliada(ruta_foto)
    
    def foto_siguiente(self):
        """Mostrar foto siguiente"""
        if not self.fotos_visor or self.indice_foto_actual >= len(self.fotos_visor) - 1:
            return
        
        self.indice_foto_actual += 1
        ruta_foto = self.fotos_visor[self.indice_foto_actual][3]  # ruta_archivo
        self.mostrar_foto_ampliada(ruta_foto)

# Ejecutar aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = PodologiaApp(root)
    root.mainloop()