#!/usr/bin/env python3
"""
Firebase Data Exporter - Exporta datos de docentes pre-inscritos
Usa la API REST de Firebase Auth + Realtime Database
"""
import json
import sys
import os
import urllib.request
import urllib.error

# Firebase config (public, from firebase-config.js)
API_KEY = "AIzaSyCzN4xNEE_hKshXbsVqLhWSnzet1pHwRh8"
DB_URL = "https://profe-blog-default-rtdb.firebaseio.com"

def firebase_auth(email, password):
    """Authenticate with Firebase and return ID token"""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    data = json.dumps({"email": email, "password": password, "returnSecureToken": True}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result["idToken"]
    except urllib.error.HTTPError as e:
        error = json.loads(e.read())
        print(f"Error de autenticacion: {error.get('error', {}).get('message', 'Unknown')}")
        sys.exit(1)

def firebase_get(path, token):
    """Read data from Firebase Realtime Database"""
    url = f"{DB_URL}/{path}.json?auth={token}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"Error leyendo {path}: {e.code}")
        return None

def main():
    print("=" * 60)
    print("  EXPORTADOR DE DATOS - profefranciscopancho.com")
    print("=" * 60)
    print()
    
    # Get credentials
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        email = input("Email admin: ").strip()
        password = input("Password admin: ").strip()
    
    if not email or not password:
        print("Email y password requeridos")
        sys.exit(1)
    
    # Authenticate
    print(f"\nAutenticando como {email}...")
    token = firebase_auth(email, password)
    print("Autenticacion exitosa!")
    
    # Read users
    print("\nLeyendo usuarios...")
    users = firebase_get("users", token)
    if not users:
        print("No se encontraron usuarios")
        sys.exit(1)
    
    # Read portfolios
    print("Leyendo portafolios...")
    portafolios = firebase_get("portafolios", token)
    if not portafolios:
        portafolios = {}
    
    # Filter out admin users
    clients = {}
    for uid, data in users.items():
        if data.get("role") != "admin":
            clients[uid] = {
                "user": data,
                "portafolio": portafolios.get(uid, {})
            }
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Manuales", "CLIENTES")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save complete export
    export_path = os.path.join(output_dir, "export_completo.json")
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(clients, f, ensure_ascii=False, indent=2)
    print(f"\nExportados {len(clients)} clientes a: {export_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"  RESUMEN: {len(clients)} DOCENTES REGISTRADOS")
    print("=" * 60)
    
    pre_inscritos = 0
    con_datos = 0
    con_cuestionario = 0
    con_gdrive = 0
    
    for uid, info in clients.items():
        u = info["user"]
        p = info["portafolio"]
        
        status = u.get("status", "")
        nombre = u.get("nombre", "(sin nombre)")
        email_c = u.get("email", "")
        nivel = ""
        asig = ""
        
        dp = p.get("datosPortafolio", {})
        if dp:
            con_datos += 1
            nivel = dp.get("nivel", "")
            asig = dp.get("asignatura", "")
        
        cq = p.get("cuestionarioModulos")
        if cq:
            con_cuestionario += 1
        
        gd = p.get("googleDrive", {})
        if gd and gd.get("shareUrl"):
            con_gdrive += 1
        
        if status == "pre-inscrito":
            pre_inscritos += 1
        
        insc = u.get("inscripcionNum", "—")
        plan = p.get("plan", "—")
        pay = p.get("paymentStatus", "pendiente")
        
        print(f"\n  [{insc}] {nombre}")
        print(f"    Email: {email_c} | Tel: {u.get('telefono', '—')}")
        print(f"    Plan: {plan} | Pago: {pay}")
        if nivel or asig:
            print(f"    Nivel: {nivel} | Asignatura: {asig}")
        if dp:
            print(f"    Colegio: {dp.get('colegio', '—')} ({dp.get('comuna', '—')}, {dp.get('region', '—')})")
            print(f"    Curso: {dp.get('curso', '—')} | Alumnos: {dp.get('numAlumnos', '—')} | PIE: {dp.get('numPIE', '0')}")
            if dp.get("objetivoAprendizaje"):
                oa = dp["objetivoAprendizaje"]
                print(f"    OA: {oa[:100]}{'...' if len(oa) > 100 else ''}")
        if gd and gd.get("shareUrl"):
            print(f"    Google Drive: {gd['shareUrl']}")
        
        # Save individual client file
        safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in nombre).strip()
        client_dir = os.path.join(output_dir, f"{insc}_{safe_name}")
        os.makedirs(client_dir, exist_ok=True)
        
        # Save context data
        with open(os.path.join(client_dir, "datos.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        # Save human-readable context
        with open(os.path.join(client_dir, "contexto.md"), "w", encoding="utf-8") as f:
            f.write(f"# Contexto Docente: {nombre}\n\n")
            f.write(f"- **Inscripcion**: {insc}\n")
            f.write(f"- **Email**: {email_c}\n")
            f.write(f"- **Telefono**: {u.get('telefono', '—')}\n")
            f.write(f"- **RUT**: {u.get('rut', '—')}\n")
            f.write(f"- **Plan**: {plan}\n")
            f.write(f"- **Pago**: {pay}\n")
            if gd and gd.get("shareUrl"):
                f.write(f"- **Google Drive**: {gd['shareUrl']}\n")
            f.write(f"\n## Datos del Portafolio\n\n")
            if dp:
                for key in ["nivel", "asignatura", "colegio", "tipoColegio", "comuna", "region", 
                           "curso", "numAlumnos", "numPIE", "tipoNEE", "codocentePIE", "ive",
                           "objetivoAprendizaje", "unidad", "ejeCurricular", "sellos", 
                           "descripcion", "conocimientosPrevios", "listaAlumnos"]:
                    val = dp.get(key, "")
                    if val:
                        f.write(f"- **{key}**: {val}\n")
            else:
                f.write("*(Sin datos de portafolio aun)*\n")
            
            if cq:
                f.write(f"\n## Cuestionario de Modulos\n\n")
                for mod_key in ["modulo1", "modulo2", "modulo3"]:
                    mod = cq.get(mod_key, {})
                    if mod:
                        f.write(f"### {mod_key.replace('modulo', 'Modulo ')}\n")
                        for k, v in mod.items():
                            f.write(f"- **{k}**: {v}\n")
                        f.write("\n")
    
    print(f"\n{'=' * 60}")
    print(f"  Pre-inscritos: {pre_inscritos}")
    print(f"  Con datos de portafolio: {con_datos}")
    print(f"  Con cuestionario completo: {con_cuestionario}")
    print(f"  Con carpeta Google Drive: {con_gdrive}")
    print(f"{'=' * 60}")
    print(f"\nCarpetas individuales creadas en: {output_dir}")

if __name__ == "__main__":
    main()
