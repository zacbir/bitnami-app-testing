import re
import subprocess
import unittest

PERMISSIONS_PATTERN = re.compile(r'^(?P<type>\S)(?P<owner_rwx>\S\S\S)(?P<group_rwx>\S\S\S)(?P<world_rwx>\S\S\S).*$')


class BitnamiTestCase(unittest.TestCase):

    def test_fs_permissions(self):
        """
        A properly-configured WordPress installation has an owner-readable/-writeable wp-config.php file.
        """
        docker_args = 'docker-compose exec wordpress ls -l bitnami/wordpress/wp-config.php'.split()
        output = subprocess.check_output(docker_args)
        m = PERMISSIONS_PATTERN.match(output)
        self.assertEqual(m.group('owner_rwx'), 'rw-', 'Permissions for owner are incorrect')
        self.assertEqual(m.group('group_rwx'), 'r--', 'Permissions for group are incorrect')
        self.assertEqual(m.group('world_rwx'), '---', 'Permissions for world are incorrect')

