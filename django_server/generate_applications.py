import os
import django
import random

os.environ["DJANGO_SETTINGS_MODULE"] = 'application_evaluator_config.settings'
django.setup()

from application_evaluator import models


parts = [
    ['HighClimate', 'NeuralShift', 'PlanetClimate', 'CannaClimate', 'Neuromic', 'Habiotic', 'Knomic', 'Mneural',
     'Msology', 'Dynamical', 'Hebbiant', 'Climatory', 'GeoFuse', 'CClimate', 'VNeural', 'NeurAct', 'Forealth',
     'Biomical', 'Degrowthly', 'Spational', 'Becological', 'ClimateBoost', 'Metaclimate', 'Neurozil', 'Gognitive',
     'M-Climate', 'Synamic', 'Climation', 'EClimate', 'EcoBlast', 'AInlytic', 'Neuropic', 'Skedaptic', 'Buxnetic',
     'Neural Future', 'NeuralStep', 'Climators', 'Adaptics', 'Vogenetic', 'Biotion', 'Adaptical', 'Abnorecast',
     'Climatomic', 'Climatch', 'Psygenic', 'Biotional', 'NeuroFlux', 'Voxicity', 'Impactive', 'Neurophic',
     'Adjustmental', 'Citygenic'],
    ['B2B', 'B2C', 'back-end', 'best-of-breed', 'bleeding-edge', 'bricks-and-clicks', 'clicks-and-mortar', 'collaborative', 'compelling', 'cross-platform', 'cross-media', 'customized', 'cutting-edge', 'distributed', 'dot-com', 'dynamic', 'e-business', 'efficient', 'end-to-end', 'enterprise', 'extensible', 'frictionless', 'front-end', 'global', 'granular', 'holistic', 'impactful', 'innovative', 'integrated', 'interactive', 'intuitive', 'killer', 'leading-edge', 'magnetic', 'mission-critical', 'next-generation', 'one-to-one', 'open-source', 'out-of-the-box', 'plug-and-play', 'proactive', 'real-time', 'revolutionary', 'rich', 'robust', 'scalable', 'seamless', 'sexy', 'sticky', 'strategic', 'synergistic', 'transparent', 'turn-key', 'ubiquitous', 'user-centric', 'value-added', 'vertical', 'viral', 'virtual', 'visionary', 'web-enabled', 'wireless', 'world-class'],
    ['tramway', 'cycling', 'mobility service', 'urban', 'carbon-reducing', 'construction', 'traffic', 'energy', 'recycling', 'upcycling', 'light rail', 'e-mobility', 'smart city', 'service-oriented', 'city planning', 'e-citizen', 'neural', 'machine learning', 'AI', 'deep learning', 'adaptive', 'self-correcting', 'robotic', 'collaboratively trained'],
    ['action-items', 'applications', 'architectures', 'bandwidth', 'channels', 'communities', 'content', 'convergence', 'deliverables', 'e-business', 'e-commerce', 'e-markets', 'e-services', 'e-tailers', 'experiences', 'eyeballs', 'functionalities', 'infomediaries', 'infrastructures', 'initiatives', 'interfaces', 'markets', 'methodologies', 'metrics', 'mindshare', 'models', 'networks', 'niches', 'paradigms', 'partnerships', 'platforms', 'portals', 'relationships', 'ROI', 'synergies', 'web-readiness', 'schemas', 'solutions', 'supply-chains', 'systems', 'technologies', 'users', 'vortals', 'web services']
]

pick = lambda lst: lst[random.randrange(0, len(lst))]

round = models.ApplicationRound.objects.first()
organization = models.Organization.objects.get(name='Helsinki')
for part in parts[0]:
    app = round.applications.create(
        name=f'{part}: {pick(parts[1]).capitalize()} {pick(parts[2])} {pick(parts[3])}'
    )
    app.evaluating_organizations.add(organization)
