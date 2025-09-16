import subprocess
import json

NPM_CMD = r"C:\Program Files\nodejs\npm.cmd"


def check_outdated():
    #Comando 'npm outdated' para detectar depedencias obsoletas
    print('\n ******* Iniciando verificación de dependencias obsoletas *******\n')
    outdated = subprocess.run([NPM_CMD,'outdated','--json'],capture_output=True, text=True)
    if not outdated.stdout:
        print("Error al verificar depedencias obsoletas")
        return
    try:
        outdated_dependencies = json.loads(outdated.stdout)
    except json.JSONDecodeError:
        print("Error al analizar la salida de 'npm outdated'")
        return
    
    if not outdated_dependencies:
        print("No hay dependencias obsoletas")
    else:
        print("----------------- Dependencias obsoletas encontradas: ------------- ")
        total_outdated = len(outdated_dependencies)
        for dep,details in outdated_dependencies.items():
            print(f"{dep:<20}-{details['current']} -> {details['latest']}")
    print("------------------------------------------------------------------------")
    return outdated_dependencies, total_outdated


def check_vulnerabilites():
    # Comando 'npm audit' para evaluar vulnerabillidades
    print('\n ******* Iniciando verificación de vulnerabilidades *******')
    audit =  subprocess.run([NPM_CMD,'audit','--json'],capture_output=True, text=True)

    if not audit.stdout:
        print("Error al verificar vulnerabilidades")    
        return
    try:
        audit_report = json.loads(audit.stdout)
    except json.JSONDecodeError:
        print("Error al analizar la salida de 'npm audit'")
        return
    if not audit_report:
        print("No se encontraron vulnerabilidades")
    else:
        print("\n--------- Vulnerabilidades encontradas: -----------")
        print(audit.stdout)
    print('-----------------------------------------------------------')
    return audit_report

def check_health_metrics(outdated, total_outdated, vulnerabilities):
    total_dependencies = vulnerabilities.get('metadata', {}).get('dependencies',0).get('total',0)
    # Procesar obsolescencias
    per_outdated = (total_outdated / (total_dependencies)) * 100  
    # Procesar vulnerabilidades
    # Indice de severidad de vulnerabilidades: Ponderar vulnerabilidad segun su severidad, para proporcionar
    # un indice que refleja el estado de salud del proyecto
    info = vulnerabilities.get('metadata', {}).get('vulnerabilities', {}).get('info', 0)
    low = vulnerabilities.get('metadata', {}).get('vulnerabilities', {}).get('low', 0)
    moderate = vulnerabilities.get('metadata', {}).get('vulnerabilities', {}).get('moderate', 0)
    high = vulnerabilities.get('metadata', {}).get('vulnerabilities', {}).get('high', 0)
    critical = vulnerabilities.get('metadata', {}).get('vulnerabilities', {}).get('critical', 0)
    indice_severity = (critical * 5 + high * 4 + moderate * 3 + low * 2 + info * 1) / (total_dependencies if total_dependencies else 1)*100
    
    # Clasificacion severidades vulnerabilidades (porcentaje)
    vuln_critical = (critical / total_dependencies) * 100 if total_dependencies else 0
    vuln_high = (high / total_dependencies) * 100 if total_dependencies else 0      
    vuln_moderate = (moderate / total_dependencies) * 100 if total_dependencies else 0
    vuln_low = (low / total_dependencies) * 100 if total_dependencies else 0
    vuln_info = (info / total_dependencies) * 100 if total_dependencies else 0

    # Salud general de las dependencias del proyecto
    health_score = 100 - (per_outdated + vuln_critical + vuln_high + vuln_moderate + vuln_low + vuln_info)

    print("\n---------------------- Resumen de la verificación---------------------")
    print(f"-Total de dependencias obsoletas: {total_outdated}")
    print(f"-Total de vulnerabilidades: {vulnerabilities.get('metadata', {}).get('vulnerabilities', {}).get('total', 0)}")
    print(f"    -Críticas: {critical} ({vuln_critical:.2f}%)")
    print(f"    -Altas: {high} ({vuln_high:.2f}%)")
    print(f"    -Moderadas: {moderate} ({vuln_moderate:.2f}%)")
    print(f"    -Bajas: {low} ({vuln_low:.2f}%)")
    print(f"    -Info: {info} ({vuln_info:.2f}%)")
    print(f"-Total de dependencias: {total_dependencies}")

    print("\n******* Métricas de salud del proyecto: ********")
    print(f"Porcentaje de dependencias obsoletas: {per_outdated:.2f}%")
    print(f"Índice de severidad de vulnerabilidades: {indice_severity:.2f}%")
    print(f"Puntuación de salud del proyecto: {health_score:.2f}%")
    print("\n-----------------------------------------------------------------------")

    return  per_outdated, indice_severity, health_score


def generar_reporte():
    outdated, total_outdated = check_outdated()
    vulnerabilities = check_vulnerabilites()
    per_outdated, severity_index, health_score = check_health_metrics(outdated, total_outdated, vulnerabilities)
    reporte = {
        "outdated_dependencies": outdated,
        "total_outdated": total_outdated,
        "vulnerabilities": vulnerabilities,
        "obsolescence percentage": f"{per_outdated:.2f}%",
        "seveity_index": f"{severity_index:.2f}%",
        "health_score": f"{health_score:.2f}%"
    }

    with open("reporte.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=4, ensure_ascii=False)
    print("\nReporte generado en 'reporte.json'")

if __name__ == "__main__":
    generar_reporte()   
