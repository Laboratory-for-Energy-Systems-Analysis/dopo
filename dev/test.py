from dopo import*
import bw2data

bw2data.projects.set_current("bw25")

dopo = Dopo()

dopo.methods.methods.append(('IPCC 2021', 'climate change', 'global warming potential (GWP100)'))
dopo.methods.methods.append(('EN15804', 'inventory indicators ISO21930', 'use of net fresh water'))

dopo.databases = ["ecoinvent-3.10-cutoff",]

dopo.add_sectors(["steel"])


dopo.analyze()

key = list(dopo.results.keys())[0]

#dopo.results[key].to_excel('lca_scores.xlsx')
