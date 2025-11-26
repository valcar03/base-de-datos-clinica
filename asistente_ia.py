import sqlite3
import re
from datetime import datetime, timedelta

class AsistenteIA:
    def __init__(self, db_path='data/podologia.db'):
        self.db_path = db_path
    
    def procesar_pregunta(self, pregunta):
        """Procesa preguntas naturales y devuelve respuestas"""
        pregunta = pregunta.lower().strip()
        
        # Conexión a la base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Patrón: "cuántos pacientes" + "semana"
            if re.search(r'cuántos pacientes|cuantos pacientes', pregunta) and re.search(r'semana', pregunta):
                return self._contar_pacientes_semana(pregunta, cursor)
            
            # Patrón: "última vez" + nombre paciente
            elif re.search(r'última vez|ultima vez|cuándo vino|cuando vino', pregunta):
                return self._ultima_visita(pregunta, cursor)
            
            # Patrón: "próximas citas"
            elif re.search(r'próximas citas|proximas citas|citas de hoy', pregunta):
                return self._proximas_citas(cursor)
            
            # Patrón: "pacientes con" + etiqueta
            elif re.search(r'pacientes con|etiqueta', pregunta):
                return self._buscar_por_etiqueta(pregunta, cursor)
            
            # Patrón: "estadísticas" o "resumen"
            elif re.search(r'estadísticas|estadisticas|resumen', pregunta):
                return self._estadisticas_generales(cursor)
            
            else:
                return "Puedo ayudarte con:\n• Contar pacientes por semana\n• Última visita de un paciente\n• Próximas citas\n• Buscar por etiquetas\n• Estadísticas generales"
                
        finally:
            conn.close()
    
    def _contar_pacientes_semana(self, pregunta, cursor):
        """Cuenta pacientes por semana"""
        try:
            # Buscar fecha en la pregunta
            fecha_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', pregunta)
            if fecha_match:
                dia, mes, año = fecha_match.groups()
                fecha_inicio = f"{año}-{mes:0>2}-{dia:0>2}"
            else:
                # Semana actual por defecto
                hoy = datetime.now()
                fecha_inicio = (hoy - timedelta(days=hoy.weekday())).strftime("%Y-%m-%d")
            
            fecha_fin = (datetime.strptime(fecha_inicio, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
            
            cursor.execute('''
                SELECT COUNT(DISTINCT paciente_id) 
                FROM citas 
                WHERE fecha BETWEEN ? AND ?
            ''', (fecha_inicio, fecha_fin))
            
            resultado = cursor.fetchone()[0]
            return f"En la semana del {fecha_inicio} al {fecha_fin} hubo {resultado} pacientes"
            
        except Exception as e:
            return f"Error al contar pacientes: {str(e)}"
    
    def _ultima_visita(self, pregunta, cursor):
        """Encuentra la última visita de un paciente"""
        # Extraer nombre del paciente
        nombre_match = re.search(r'paciente\s+(\w+)', pregunta)
        if not nombre_match:
            return "¿De qué paciente quieres saber la última visita? Ej: 'última vez del paciente Juan'"
        
        nombre_paciente = nombre_match.group(1)
        
        cursor.execute('''
            SELECT p.nombre, MAX(c.fecha) 
            FROM citas c 
            JOIN pacientes p ON c.paciente_id = p.id 
            WHERE p.nombre LIKE ? 
            GROUP BY p.nombre
        ''', (f'%{nombre_paciente}%',))
        
        resultado = cursor.fetchone()
        if resultado:
            return f"El paciente {resultado[0]} vino por última vez el {resultado[1]}"
        else:
            return f"No se encontraron visitas para pacientes que coincidan con '{nombre_paciente}'"
    
    def _proximas_citas(self, cursor):
        """Muestra las próximas citas"""
        hoy = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute('''
            SELECT p.nombre, c.fecha, c.tratamiento 
            FROM citas c 
            JOIN pacientes p ON c.paciente_id = p.id 
            WHERE c.fecha >= ? 
            ORDER BY c.fecha 
            LIMIT 5
        ''', (hoy,))
        
        citas = cursor.fetchall()
        if citas:
            respuesta = "Próximas citas:\n"
            for cita in citas:
                respuesta += f"• {cita[0]} - {cita[1]} - {cita[2]}\n"
            return respuesta
        else:
            return "No hay próximas citas programadas"
    
    def _buscar_por_etiqueta(self, pregunta, cursor):
        """Busca pacientes por etiqueta"""
        etiqueta_match = re.search(r'etiqueta\s+(\w+)|con\s+(\w+)', pregunta)
        if not etiqueta_match:
            return "¿Qué etiqueta buscas? Ej: 'pacientes con diabetes'"
        
        etiqueta = etiqueta_match.group(1) or etiqueta_match.group(2)
        
        cursor.execute('''
            SELECT DISTINCT p.nombre 
            FROM pacientes p 
            JOIN etiquetas e ON p.id = e.paciente_id 
            WHERE e.nombre_etiqueta LIKE ?
        ''', (f'%{etiqueta}%',))
        
        pacientes = cursor.fetchall()
        if pacientes:
            respuesta = f"Pacientes con etiqueta '{etiqueta}':\n"
            for paciente in pacientes:
                respuesta += f"• {paciente[0]}\n"
            return respuesta
        else:
            return f"No hay pacientes con la etiqueta '{etiqueta}'"
    
    def _estadisticas_generales(self, cursor):
        """Estadísticas generales de la clínica"""
        # Total pacientes
        cursor.execute('SELECT COUNT(*) FROM pacientes')
        total_pacientes = cursor.fetchone()[0]
        
        # Citas este mes
        mes_actual = datetime.now().strftime("%Y-%m")
        cursor.execute('SELECT COUNT(*) FROM citas WHERE fecha LIKE ?', (f'{mes_actual}%',))
        citas_mes = cursor.fetchone()[0]
        
        return f"Estadísticas:\n• Total pacientes: {total_pacientes}\n• Citas este mes: {citas_mes}"

# Pruebas del asistente
if __name__ == "__main__":
    asistente = AsistenteIA()
    
    preguntas = [
        "¿Cuántos pacientes tuve esta semana?",
        "¿Cuándo vino el paciente Juan por última vez?",
        "¿Qué próximas citas tengo?",
        "¿Qué pacientes tienen diabetes?",
        "Estadísticas generales"
    ]
    
    for pregunta in preguntas:
        print(f"P: {pregunta}")
        print(f"R: {asistente.procesar_pregunta(pregunta)}\n")