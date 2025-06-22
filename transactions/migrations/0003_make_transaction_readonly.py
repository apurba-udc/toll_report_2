# Generated manually for Transaction read-only protection

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_alter_transaction_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={
                'default_permissions': (),  # No permissions at all
                'managed': False,  # Django doesn't manage this table
                'ordering': ['-capturedate'],
            },
        ),
        # This migration ensures the Transaction table remains read-only
        # and cannot be modified by any Django operation
    ] 