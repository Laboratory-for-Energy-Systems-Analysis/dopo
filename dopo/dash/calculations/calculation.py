from dopo import*
import bw2data

def get_projects():
    projects = [project for project in bw2data.projects if get_databases(project.name) and project.name != ""]
    bw2data.projects.set_current(projects[0].name)
    return projects

def activate_project(project):
    bw2data.projects.set_current(project)

def get_databases(project=None):
    try:
        if project:
            bw2data.projects.set_current(project)
        return list(bw2data.databases)
    except:
        return []

def get_methods():
    return list(bw2data.methods)

def get_classifications_from_database(database: str, classification="ISIC"):
    data = []

    for ds in bw2data.Database(database):
        if "classifications" in ds:
            for c in ds["classifications"]:
                if classification in c[0].lower():
                    data.append(c[1].split(":")[-1])

    return sorted(list(set(data)))

def analyze(project, databases, impact_assessments, sectors, search_type):
    bw2data.projects.set_current(project)

    dopo = Dopo()

    for method in impact_assessments:
        dopo.methods.methods.append(eval(method))

    dopo.databases = []
    for database in databases:
        dopo.databases.append(database)

    if search_type == "sectors":
        dopo.add_sectors(sectors)
    else:
        dopo.find_activities_from_classification(search_type, sectors)

    dopo.analyze()

    return dopo.results

