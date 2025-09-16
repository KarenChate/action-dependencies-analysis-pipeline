import subprocess
import json

NPM_CMD = 'npm'
def count_total_dependencies(package_json_path):
    with open(package_json_path, encoding="utf-8") as f:
        data = json.load(f)
    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})
    return len(deps) + len(dev_deps)

def check_dependencies():
    #Comando 'npm outdated' para detectar depedencias obsoletas
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
        print("\n******* Dependencias obsoletas encontradas: *************** ")
        count = 0
        for dep,details in outdated_dependencies.items():
            print(f"{dep:<20}-{details['current']} -> {details['latest']}")
            count += 1
        print(f"Total de dependencias obsoletas: {count}\n")
    return outdated_dependencies

def check_vulnerabilites():
    # Comando 'npm audit' para evaluar vulnerabillidades
    audit =  subprocess.run([NPM_CMD,'audit','--json'],capture_output=True, text=True)
    if not audit.stdout:
        print("Error al verificar vulnerabilidades")    
        return
    audit_report = json.loads(audit.stdout)

    # Contar vulnerabilidades individuales por severidad
    vulnerabilities_detail = audit_report.get('vulnerabilities', {})
    level_counts = {'info': 0, 'low': 0, 'moderate': 0, 'high': 0, 'critical': 0}
    total_vulnerabilities = 0
    if vulnerabilities_detail:
        print('\n*******  Vulnerabilidades encontradas:  ***************')
        for pkg, info in vulnerabilities_detail.items():
            via = info.get('via', [])
            for v in via:
                if isinstance(v, dict):
                    severity = v.get('severity', 'N/A')
                    title = v.get('title', 'N/A')
                    print(f"{pkg:<20}-{severity} - {title}")
                    if severity in level_counts:
                        level_counts[severity] += 1
                        total_vulnerabilities += 1
        print("\n******* Resumen de vulnerabilidades individuales por severidad:********")
        for level in ['info', 'low', 'moderate', 'high', 'critical']:
            print(f"{level.capitalize()}: {level_counts[level]}")
        print(f"Total de vulnerabilidades individuales: {total_vulnerabilities}")
    else:
        print('No hay vulnerabilidades')
    return vulnerabilities_detail, level_counts

def generate_report(filename,outdated,vulnerabilities,vuln_resume):
    total_outdated = len(outdated) if outdated else 0
    resumen = {
        "Resumen_dependencias_obsoletas": total_outdated,
        "Total_vulnerabilidades": sum(vuln_resume.values()),
        "Resumen_vulnerabilidades":  vuln_resume
    }
    report = {
        **resumen,
        "outdated_dependencies": outdated,
        "vulnerabilities": vulnerabilities
    }
    with open(filename,'w',encoding='utf-8') as f:
        json.dump(report, f,indent=4,ensure_ascii=False)
    print(f"Reporte guardado: {filename}")

if __name__ == "__main__":
    outdated = check_dependencies()
    vulnerabilities,vuln_resume = check_vulnerabilites()
    generate_report("reporte.json",outdated, vulnerabilities,vuln_resume)
