from __future__ import unicode_literals
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wdqms','0018_auto_20181001_2308')
    ]

    sql_forward = """
    CREATE VIEW stationsbyperiod as
SELECT location as geom,invola,assimilationdate,centre,varid,wigosid,
        CASE
        WHEN isempty THEN 0 
            WHEN nr_expected = 0 AND nr_received = 0 THEN 100.0
            WHEN nr_expected = 0 AND nr_received > 0 THEN 100.0
            ELSE nr_received::numeric / nr_expected::numeric
        END AS per_received,
        CASE
        WHEN isempty THEN 0 
            WHEN nr_received = 0 THEN 0.0
            ELSE nr_used::numeric / nr_received::numeric
        END AS per_used
FROM nwpdatabyperiod
    """

    sql_backward = """
    DROP VIEW stationsbyperiod
    """

    operations = [
        migrations.RunSQL(sql_forward,sql_backward)
    ]
