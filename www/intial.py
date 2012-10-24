import csv

from recordings.models import Organisation, Site, Recorder, Deployment

DIR = 'fixtures'
organisation = csv.DictReader(open(os.path.join(DIR, 'Organisations.csv')))

for row in organisation:
    o = Organisation(code=row['Code'], name=row['Name'])
    o.save()



