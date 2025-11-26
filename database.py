import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.init_db()
    
    def init_db(self):
        """Inicializar la base de datos y tablas"""
        # Crear carpeta data si no existe
        if not os.path.exists('data'):
            os.makedirs('data')
            os.makedirs('data/fotos')
        
        self.conn = sqlite3.connect('data/podologia.db')
        self.cursor = self.conn.cursor()
        
        # Tabla de pacientes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT,
                email TEXT,
                fecha_nacimiento TEXT,
                direccion TEXT,
                fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de citas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS citas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                fecha TEXT NOT NULL,
                notas TEXT,
                tratamiento TEXT,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
            )
        ''')
        
        # Tabla de fotos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fotos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                fecha TEXT NOT NULL,
                ruta_archivo TEXT NOT NULL,
                descripcion TEXT,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
            )
        ''')
        
        # NUEVO: Catálogo de etiquetas disponibles
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS etiquetas_disponibles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_etiqueta TEXT UNIQUE NOT NULL,
                categoria TEXT DEFAULT 'general'
            )
        ''')
        
        # NUEVO: Relación pacientes-etiquetas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS etiquetas_pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                etiqueta_id INTEGER,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
                FOREIGN KEY (etiqueta_id) REFERENCES etiquetas_disponibles (id),
                UNIQUE(paciente_id, etiqueta_id)
            )
        ''')
        
        # Insertar etiquetas comunes por defecto
        etiquetas_comunes = [
            'diabetes', 'uñero', 'hongos', 'callos', 'juanetes',
            'pie plano', 'espolón', 'circulación', 'anciano', 'deportista',
            'niño', 'adulto mayor', 'diabético', 'postoperatorio'
        ]
        
        for etiqueta in etiquetas_comunes:
            try:
                self.cursor.execute(
                    'INSERT OR IGNORE INTO etiquetas_disponibles (nombre_etiqueta) VALUES (?)',
                    (etiqueta,)
                )
            except:
                pass
        
        self.conn.commit()
        print("Base de datos inicializada correctamente")
    
    # --- OPERACIONES PARA PACIENTES ---
    def agregar_paciente(self, nombre, telefono="", email="", fecha_nacimiento="", direccion=""):
        """Agregar nuevo paciente"""
        query = '''
            INSERT INTO pacientes (nombre, telefono, email, fecha_nacimiento, direccion)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.cursor.execute(query, (nombre, telefono, email, fecha_nacimiento, direccion))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def obtener_pacientes(self):
        """Obtener todos los pacientes"""
        self.cursor.execute('SELECT * FROM pacientes ORDER BY nombre')
        return self.cursor.fetchall()
    
    def buscar_paciente(self, nombre):
        """Buscar paciente por nombre"""
        self.cursor.execute('SELECT * FROM pacientes WHERE nombre LIKE ?', (f'%{nombre}%',))
        return self.cursor.fetchall()
    
    # --- OPERACIONES PARA CITAS ---
    def agregar_cita(self, paciente_id, fecha, notas="", tratamiento=""):
        """Agregar nueva cita"""
        query = '''
            INSERT INTO citas (paciente_id, fecha, notas, tratamiento)
            VALUES (?, ?, ?, ?)
        '''
        self.cursor.execute(query, (paciente_id, fecha, notas, tratamiento))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def obtener_citas_paciente(self, paciente_id):
        """Obtener todas las citas de un paciente"""
        self.cursor.execute('''
            SELECT * FROM citas 
            WHERE paciente_id = ? 
            ORDER BY fecha DESC
        ''', (paciente_id,))
        return self.cursor.fetchall()
    
    def obtener_citas_fecha(self, fecha):
        """Obtener citas de una fecha específica"""
        self.cursor.execute('SELECT * FROM citas WHERE fecha LIKE ?', (f'{fecha}%',))
        return self.cursor.fetchall()
    
    # --- OPERACIONES PARA FOTOS ---
    def agregar_foto(self, paciente_id, ruta_archivo, descripcion=""):
        """Agregar referencia a foto"""
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = '''
            INSERT INTO fotos (paciente_id, fecha, ruta_archivo, descripcion)
            VALUES (?, ?, ?, ?)
        '''
        self.cursor.execute(query, (paciente_id, fecha_actual, ruta_archivo, descripcion))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def obtener_fotos_paciente(self, paciente_id):
        """Obtener todas las fotos de un paciente"""
        self.cursor.execute('''
            SELECT * FROM fotos 
            WHERE paciente_id = ? 
            ORDER BY fecha DESC
        ''', (paciente_id,))
        return self.cursor.fetchall()
    
    # --- SISTEMA MEJORADO DE ETIQUETAS ---
    
    def obtener_etiquetas_disponibles(self):
        """Obtener todas las etiquetas disponibles"""
        self.cursor.execute('SELECT nombre_etiqueta FROM etiquetas_disponibles ORDER BY nombre_etiqueta')
        return [item[0] for item in self.cursor.fetchall()]
    
    def agregar_etiqueta_disponible(self, nombre_etiqueta):
        """Agregar nueva etiqueta al catálogo"""
        try:
            self.cursor.execute(
                'INSERT OR IGNORE INTO etiquetas_disponibles (nombre_etiqueta) VALUES (?)',
                (nombre_etiqueta,)
            )
            self.conn.commit()
            return True
        except:
            return False
    
    def agregar_etiqueta_paciente(self, paciente_id, nombre_etiqueta):
        """Agregar etiqueta a paciente (sistema nuevo)"""
        # Primero asegurar que la etiqueta existe en el catálogo
        self.agregar_etiqueta_disponible(nombre_etiqueta)
        
        # Obtener ID de la etiqueta
        self.cursor.execute('SELECT id FROM etiquetas_disponibles WHERE nombre_etiqueta = ?', (nombre_etiqueta,))
        etiqueta_id_result = self.cursor.fetchone()
        
        if etiqueta_id_result:
            etiqueta_id = etiqueta_id_result[0]
            # Agregar relación paciente-etiqueta
            try:
                self.cursor.execute(
                    'INSERT OR IGNORE INTO etiquetas_pacientes (paciente_id, etiqueta_id) VALUES (?, ?)',
                    (paciente_id, etiqueta_id)
                )
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error agregando etiqueta: {e}")
                return False
        return False
    
    def obtener_etiquetas_paciente(self, paciente_id):
        """Obtener etiquetas de un paciente (sistema nuevo)"""
        self.cursor.execute('''
            SELECT ed.nombre_etiqueta 
            FROM etiquetas_disponibles ed
            JOIN etiquetas_pacientes ep ON ed.id = ep.etiqueta_id
            WHERE ep.paciente_id = ?
        ''', (paciente_id,))
        return [item[0] for item in self.cursor.fetchall()]
    
    def buscar_por_etiqueta(self, etiqueta):
        """Buscar pacientes por etiqueta (sistema nuevo)"""
        self.cursor.execute('''
            SELECT p.* FROM pacientes p
            JOIN etiquetas_pacientes ep ON p.id = ep.paciente_id
            JOIN etiquetas_disponibles ed ON ep.etiqueta_id = ed.id
            WHERE ed.nombre_etiqueta LIKE ?
        ''', (f'%{etiqueta}%',))
        return self.cursor.fetchall()
    
    def eliminar_etiqueta_paciente(self, paciente_id, nombre_etiqueta):
        """Eliminar etiqueta de un paciente"""
        try:
            self.cursor.execute('''
                DELETE FROM etiquetas_pacientes 
                WHERE paciente_id = ? AND etiqueta_id IN (
                    SELECT id FROM etiquetas_disponibles WHERE nombre_etiqueta = ?
                )
            ''', (paciente_id, nombre_etiqueta))
            self.conn.commit()
            return True
        except:
            return False
        
    def eliminar_paciente(self, paciente_id):
        try:
            # Eliminar en este orden para respetar las claves foráneas
            self.cursor.execute('DELETE FROM etiquetas_pacientes WHERE paciente_id = ?', (paciente_id,))
            self.cursor.execute('DELETE FROM fotos WHERE paciente_id = ?', (paciente_id,))
            self.cursor.execute('DELETE FROM citas WHERE paciente_id = ?', (paciente_id,))
            self.cursor.execute('DELETE FROM pacientes WHERE id = ?', (paciente_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error eliminando paciente: {e}")
            self.conn.rollback()
            return False
        
    def cerrar_conexion(self):
        """Cerrar conexión a la base de datos"""
        if self.conn:
            self.conn.close()

    def actualizar_paciente(self, paciente_id, nombre, telefono="", email="", fecha_nacimiento="", direccion=""):

        try:
            query = '''
                UPDATE pacientes 
                SET nombre = ?, telefono = ?, email = ?, fecha_nacimiento = ?, direccion = ?
                WHERE id = ?
            '''
            self.cursor.execute(query, (nombre, telefono, email, fecha_nacimiento, direccion, paciente_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando paciente: {e}")
            return False

# Probar la base de datos
if __name__ == "__main__":
    db = Database()
    
    # Ejemplos de uso
    paciente_id = db.agregar_paciente("Juan Pérez", "123456789", "juan@email.com")
    print(f"Paciente agregado con ID: {paciente_id}")
    
    db.agregar_cita(paciente_id, "2024-01-15 10:00", "Primera consulta", "Evaluación inicial")
    db.agregar_etiqueta_paciente(paciente_id, "diabetes")
    db.agregar_etiqueta_paciente(paciente_id, "uñero")
    
    pacientes = db.obtener_pacientes()
    print("Pacientes:", pacientes)
    
    etiquetas = db.obtener_etiquetas_disponibles()
    print("Etiquetas disponibles:", etiquetas)