import os
import sys
import subprocess
import unittest

class SecurityTests(unittest.TestCase):
    def run_script(self, script, env_vars=None, remove_vars=None):
        env = os.environ.copy()
        env["DATABASE_URL"] = "sqlite:///./test_sec_db.sqlite"
        if env_vars:
            env.update(env_vars)
        if remove_vars:
            for k in remove_vars:
                env.pop(k, None)
            
        # Write temporary script
        with open("test_runner.py", "w") as f:
            f.write(script)
            
        # Run it
        result = subprocess.run([sys.executable, "test_runner.py"], env=env, capture_output=True, text=True)
        
        # Cleanup
        if os.path.exists("test_runner.py"):
            os.remove("test_runner.py")
            
        return result

    def setUp(self):
        if os.path.exists("test_sec_db.sqlite"):
            os.remove("test_sec_db.sqlite")

    def tearDown(self):
        if os.path.exists("test_sec_db.sqlite"):
            os.remove("test_sec_db.sqlite")

    def test_1_jwt_present(self):
        script = """
import api.auth
print(api.auth.SECRET_KEY)
"""
        res = self.run_script(script, {"JWT_SECRET_KEY": "test-secret"})
        self.assertEqual(res.returncode, 0)
        self.assertIn("test-secret", res.stdout)
        
    def test_2_jwt_missing(self):
        script = """
import api.auth
"""
        res = self.run_script(script, remove_vars=["JWT_SECRET_KEY"])
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("JWT_SECRET_KEY must be set in the environment", res.stderr)
        
    def test_3_existing_admin(self):
        # Create DB and admin first
        script_setup = """
import os
import api.database
from api.models import User
api.database.Base.metadata.create_all(bind=api.database.engine)
db = api.database.SessionLocal()
existing_admin = User(username="existing_admin", hashed_password="old_hash", role="admin")
db.add(existing_admin)
db.commit()
db.close()
"""
        self.run_script(script_setup, {"JWT_SECRET_KEY": "dummy"})
        
        # Now run init_database
        script_test = """
import os
import api.database
from api.models import User
api.database.init_database()
db = api.database.SessionLocal()
admins = db.query(User).filter(User.role == 'admin').all()
assert len(admins) == 1
assert admins[0].username == 'existing_admin'
assert admins[0].hashed_password == 'old_hash'
print("SUCCESS")
"""
        res = self.run_script(script_test, {
            "JWT_SECRET_KEY": "dummy",
            "ADMIN_USERNAME": "new_admin",
            "ADMIN_PASSWORD": "new_password"
        })
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("SUCCESS", res.stdout)

    def test_4_no_admin_with_credentials(self):
        script = """
import os
import api.database
from api.models import User
api.database.init_database()
db = api.database.SessionLocal()
admins = db.query(User).filter(User.role == 'admin').all()
assert len(admins) == 1
assert admins[0].username == 'test_admin'
print("SUCCESS")
"""
        res = self.run_script(script, {
            "JWT_SECRET_KEY": "dummy",
            "ADMIN_USERNAME": "test_admin",
            "ADMIN_PASSWORD": "test_password"
        })
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("SUCCESS", res.stdout)
        
    def test_5_no_admin_missing_credentials(self):
        script = """
import os
import api.database
api.database.init_database()
"""
        res = self.run_script(script, env_vars={"JWT_SECRET_KEY": "dummy"}, remove_vars=["ADMIN_PASSWORD"])
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("ADMIN_PASSWORD must be set", res.stderr)
        
    def test_6_admin_password_verified(self):
        script = """
import os
import api.database
from api.models import User
from api.auth import verify_password
api.database.init_database()
db = api.database.SessionLocal()
admin = db.query(User).filter(User.role == 'admin').first()
assert verify_password('test_pass2', admin.hashed_password)
assert not verify_password('wrong_pass', admin.hashed_password)
print("SUCCESS")
"""
        res = self.run_script(script, {
            "JWT_SECRET_KEY": "dummy",
            "ADMIN_USERNAME": "test_admin2",
            "ADMIN_PASSWORD": "test_pass2"
        })
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("SUCCESS", res.stdout)
        
    def test_7_no_plaintext_password_logged(self):
        script = """
import os
import api.database
api.database.init_database()
"""
        res = self.run_script(script, {
            "JWT_SECRET_KEY": "dummy",
            "ADMIN_USERNAME": "test_admin3",
            "ADMIN_PASSWORD": "secret_password_123"
        })
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertNotIn("secret_password_123", res.stdout)
        self.assertNotIn("secret_password_123", res.stderr)
        self.assertIn("test_admin3", res.stdout)

if __name__ == '__main__':
    unittest.main()
