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


def analyze(project, databases, impact_assessments, sectors):
    bw2data.projects.set_current(project)

    dopo = Dopo()

    for method in impact_assessments:
        dopo.methods.methods.append(eval(method))

    dopo.databases = []
    for database in databases:
        dopo.databases.append(database)

    dopo.add_sectors(sectors)

    dopo.analyze()

    return dopo.results

